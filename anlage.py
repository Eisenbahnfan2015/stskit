import collections
import itertools
import os
import re
from collections.abc import Set
import json
import logging
from pathlib import Path
from typing import Any, Dict, Generator, Iterable, List, Mapping, Optional, Set, Tuple, Union

import networkx as nx
import numpy as np
import trio

from stsobj import AnlagenInfo, BahnsteigInfo, Knoten, ZugDetails, FahrplanZeile, time_to_seconds
from stsplugin import PluginClient, TaskDone


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class JSONEncoder(json.JSONEncoder):
    """
    translate non-standard objects to JSON objects.

    currently implemented: Set.

    ~~~~~~{.py}
    encoded = json.dumps(data, cls=JSONEncoder)
    decoded = json.loads(encoded, object_hook=json_object_hook)
    ~~~~~~
    """

    def default(self, obj):
        if isinstance(obj, Set):
            return dict(__class__='Set', data=list(obj))
        if isinstance(obj, frozenset):
            return dict(__class__='frozenset', data=list(obj))
        if isinstance(obj, nx.Graph):
            return "networkx.Graph"
        else:
            return super().default(obj)


def json_object_hook(d):
    if '__class__' in d and d['__class__'] == 'Set':
        return set(d['data'])
    else:
        return d


def common_prefix(lst: Iterable) -> Generator[str, None, None]:
    for s in zip(*lst):
        if len(set(s)) == 1:
            yield s[0]
        else:
            return


def gemeinsamer_name(g: Iterable) -> str:
    return ''.join(common_prefix(g)).strip()


ALPHA_PREFIX_PATTERN = re.compile(r'[^\d\W]*')
NON_DIGIT_PREFIX_PATTERN = re.compile(r'\D*')


def alpha_prefix(name: str) -> str:
    """
    alphabetischen anfang eines namens extrahieren.

    anfang des namens bis zum ersten nicht-alphabetischen zeichen (ziffer, leerzeichen, sonderzeichen).
    umlaute etc. werden als alphabetisch betrachtet.
    leerer string, wenn keine alphabetischen zeichen gefunden wurden.

    :param name: z.b. gleisname
    :return: resultat

    """
    return re.match(ALPHA_PREFIX_PATTERN, name).group(0)


def default_bahnhofname(gleis: str) -> str:
    """
    bahnhofnamen aus gleisnamen ableiten.

    es wird angenommen, dass der bahnhofname aus den alphabetischen zeichen am anfang des gleisnamens besteht.
    wenn der gleisname keine alphabetischen zeichen enthält, wird per default "HBf" zurückgegeben.

    :param gleis: gleis- bzw. bahnsteigname
    :return: bahnhofname
    """

    name = alpha_prefix(gleis)
    if name:
        return name
    else:
        return "HBf"


def default_anschlussname(gleis: str) -> str:
    """
    anschlussname aus gleisnamen ableiten.

    es wird angenommen, dass der bahnhofname aus den alphabetischen zeichen am anfang des gleisnamens besteht.
    wenn der gleisname keine alphabetischen zeichen enthält, wird ein leerer string zurückgegeben.

    :param gleis: gleisname
    :return: anschlussname
    """

    return re.match(ALPHA_PREFIX_PATTERN, gleis).group(0).strip()


def dict_union(*gr: Dict[str, Set[Any]]) -> Dict[str, Set[Any]]:
    """
    merge dictionaries of sets.

    the given dictionaries are merged.
    if two dictionaries contain the same key, the union of their values is stored.

    :param gr: any number of dictionaries containing sets as values
    :return: merged dictionary
    """
    d = dict()
    for g in gr:
        for k, v in g.items():
            if k in d:
                d[k] = d[k].union(v)
            else:
                d[k] = v
    return d


def find_set_item_in_dict(item: Any, mapping: Mapping[Any, Set[Any]]) -> Any:
    """
    look up a set member in a key->set mapping.

    :param item: item to find in one of the sets in the dictonary.
    :param mapping: mapping->set
    :return: key
    :raise ValueError if not found
    """
    for k, s in mapping.items():
        if item in s:
            return k
    else:
        raise ValueError(f"item {item} not found in dictionary.")


anschluss_name_funktionen = {}
    # "Bern - Lötschberg": alpha_prefix,
    # "Ostschweiz": alpha_prefix,
    # "Tessin": alpha_prefix,
    # "Westschweiz": alpha_prefix,
    # "Zentralschweiz": alpha_prefix,
    # "Zürich und Umgebung": alpha_prefix}

bahnhof_name_funktionen = {}


class Anlage:
    """
    netzwerk-darstellungen der bahnanlage

    diese klasse verwaltet folgende graphen als darstellung der bahnanlage:

    :var self.signal_graph original "wege"-graph vom simulator
        mit bahnsteigen, haltepunkten, signalen, einfahrten und ausfahrten.
        dieser graph dient als basis und wird nicht speziell bearbeitet.
        der graph ist ungerichtet, weil die richtung vom simulator nicht konsistent angegeben wird:
        entgegengesetzte signale sind verbunden, einfahrten sind mit ausfahrsignalen verbunden.

    :var self.bahnsteig_graph graph mit den bahnsteigen von der "bahnsteigliste".
        vom simulator als nachbarn bezeichnete bahnsteige sind durch kanten verbunden.
        der bahnsteig-graph zerfällt dadurch in bahnhof-teile.
        es ist für den gebrauch in den charts in einigen fällen wünschbar,
        dass bahnhof-teile zu einem ganzen bahnhof zusammengefasst werden,
        z.b. bahnsteige und abstellgleise.
        die zuordnung kann jedoch nicht aus dem graphen selber abgelesen werden
        und muss separat (user, konfiguration, empirische auswertung) gemacht werden.

        vorsicht: bahnsteige aus der bahnsteigliste sind teilweise im wege-graph nicht enthalten!

    :var self.bahnhof_graph netz-graph mit bahnsteiggruppen, einfahrtgruppen und ausfahrtgruppen.
        vom bahnsteig-graph abgeleiteter graph, der die ganzen zugeordneten gruppen enthält.


    :var self.anschlussgruppen gruppierung von einfahrten und ausfahrten

        mehrere ein- und ausfahrten können zu einer gruppe zusammengefasst werden.
        dieser dictionary bildet gruppennamen auf sets von knotennamen ab.

    :var self.bahnsteiggruppen gruppierung von bahnsteigen

        mehrere bahnsteige (typischerweise alle zu einem bahnhof gehörigen)
        können zu einer gruppe zusammengefasst werden.
        dieser dictionary bildet gruppennamen (bahnhofnamen) auf sets von bahnsteignamen ab.
    """

    BAHNHOF_GRAPH_INIT_ATTR = {
        "fahrzeit_sum": 0,
        "fahrzeit_min": np.nan,
        "fahrzeit_max": np.nan,
        "fahrzeit_count": 0
    }

    def __init__(self, anlage: AnlagenInfo):
        self.anlage = anlage
        self.config_loaded = False
        self.auto = True

        self.f_anschlussname = default_anschlussname
        self.f_bahnhofname = default_bahnhofname

        # gruppenname -> {gleisnamen}
        self.anschlussgruppen: Dict[str, Set[str]] = {}
        self.bahnsteiggruppen: Dict[str, Set[str]] = {}
        self.gleisgruppen: Dict[str, Set[str]] = {}

        # gleisname -> gruppenname
        self.anschlusszuordnung: Dict[str, str] = {}
        self.bahnsteigzuordnung: Dict[str, str] = {}
        self.gleiszuordnung: Dict[str, str] = {}

        # lage des anschlusses auf dem gleisbild
        # gruppenname -> "links", "mitte", "rechts", "oben", "unten"
        self.anschlusslage: Dict[str, str] = {}

        self.signal_graph: nx.Graph = nx.DiGraph()
        self.bahnsteig_graph: nx.Graph = nx.DiGraph()
        self.bahnhof_graph: nx.Graph = nx.Graph()

        # strecken-name -> gruppen-namen
        self.strecken: Dict[str, Tuple[str]] = {}

        self._verbindungsstrecke_cache: Dict[Tuple[str, str], List[str]] = {}

    def update(self, client: PluginClient, config_path: os.PathLike):
        if not self.anlage:
            self.anlage = client.anlageninfo

            try:
                self.f_anschlussname = anschluss_name_funktionen[self.anlage.region]
            except KeyError:
                pass
            try:
                self.f_bahnhofname = bahnhof_name_funktionen[self.anlage.region]
            except KeyError:
                pass

        if len(self.signal_graph) == 0:
            self.original_graphen_erstellen(client)
            self.gleise_gruppieren()

        if not self.config_loaded:
            try:
                self.load_config(config_path)
            except OSError:
                logger.exception("fehler beim laden der anlagenkonfiguration")
            except ValueError as e:
                logger.exception("fehlerhafte anlagenkonfiguration")
            self.config_loaded = True

        if len(self.bahnhof_graph) == 0:
            self.bahnhof_graph_erstellen()

        if len(self.strecken) == 0:
            self.strecken_aus_signalgraph()

        self.bahnhof_graph_zugupdate(client.zugliste.values())

    def original_graphen_erstellen(self, client: PluginClient):
        """
        erstellt die signal- und bahnsteig-graphen nach anlageninformationen vom simulator.

        der signal-graph enthält alle signale, bahnsteige, einfahrten, ausfahrten und haltepunkte aus der wege-liste
        der plugin-schnittstelle als knoten.
        das 'typ'-attribut wird auf den sts-knotentyp (int) gesetzt.
        kanten werden entsprechend der nachbarn-relationen aus der wegeliste ('typ'-attribut 'gleis') gesetzt.
        der graph ist gerichtet, da die nachbarbeziehung nicht reziprok ist.
        die kante zeigt auf die knoten, die als nachbarn aufgeführt sind.
        der graph wird in self.signal_graph abgelegt.
        dieser graph sollte nicht verändert werden.

        der bahnsteig-graph enthält alle bahnsteige aus der bahnsteigliste der plugin-schnittstelle als knoten.
        kanten werden entsprechend der nachbar-relationen gesetzt.
        der graph ist gerichtet, da die nachbarbeziehung nicht reziprok ist.
        die kante zeigt auf die knoten, die als nachbarn aufgeführt sind.

        signal-attribute
        ----------------
        knoten 'typ': (int) stsobj.Knoten.TYP_NUMMER
        kanten 'typ': (str) 'gleis'
        kanten 'distanz': (int) länge (anzahl knoten) des kürzesten pfades zwischen den knoten. wird auf 1 gesetzt.

        bahnsteig-attribute
        -------------------
        kanten 'typ': (str) 'bahnhof', wenn die bahnsteignamen mit der gleichen buchstabenfolge
                      (oder direkt mit der gleisnummer) beginnen und damit zum gleichen bahnhof gehören,
                      sonst 'nachbar'.
        kanten 'distanz': (int) länge (anzahl knoten) des kürzesten pfades zwischen den knoten. wird auf 0 gesetzt.

        :param client: PluginClient-artiges objekt mit aktuellen bahnsteigliste und wege attributen.
        :return: None.
        """
        knoten_auswahl = {Knoten.TYP_NUMMER["Signal"],
                          Knoten.TYP_NUMMER["Bahnsteig"],
                          Knoten.TYP_NUMMER["Einfahrt"],
                          Knoten.TYP_NUMMER["Ausfahrt"],
                          Knoten.TYP_NUMMER["Haltepunkt"]}

        self.signal_graph.clear()
        for knoten1 in client.wege.values():
            if knoten1.name and knoten1.typ in knoten_auswahl:
                self.signal_graph.add_node(knoten1.name, typ=knoten1.typ)
                for knoten2 in knoten1.nachbarn:
                    if knoten2.name and knoten2.typ in knoten_auswahl:
                        self.signal_graph.add_edge(knoten1.name, knoten2.name, typ='gleis', distanz=1)

        for bs1 in client.bahnsteigliste.values():
            self.bahnsteig_graph.add_node(bs1.name)
            pre1 = alpha_prefix(bs1.name)
            for bs2 in bs1.nachbarn:
                pre2 = alpha_prefix(bs2.name)
                if pre1 == pre2:
                    self.bahnsteig_graph.add_edge(bs1.name, bs2.name, typ='bahnhof', distanz=0)
                else:
                    self.bahnsteig_graph.add_edge(bs1.name, bs2.name, typ='nachbar', distanz=0)

        self._verbindungsstrecke_cache = {}

    def gleise_gruppieren(self):
        """
        gruppiert bahnsteige zu bahnhöfen und ein-/ausfahrten zu anschlüssen.

        bahnsteige werden nach nachbarn gemäss anlageninfo gruppiert.
        der gruppenname wird aus gemäss der regionsabhängigen f_bahnhofname-funktion gebildet
        (per default die alphabetischen zeichen bis zum ersten nicht-alphabetischen zeichen).
        falls dieses verfahren jedoch zu mehrdeutigen bezeichnungen führen würde,
        wird der alphabetisch erste gleisnamen übernommen.

        einfahrten und ausfahrten werden nach dem namen gruppiert,
        der durch die regionsabhängige f_anschlussname gebildet wird.
        falls ein anschlussname mit einem bahnhofsnamen kollidiert, wird ein pluszeichen nachgestellt.

        da es keine allgemeine konvention für gleis- und anschlussnamen gibt,
        kann der algorithmus abhängig vom stellwerk zu viele oder zu wenige gleise zusammenfassen.
        in diesen fällen muss die zuordnung in der konfigurationsdatei manuell korrigiert werden.

        :return: None
        """
        anschlusstypen = {Knoten.TYP_NUMMER["Einfahrt"], Knoten.TYP_NUMMER["Ausfahrt"]}
        bahnsteigtypen = {Knoten.TYP_NUMMER["Bahnsteig"], Knoten.TYP_NUMMER["Haltepunkt"]}

        def filter_node(n1):
            try:
                return self.signal_graph.nodes[n1]["typ"] in bahnsteigtypen
            except KeyError:
                return False

        def filter_edge(n1, n2):
            try:
                return self.bahnsteig_graph[n1][n2]["typ"] == "bahnhof"
            except KeyError:
                return False

        # durch nachbarbeziehung verbundene bahnsteige bilden einen bahnhof
        subgraph = nx.subgraph_view(self.bahnsteig_graph, filter_node=filter_node, filter_edge=filter_edge)
        subgraph = subgraph.to_undirected()
        gruppen = {sorted(g)[0]: g for g in nx.connected_components(subgraph)}
        # gleisbezeichnung abtrennen
        nice_names = {k: self.f_bahnhofname(k) for k in gruppen}
        # mehrdeutige bahnhofsnamen identifizieren und durch gleichbezeichnung ersetzen
        counts_nice = collections.Counter(nice_names.values())
        counts_safe = {sn: counts_nice[nice_names[sn]] for sn in gruppen.keys()}
        self.bahnsteiggruppen = {nice_names[sn] if counts_safe[sn] == 1 else sn: g for sn, g in gruppen.items()}

        # ein- und ausfahrten, die auf den gleichen anschlussnamen abbilden, bilden einen anschluss
        nodes = [n for n, t in self.signal_graph.nodes(data='typ') if t in anschlusstypen]
        nice_names = {k: self.f_anschlussname(k) for k in nodes}
        # anschlüsse, die den gleichen namen wie ein bahnhof haben, umbenennen
        nice_names = {k: v if v not in self.bahnsteiggruppen else v + "+" for k, v in nice_names.items()}
        unique_names = set(nice_names.values())
        self.anschlussgruppen = {k: set([n for n in nodes if self.f_anschlussname(n) == k]) for k in unique_names}

        self.auto = True
        self._update_gruppen_dict()

    def _update_gruppen_dict(self):
        """
        gruppen-dictionaries aktualisieren.

        die ursprungsdaten stehen in den bahnsteiggruppen- und anschlussgruppen-dictionaries.
        von ihnen werden die zuordnungen, gleisgruppen und gleiszuordnung abgeleitet.

        :return: None
        """

        self.anschlusszuordnung = {}
        for name, gruppe in self.anschlussgruppen.items():
            for gleis in gruppe:
                self.anschlusszuordnung[gleis] = name

        self.bahnsteigzuordnung = {}
        for name, gruppe in self.bahnsteiggruppen.items():
            for gleis in gruppe:
                self.bahnsteigzuordnung[gleis] = name

        self.gleisgruppen = dict_union(self.bahnsteiggruppen, self.anschlussgruppen)
        self.gleiszuordnung = {**self.bahnsteigzuordnung, **self.anschlusszuordnung}

        self._verbindungsstrecke_cache = {}

    def bahnhof_graph_erstellen(self):
        """
        bahnhofgraph aus signalgraph und gruppenkonfiguration neu erstellen.

        der bahnhofgraph wird aus den kürzesten verbindungsstrecken aller möglichen kombinationen von ein- und
        ausfahrten gebildet. er enthält die von ihnen berührten bahnhöfe und anschlüsse als knoten.

        die self.anschlussgruppen und self.bahnsteiggruppen müssen bereits konfiguriert sein.

        :return: kein
        """
        self.bahnhof_graph.clear()

        endpunkte = [list(gruppe)[0] for gruppe in self.gleisgruppen.values() if len(gruppe) > 0]

        for ein, aus in itertools.combinations(endpunkte, 2):
            strecke = self.verbindungsstrecke(ein, aus)
            if len(strecke):
                start = None
                for ziel in strecke:
                    if ziel in self.bahnsteiggruppen:
                        self.bahnhof_graph.add_node(ziel, typ="bahnhof")
                    else:
                        self.bahnhof_graph.add_node(ziel, typ="anschluss")
                    if start is not None:
                        self.bahnhof_graph.add_edge(start, ziel, **Anlage.BAHNHOF_GRAPH_INIT_ATTR)
                    start = ziel

    def bahnhof_graph_zugupdate(self, zugliste: Iterable[ZugDetails]):
        """
        bahnhof-graph aus fahrplan aktualisieren.

        der bahnhofgraph wird von der bahnhof_graph_erstellen-methode erstellt.
        diese methode aktualisiert die fahrzeiten-attribute der kanten anhand des fahrplans.
        fahrzeit_sum, fahrzeit_min, fahrzeit_max und fahrzeit_count werden aktualisiert.
        die fahrzeiten sind in sekunden.
        fahrzeit_count ist die anzahl betrachteter zugverbindungen.

        :return: kein
        """

        for zug in zugliste:
            start = None
            startzeit = 0
            for zeile in zug.fahrplan:
                try:
                    ziel = self.gleiszuordnung[zeile.plan]
                    zielzeit = time_to_seconds(zeile.an)
                except (AttributeError, KeyError):
                    break

                if start and start != ziel:
                    zeit = zielzeit - startzeit
                    try:
                        d = self.bahnhof_graph[start][ziel]
                    except KeyError:
                        self.bahnhof_graph.add_edge(start, ziel, **Anlage.BAHNHOF_GRAPH_INIT_ATTR)
                        d = self.bahnhof_graph[start][ziel]

                    d['fahrzeit_sum'] = d['fahrzeit_sum'] + zeit
                    d['fahrzeit_min'] = min(d['fahrzeit_min'], zeit) if not np.isnan(d['fahrzeit_min']) else zeit
                    d['fahrzeit_max'] = max(d['fahrzeit_max'], zeit) if not np.isnan(d['fahrzeit_max']) else zeit
                    d['fahrzeit_count'] = d['fahrzeit_count'] + 1

                start = ziel
                try:
                    startzeit = time_to_seconds(zeile.ab)
                except AttributeError:
                    break

    def generalisieren(self, metrik):
        graph = self.bahnhof_graph

        edges_to_remove = set([])
        for u, nbrs in graph.adj.items():
            ns = set(nbrs) - {u}
            for v, w in itertools.combinations(ns, 2):
                try:
                    luv = graph[u][v][metrik]
                    lvw = graph[v][w][metrik]
                    luw = graph[u][w][metrik]
                    if luv < lvw and luw < lvw:
                        edges_to_remove.add((v, w))
                        logger.debug(f"remove {v}-{w} from triangle ({u},{v},{w}) distance ({lvw},{luw},{luv})")
                except KeyError:
                    pass

        graph.remove_edges_from(edges_to_remove)

    def strecken_aus_signalgraph(self):
        """
        strecken aus signalgraph ableiten

        diese funktion bestimmt die kürzesten pfade zwischen allen anschlüssen und bahnsteigen
        und listet die an diesen pfaden liegenden bahnhöfe auf.
        der kürzeste pfad im signalgraph besteht meist nur aus signalen.
        bahnsteige erscheinen als nachbarn eines oder mehrerer signale auf dem pfad.

        eine strecke besteht aus einer liste von bahnhöfen plus einfahrt am anfang und ausfahrt am ende.
        die namen der elemente sind gruppennamen, d.h. die schlüssel aus self.gleisgruppen.
        der streckenname (schlüssel von self.strecken) wird aus dem ersten und letzten wegpunkt gebildet,
        die mit einem bindestrich aneinandergefügt werden.

        :return: das result wird in self.strecken abgelegt.
        """
        anschlussgleise = [list(gruppe)[0] for gruppe in self.anschlussgruppen.values() if len(gruppe) > 0]
        strecken = []
        for ein, aus in itertools.combinations(anschlussgleise, 2):
            strecke = self.verbindungsstrecke(ein, aus)
            if len(strecke) >= 1:
                strecken.append(strecke)

        self.strecken = {f"{s[0]}-{s[-1]}": s for s in strecken}

    def verbindungsstrecke(self, start_gleis: str, ziel_gleis: str) -> List[str]:
        """
        kürzeste verbindung zwischen zwei gleisen bestimmen

        die kürzeste verbindung wird aus dem signalgraphen bestimmt.
        start und ziel müssen knoten im signalgraphen sein,
        also gleisbezeichnungen (einfahrten, ausfahrten, bahnsteige, haltepunkte), die im fahrplan vorkommen.

        die berechnete strecke ist eine geordnete liste von gruppennamen (bahnhöfe bzw. anschlussgruppen).

        da die streckenberechnung aufwändig sein kann, werden die resultate im self._verbindungsstrecke_cache
        gespeichert. der cache muss gelöscht werden, wenn sich der signalgraph oder die bahnsteigzuordnung ändert.

        :param start_gleis: gleis- oder einfahrtsbezeichnung
        :param ziel_gleis: gleis- oder ausfahrtsbezeichnung
        :return: liste von befahrenen gleisgruppen vom start zum ziel.
            die liste kann leer sein, wenn kein pfad gefunden wurde!
        """

        try:
            return self._verbindungsstrecke_cache[(start_gleis, ziel_gleis)]
        except KeyError:
            pass

        try:
            pfad = nx.shortest_path(self.signal_graph, start_gleis, ziel_gleis)
        except nx.NetworkXException:
            wegpunkte = []
        else:
            nachbar_haltepunkte = [[hp for hp in self.signal_graph.neighbors(n)
                                    if self.signal_graph.nodes[hp]['typ'] in {5, 12}]
                                   for n in pfad]
            wegpunkte = [hp[0] for hp in nachbar_haltepunkte if hp]
            wegpunkte.insert(0, start_gleis)
            wegpunkte.append(ziel_gleis)

        strecke = []
        for hp in wegpunkte:
            try:
                bf = self.gleiszuordnung[hp]
            except KeyError:
                pass
            else:
                if bf not in strecke:
                    strecke.append(bf)

        self._verbindungsstrecke_cache[(start_gleis, ziel_gleis)] = strecke
        return strecke

    def get_strecken_distanzen(self, strecke: List[str]) -> Dict[str, float]:
        """

        :param strecke: liste von gleisgruppen-namen
        :return: distanz = minimale fahrzeit in sekunden
        """
        kanten = zip(strecke[:-1], strecke[1:])
        distanz = 0.
        result = {strecke[0]: distanz}
        for u, v in kanten:
            try:
                zeit = self.bahnhof_graph[u][v]['fahrzeit_min']
                if not np.isnan(zeit):
                    distanz += zeit
                else:
                    distanz += 60.
            except KeyError:
                logger.warning(f"verbindung {u}-{v} nicht im netzplan.")
                distanz += 60.

            result[v] = float(distanz)

        return result

    def load_config(self, path: os.PathLike, load_graphs=False, ignore_version=False):
        """

        :param path: verzeichnis mit den konfigurationsdaten.
            der dateiname wird aus der anlagen-id gebildet.
        :param load_graphs: die graphen werden normalerweise vom simulator abgefragt und erstellt.
            für offline-auswertung können sie auch aus dem konfigurationsfile geladen werden.
        :return: None
        :raise: OSError, JSONDecodeError(ValueError)
        """
        if load_graphs:
            p = Path(path) / f"{self.anlage.aid}diag.json"
        else:
            p = Path(path) / f"{self.anlage.aid}.json"

        with open(p) as fp:
            d = json.load(fp, object_hook=json_object_hook)

        if not ignore_version:
            assert d['_aid'] == self.anlage.aid
            if self.anlage.build != d['_build']:
                logger.warning(f"unterschiedliche build-nummern (file: {d['_build']}, sim: {self.anlage.build})")

            if '_version' not in d:
                d['_version'] = 1
                logger.warning(f"konfigurationsdatei ohne versionsangabe. nehme 1 an.")
            if d['_version'] < 2:
                logger.error(f"inkompatible konfigurationsdatei - auto-konfiguration")
                return

        try:
            self.bahnsteiggruppen = d['bahnsteiggruppen']
            self.auto = False
        except KeyError:
            logger.info("fehlende bahnsteiggruppen-konfiguration - auto-konfiguration")
        try:
            self.anschlussgruppen = d['anschlussgruppen']
        except KeyError:
            logger.info("fehlende anschlussgruppen-konfiguration - auto-konfiguration")
        try:
            self.anschlusslage = d['anschlusslage']
        except KeyError:
            self.anschlusslage = {k: "mitte" for k in self.anschlussgruppen.keys()}

        try:
            self.strecken = d['strecken']
        except KeyError:
            logger.info("fehlende streckenkonfiguration")

        self._update_gruppen_dict()
        self.config_loaded = True

        if load_graphs:
            try:
                self.signal_graph = nx.node_link_graph(d['signal_graph'])
            except KeyError:
                pass
            try:
                self.bahnsteig_graph = nx.node_link_graph(d['bahnsteig_graph'])
            except KeyError:
                pass
            try:
                self.bahnhof_graph = nx.node_link_graph(d['bahnhof_graph'])
            except KeyError:
                pass

    def save_config(self, path: os.PathLike):
        d = self.get_config(graphs=False)
        p = Path(path) / f"{self.anlage.aid}.json"
        with open(p, "w") as fp:
            json.dump(d, fp, sort_keys=True, indent=4, cls=JSONEncoder)

        if logger.isEnabledFor(logging.DEBUG):
            d = self.get_config(graphs=True)
            p = Path(path) / f"{self.anlage.aid}diag.json"
            with open(p, "w") as fp:
                json.dump(d, fp, sort_keys=True, indent=4, cls=JSONEncoder)

    def get_config(self, graphs=False) -> Dict:
        """
        aktuelle konfiguration im dict-format auslesen

        das dictionary kann dann im json-format abgespeichert und als konfigurationsdatei verwendet werden.

        :param graphs: gibt an, ob die graphen (im networkx node-link format mitgeliefert werden sollen.
        :return: dictionary mit konfiguration- und diagnostik-daten.
        """

        d = {'_aid': self.anlage.aid,
             '_region': self.anlage.region,
             '_name': self.anlage.name,
             '_build': self.anlage.build,
             '_version': 2,
             'bahnsteiggruppen': self.bahnsteiggruppen,
             'anschlussgruppen': self.anschlussgruppen,
             'anschlusslage': self.anschlusslage,
             'strecken': self.strecken}

        if graphs:
            if self.signal_graph:
                d['signal_graph'] = dict(nx.node_link_data(self.signal_graph))
            if self.bahnsteig_graph:
                d['bahnsteig_graph'] = dict(nx.node_link_data(self.bahnsteig_graph))
            if self.bahnhof_graph:
                d['bahnhof_graph'] = dict(nx.node_link_data(self.bahnhof_graph))

        return d


async def main():
    """
    anlagenkonfiguration ausgeben

    diese funktion dient der inspektion der anlage.
    die anlage inkl. wege, bahnsteige und zuege wird vom sim abgefragt und automatisch konfiguriert.
    die konfiguration wird dann im json-format an stdout ausgegeben.

    :return: None
    """
    client = PluginClient(name='anlageinfo', autor='tester', version='0.0', text='anlagekonfiguration auslesen')
    await client.connect()

    try:
        async with client._stream:
            async with trio.open_nursery() as nursery:
                await nursery.start(client.receiver)
                await client.register()
                await client.request_simzeit()
                await client.request_anlageninfo()
                await client.request_bahnsteigliste()
                await client.request_wege()
                await client.request_zugliste()
                await client.request_zugdetails()
                await client.request_zugfahrplan()
                await client.resolve_zugflags()
                client.update_bahnsteig_zuege()
                client.update_wege_zuege()

                anlage = Anlage(client.anlageninfo)
                anlage.update(client, "")
                d = anlage.get_config(graphs=True)
                s = json.dumps(d, sort_keys=True, indent=4, cls=JSONEncoder)
                print(s)
                raise TaskDone()
    except TaskDone:
        pass

if __name__ == "__main__":
    trio.run(main)
