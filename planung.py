import datetime
import logging
import numpy as np
from typing import Any, Callable, Dict, Iterable, List, Mapping, Optional, Set, Tuple, Union

from stsobj import ZugDetails, FahrplanZeile, Ereignis
from stsobj import time_to_minutes, time_to_seconds, minutes_to_time, seconds_to_time
from auswertung import Auswertung


logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class VerspaetungsKorrektur:
    """
    basisklasse für die anpassung der verspätungszeit eines fahrplanziels

    eine VerspaetungsKorrektur-klasse besteht im wesentlichen aus der anwenden-methode.
    diese berechnet für das gegebene ziel die abfahrtsverspätung aus der ankunftsverspätung
    und ggf. weiteren ziel- bzw. zugdaten.

    über das _planung-attribut hat die klasse zugriff auf die ganze zugliste.
    sie darf jedoch nur das angegebene ziel sowie allfällige verknüpfte züge direkt ändern.
    """
    def __init__(self, planung: 'Planung'):
        super().__init__()
        self._planung = planung

    def anwenden(self, zug: 'ZugDetailsPlanung', ziel: 'ZugZielPlanung'):
        pass


class FesteVerspaetung(VerspaetungsKorrektur):
    """
    verspaetung auf einen festen wert setzen.

    kann bei vorzeitiger abfahrt auch negativ sein.

    diese klasse ist für manuelle eingriffe des fahrdienstleiters gedacht.
    """

    def __init__(self, planung: 'Planung'):
        super().__init__(planung)
        self.verspaetung: int = 0

    def anwenden(self, zug: 'ZugDetailsPlanung', ziel: 'ZugZielPlanung'):
        ziel.verspaetung_ab = self.verspaetung


class PlanmaessigeAbfahrt(VerspaetungsKorrektur):
    """
    planmaessige abfahrt oder verspaetung aufholen, wenn moeglich

    dies ist die normale abfertigung in abwesenheit soweit kein anderer zug involviert ist.
    die verspaetung wird soweit moeglich reduziert, ohne die mindestaufenthaltsdauer zu unterschreiten.
    """

    def anwenden(self, zug: 'ZugDetailsPlanung', ziel: 'ZugZielPlanung'):
        try:
            plan_an = time_to_minutes(ziel.an)
        except AttributeError:
            logger.debug(f"zug {zug.name} hat keine ankunft in zeile {ziel}")
            return
        try:
            plan_ab = time_to_minutes(ziel.ab)
        except AttributeError:
            plan_ab = plan_an + ziel.mindestaufenthalt

        ankunft = plan_an + ziel.verspaetung_an
        aufenthalt = max(plan_ab - ankunft, ziel.mindestaufenthalt)
        abfahrt = ankunft + aufenthalt
        ziel.verspaetung_ab = abfahrt - plan_ab


class AnkunftAbwarten(VerspaetungsKorrektur):
    """
    wartet auf einen anderen zug.

    die abfahrtsverspätung des von dieser korrektur kontrollierten fahrplanziels
    richtet sich nach der effektiven ankunftszeit des anderen zuges
    oder der eigenen verspätung.

    diese korrektur wird von der auto-korrektur bei ersatzzügen, kupplungen und flügelungen eingesetzt,
    kann aber auch in der fdl_korrektur verwendet werden, um abhängigkeiten zu definieren.

    attribute
    --------

    - ursprung: fahrplanziel des abzuwartenden zuges
    - wartezeit: wartezeit nach ankunft des abzuwartenden zuges
    """

    def __init__(self, planung: 'Planung'):
        super().__init__(planung)
        self.ursprung: Optional[ZugZielPlanung] = None
        self.wartezeit: int = 0

    def anwenden(self, zug: 'ZugDetailsPlanung', ziel: 'ZugZielPlanung'):
        try:
            plan_an = time_to_minutes(ziel.an)
        except AttributeError:
            plan_an = None

        try:
            plan_ab = time_to_minutes(ziel.ab)
        except AttributeError:
            plan_ab = plan_an + ziel.mindestaufenthalt

        if plan_an is None:
            plan_an = plan_ab

        ankunft = plan_an + ziel.verspaetung_an
        aufenthalt = max(plan_ab - ankunft, ziel.mindestaufenthalt)
        anschluss_an = time_to_minutes(self.ursprung.an) + self.ursprung.verspaetung_an
        anschluss_ab = anschluss_an + self.wartezeit
        abfahrt = max(ankunft + aufenthalt, anschluss_ab)
        ziel.verspaetung_ab = abfahrt - plan_ab


class AbfahrtAbwarten(VerspaetungsKorrektur):
    """
    wartet, bis ein anderer zug abgefahren ist.

    die abfahrtsverspätung des von dieser korrektur kontrollierten fahrplanziels
    richtet sich nach der abfahrtszeit des anderen zuges und der eigenen verspätung.

    diese korrektur wird von der auto-korrektur bei flügelungen eingesetzt,
    kann aber auch in der fdl_korrektur verwendet werden, um abhängigkeiten zu definieren.

    attribute
    --------

    - ursprung: fahrplanziel des abzuwartenden zuges
    - wartezeit: wartezeit nach ankunft des abzuwartenden zuges
    """

    def __init__(self, planung: 'Planung'):
        super().__init__(planung)
        self.ursprung: Optional[ZugZielPlanung] = None
        self.wartezeit: int = 0

    def anwenden(self, zug: 'ZugDetailsPlanung', ziel: 'ZugZielPlanung'):
        try:
            plan_an = time_to_minutes(ziel.an)
        except AttributeError:
            plan_an = None

        try:
            plan_ab = time_to_minutes(ziel.ab)
        except AttributeError:
            plan_ab = plan_an + ziel.mindestaufenthalt

        if plan_an is None:
            plan_an = plan_ab

        ankunft = plan_an + ziel.verspaetung_an
        aufenthalt = max(plan_ab - ankunft, ziel.mindestaufenthalt)
        anschluss_ab = time_to_minutes(self.ursprung.ab) + self.ursprung.verspaetung_ab
        anschluss_ab = anschluss_ab + self.wartezeit
        abfahrt = max(ankunft + aufenthalt, anschluss_ab)
        ziel.verspaetung_ab = abfahrt - plan_ab


class Ersatzzug(VerspaetungsKorrektur):
    """
    abfahrt frühestens wenn nummernwechsel abgeschlossen ist

    das erste fahrplanziel des ersatzzuges muss it einer AnschlussAbwarten-korrektur markiert sein.
    """
    def anwenden(self, zug: 'ZugDetailsPlanung', ziel: 'ZugZielPlanung'):
        try:
            plan_an = time_to_minutes(ziel.an)
        except AttributeError:
            logger.debug(f"zug {zug.name} hat keine ankunft in zeile {ziel}")
            return

        try:
            plan_ab = time_to_minutes(ziel.ersatzzug.fahrplan[0].an)
        except (AttributeError, IndexError):
            try:
                plan_ab = time_to_minutes(ziel.ab)
            except AttributeError:
                plan_ab = plan_an + ziel.mindestaufenthalt

        ankunft = plan_an + ziel.verspaetung_an
        aufenthalt = max(plan_ab - ankunft, ziel.mindestaufenthalt)
        abfahrt = ankunft + aufenthalt
        ziel.verspaetung_ab = abfahrt - plan_ab
        ziel.ab = minutes_to_time(abfahrt - ziel.verspaetung_ab)

        if ziel.ersatzzug:
            ziel.ersatzzug.verspaetung = ziel.verspaetung_ab
            self._planung.zugverspaetung_korrigieren(ziel.ersatzzug)


class Kupplung(VerspaetungsKorrektur):
    """
    zwei züge kuppeln

    gekuppelter zug kann erst abfahren, wenn beide züge angekommen sind.

    bemerkung: der zug mit dem kuppel-flag verschwindet. der verlinkte zug fährt weiter.
    """
    def anwenden(self, zug: 'ZugDetailsPlanung', ziel: 'ZugZielPlanung'):
        try:
            plan_an = time_to_minutes(ziel.an)
        except AttributeError:
            logger.warning(f"zug {zug} hat keine ankunft in zeile {ziel}")
            return

        try:
            plan_ab = time_to_minutes(ziel.ab)
        except (AttributeError, IndexError):
            plan_ab = plan_an + ziel.mindestaufenthalt

        # zuerst die verspaetung des kuppelnden zuges berechnen
        try:
            self._planung.zugverspaetung_korrigieren(ziel.kuppelzug)
            kuppel_index = ziel.kuppelzug.find_fahrplan_index(plan=ziel.plan)
            kuppel_ziel = ziel.kuppelzug.fahrplan[kuppel_index]
            kuppel_verspaetung = kuppel_ziel.verspaetung_an
            kuppel_an = time_to_minutes(kuppel_ziel.an) + kuppel_verspaetung
        except (AttributeError, IndexError):
            kuppel_an = 0

        while abs(kuppel_an - (plan_an + ziel.verspaetung_an)) < 2:
            ziel.verspaetung_an += 1

        ankunft = plan_an + ziel.verspaetung_an
        aufenthalt = max(plan_ab - ankunft, ziel.mindestaufenthalt)
        abfahrt = max(ankunft + aufenthalt, kuppel_an)
        ziel.verspaetung_ab = abfahrt - plan_ab

        if ziel.kuppelzug:
            self._planung.zugverspaetung_korrigieren(ziel.kuppelzug)


class Fluegelung(VerspaetungsKorrektur):
    def anwenden(self, zug: 'ZugDetailsPlanung', ziel: 'ZugZielPlanung'):
        try:
            plan_an = time_to_minutes(ziel.an)
        except AttributeError:
            logger.warning(f"zug {zug} hat keine ankunft in zeile {ziel}")
            return

        try:
            plan_ab = time_to_minutes(ziel.ab)
        except (AttributeError, IndexError):
            plan_ab = plan_an + ziel.mindestaufenthalt

        ankunft = plan_an + ziel.verspaetung_an
        aufenthalt = max(plan_ab - ankunft, ziel.mindestaufenthalt)
        abfahrt = ankunft + aufenthalt
        ziel.verspaetung_ab = abfahrt - plan_ab

        if ziel.fluegelzug:
            ziel.fluegelzug.verspaetung = ziel.verspaetung_an
            ziel.fluegelzug.fahrplan[0].verspaetung_an = ziel.verspaetung_an
            self._planung.zugverspaetung_korrigieren(ziel.fluegelzug)


class ZugDetailsPlanung(ZugDetails):
    """
    ZugDetails für das planungsmodul

    dies ist eine unterklasse von ZugDetails, wie sie vom planungsmodul verwendet wird.
    im planungsmodul haben einige attribute eine geänderte bedeutung.
    insbesondere bleibt der fahrplan vollständig (abgefahrene ziele werden nicht gelöscht)
    und enthält auch die ein- und ausfahrten als erste/letzte zeile
    (ausser der zug beginnt oder endet im stellwerk).

    wenn der zug neu angelegt wird, übernimmt die assign_zug_details-methode die daten vom PluginClient.
    die update_zug_details-methode aktualisert die veränderlichen attribute, z.b. gleis, verspätung etc.
    """
    def __init__(self):
        super().__init__()
        self.ausgefahren: bool = False
        self.folgezuege_aufgeloest: bool = False
        self.korrekturen_definiert: bool = False

    @property
    def einfahrtszeit(self) -> datetime.time:
        """
        planmässige einfahrtszeit (ohne verspätung)

        dies entspricht der abfahrtszeit des ersten fahrplaneintrags (einfahrt).

        :return: uhrzeit als datetime.time
        :raise IndexError, wenn der fahrplan keinen eintrag enthält.
        """
        return self.fahrplan[0].ab

    @property
    def ausfahrtszeit(self) -> datetime.time:
        """
        planmässige ausfahrtszeit (ohne verspätung)

        dies enstspricht der ankunftszeit des letzten fahrplaneintrags (ausfahrt).

        :return: uhrzeit als datetime.time
        :raise IndexError, wenn der fahrplan keinen eintrag enthält.
        """
        return self.fahrplan[-1].an

    def route(self, plan: bool = False) -> Iterable[str]:
        """
        route (reihe von stationen) des zuges als generator

        die route ist eine liste von stationen (gleisen, ein- und ausfahrt) in der reihenfolge des fahrplans.
        ein- und ausfahrten können bei ersatzzügen o.ä. fehlen.
        durchfahrtsgleise sind auch enthalten.

        die methode liefert das gleiche ergebnis wie die überschriebene methode.
        aber da in der planung die ein- und ausfahrten im fahrplan enthalten sind,
        ist die implementierung etwas einfacher.

        :param plan: plangleise statt effektive gleise melden
        :return: generator
        """
        for fpz in self.fahrplan:
            if plan:
                yield fpz.plan
            else:
                yield fpz.gleis

    def assign_zug_details(self, zug: ZugDetails):
        """
        objekt mit stammdaten vom PluginClient initialisieren.

        unterschiede zum original-ZugDetails:
        - ein- und ausfahrtsgleise werden als separate fahrplanzeile am anfang bzw. ende der liste eingefügt
          und mit den attributen einfahrt bzw. ausfahrt markiert.
          ankunfts- und abfahrtszeiten werden dem benachbarten fahrplanziel gleichgesetzt.
        - der text 'Gleis', wenn der zug im stellwerk beginnt oder endet, wird aus dem von/nach entfernt.
          das gleis befindet sich bereits im fahrplan, es wird keine zusätzliche ein-/ausfahrt-zeile eingefügt.

        :param zug: original-ZugDetails-objekt vom PluginClient.zugliste.
        :return: None
        """
        self.zid = zug.zid
        self.name = zug.name
        self.von = zug.von.replace("Gleis ", "") if zug.von else ""
        self.nach = zug.nach.replace("Gleis ", "") if zug.nach else ""
        self.hinweistext = zug.hinweistext

        self.fahrplan = []
        if not self.sichtbar and self.von and not zug.von.startswith("Gleis"):
            ziel = ZugZielPlanung(self)
            ziel.plan = ziel.gleis = self.von
            try:
                ziel.ab = ziel.an = zug.fahrplan[0].an
            except IndexError:
                pass
            ziel.einfahrt = True
            self.fahrplan.append(ziel)
        for zeile in zug.fahrplan:
            ziel = ZugZielPlanung(self)
            ziel.assign_fahrplan_zeile(zeile)
            self.fahrplan.append(ziel)
        if self.nach and not zug.nach.startswith("Gleis"):
            ziel = ZugZielPlanung(self)
            ziel.plan = ziel.gleis = self.nach
            try:
                ziel.ab = ziel.an = zug.fahrplan[-1].ab
            except IndexError:
                pass
            ziel.ausfahrt = True
            self.fahrplan.append(ziel)

        for index, ziel in enumerate(self.fahrplan):
            if zug.plangleis == ziel.plan:
                self.ziel_index = index
                break
        else:
            if len(zug.fahrplan) and not zug.sichtbar:
                self.ziel_index = 0
            else:
                self.ziel_index = None

    def update_zug_details(self, zug: ZugDetails):
        """
        aktualisiert die veränderlichen attribute vom PluginClient

        die folgenden attribute werden aktualisert, alle anderen bleiben unverändert.
        gleis, plangleis, amgleis, sichtbar, verspaetung, usertext, usertextsender, fahrplanzeile.
        wenn der zug ausfährt, wird das gleis dem nach-attribut gleichgesetzt.

        im fahrplan werden die gleisänderungen aktualisiert.

        :param zug: original-ZugDetails-objekt vom PluginClient.zugliste.
        :return: None
        """
        self.gleis = zug.gleis
        self.plangleis = zug.plangleis
        self.verspaetung = zug.verspaetung
        self.amgleis = zug.amgleis
        self.sichtbar = zug.sichtbar
        self.usertext = zug.usertext
        self.usertextsender = zug.usertextsender

        if len(zug.fahrplan) == 0:
            self.gleis = self.plangleis = self.nach

        for zeile in zug.fahrplan:
            ziel = self.find_fahrplanzeile(plan=zeile.plan)
            try:
                ziel.update_fahrplan_zeile(zeile)
            except AttributeError:
                pass

        route = list(self.route(plan=True))
        try:
            self.ziel_index = route.index(zug.plangleis)
        except ValueError:
            pass

        for zeile in zug.fahrplan[0:self.ziel_index]:
            zeile.passiert = True


class ZugZielPlanung(FahrplanZeile):
    """
    fahrplanzeile im planungsmodul

    in ergänzung zum originalen FahrplanZeile objekt, führt diese klasse:
    - nach ziel aufgelöste ankunfts- und abfahrtsverspätung.
    - daten zur verspätungsanpassung.
    - status des fahrplanziels.
      nachdem das ziel passiert wurde, sind die verspätungsangaben effektiv, vorher schätzwerte.

    """

    def __init__(self, zug: ZugDetails):
        super().__init__(zug)

        self.einfahrt: bool = False
        self.ausfahrt: bool = False
        # verspaetung ist die geschätzte verspätung bei der abfahrt von diesem wegpunkt.
        # solange der zug noch nicht am gleis angekommen ist,
        # kann z.b. das auswertungsmodul oder der fahrdienstleiter die geschätzte verspätung anpassen.
        self.verspaetung_an: int = 0
        self.verspaetung_ab: int = 0
        self.mindestaufenthalt: int = 0
        self.auto_korrektur: Optional[VerspaetungsKorrektur] = None
        self.fdl_korrektur: Optional[VerspaetungsKorrektur] = None
        self.passiert: bool = False

    def assign_fahrplan_zeile(self, zeile: FahrplanZeile):
        """
        objekt aus fahrplanzeile initialisieren.

        die gemeinsamen attribute werden übernommen.
        folgezüge bleiben leer.

        :param zeile: FahrplanZeile vom PluginClient
        :return: None
        """
        self.gleis = zeile.gleis
        self.plan = zeile.plan
        self.an = zeile.an
        self.ab = zeile.ab
        self.flags = zeile.flags
        self.hinweistext = zeile.hinweistext

        # die nächsten drei attribute werden separat anhand der flags aufgelöst.
        self.ersatzzug = None
        self.fluegelzug = None
        self.kuppelzug = None

    def update_fahrplan_zeile(self, zeile: FahrplanZeile):
        """
        objekt aus fahrplanzeile aktualisieren.

        aktualisiert werden nur:
        - gleis: weil möglicherweise eine gleisänderung vorgenommen wurde.

        alle anderen attribute sind statisch oder werden vom Planung objekt aktualisiert.

        :param zeile: FahrplanZeile vom PluginClient
        :return: None
        """
        self.gleis = zeile.gleis

    @property
    def ankunft_minute(self) -> Optional[int]:
        """
        ankunftszeit inkl. verspätung in minuten

        :return: minuten seit mitternacht oder None, wenn die zeitangabe fehlt.
        """
        try:
            return time_to_minutes(self.an) + self.verspaetung_an
        except AttributeError:
            return None

    @property
    def abfahrt_minute(self) -> Optional[int]:
        """
        abfahrtszeit inkl. verspätung in minuten

        :return: minuten seit mitternacht oder None, wenn die zeitangabe fehlt.
        """
        try:
            return time_to_minutes(self.ab) + self.verspaetung_ab
        except AttributeError:
            return None

    @property
    def verspaetung(self) -> int:
        """
        abfahrtsverspaetung

        dies ist ein alias von verspaetung_ab und sollte in neuem code nicht mehr verwendet werden.

        :return: verspaetung in minuten
        """
        return self.verspaetung_ab


class Planung:
    """
    zug-planung und disposition

    diese klasse führt eine zugliste ähnlich zu der vom PluginClient.
    sie unterscheidet sich jedoch in einigen merkmalen:

    - die liste enthält ZugDetailsPlanung-objekte statt ZugDetails.
    - züge werden bei ihrem ersten auftreten in den quelldaten übernommen und bleiben in der liste,
      bis sie explizit entfernt werden.
    - bei folgenden quelldatenübernahmen, werden nur noch die zielattribute nachgeführt,
      der fahrplan bleibt jedoch bestehen (im PluginClient werden abgefahrene ziele entfernt).
    - die fahrpläne der züge haben auch einträge zur einfahrt und ausfahrt.
    """
    def __init__(self):
        self.zugliste: Dict[int, ZugDetailsPlanung] = dict()
        self.auswertung: Optional[Auswertung] = None

    def zuege_uebernehmen(self, zuege: Iterable[ZugDetails]):
        """
        interne zugliste mit sim-daten aktualisieren.

        - neue züge übernehmen
        - bekannte züge aktualisieren
        - ausgefahrene züge markieren
        - links zu folgezügen aktualisieren
        - verspätungsmodell aktualisieren

        :param zuege:
        :return:
        """
        verarbeitete_zuege = set(self.zugliste.keys())

        for zug in zuege:
            try:
                zug_planung = self.zugliste[zug.zid]
            except KeyError:
                # neuer zug
                zug_planung = ZugDetailsPlanung()
                zug_planung.assign_zug_details(zug)
                zug_planung.update_zug_details(zug)
                self.zug_korrekturen_definieren(zug_planung)
                self.zugliste[zug_planung.zid] = zug_planung
                verarbeitete_zuege.discard(zug.zid)
            else:
                # bekannter zug
                zug_planung.update_zug_details(zug)
                verarbeitete_zuege.discard(zug.zid)

        for zid in verarbeitete_zuege:
            zug = self.zugliste[zid]
            if zug.sichtbar:
                zug.sichtbar = zug.amgleis = False
                zug.gleis = zug.plangleis = ""
                zug.ausgefahren = True

        self.folgezuege_aufloesen()
        self.korrekturen_definieren()

    def folgezuege_aufloesen(self):
        """
        folgezüge aus den zugflags auflösen.

        folgezüge werden im stammzug referenziert.
        die funktion arbeitet iterativ, bis alle folgezüge aufgelöst sind.

        :return: None
        """

        zids = list(self.zugliste.keys())

        while zids:
            zid = zids.pop(0)
            try:
                zug = self.zugliste[zid]
            except KeyError:
                continue

            if zug.folgezuege_aufgeloest:
                continue
            folgezuege_aufgeloest = True

            for planzeile in zug.fahrplan:
                if set(planzeile.flags).intersection({'E', 'F', 'K'}):
                    if zid2 := planzeile.ersatz_zid():
                        try:
                            zug2 = self.zugliste[zid2]
                        except KeyError:
                            planzeile.ersatzzug = None
                            folgezuege_aufgeloest = False
                        else:
                            planzeile.ersatzzug = zug2
                            zug2.stammzug = zug
                            zids.append(zid2)

                    if zid2 := planzeile.fluegel_zid():
                        try:
                            zug2 = self.zugliste[zid2]
                        except KeyError:
                            planzeile.fluegelzug = None
                            folgezuege_aufgeloest = False
                        else:
                            planzeile.fluegelzug = zug2
                            zug2.stammzug = zug
                            zids.append(zid2)

                    if zid2 := planzeile.kuppel_zid():
                        try:
                            zug2 = self.zugliste[zid2]
                        except KeyError:
                            planzeile.kuppelzug = None
                            folgezuege_aufgeloest = False
                        else:
                            planzeile.kuppelzug = zug2
                            zug2.stammzug = zug
                            zids.append(zid2)

            zug.folgezuege_aufgeloest = folgezuege_aufgeloest

    def einfahrten_korrigieren(self):
        for zug in self.zugliste.values():
            try:
                einfahrt = zug.fahrplan[0]
                ziel1 = zug.fahrplan[1]
            except IndexError:
                pass
            else:
                if einfahrt.einfahrt and einfahrt.gleis and ziel1.gleis:
                    fahrzeit = self.auswertung.fahrzeit_schaetzen(zug.name, einfahrt.gleis, ziel1.gleis)
                    if not np.isnan(fahrzeit):
                        try:
                            einfahrt.an = einfahrt.ab = seconds_to_time(time_to_seconds(ziel1.an) - fahrzeit)
                            logger.debug(f"einfahrt {einfahrt.gleis} - {ziel1.gleis} korrigiert: {einfahrt.ab}")
                        except (AttributeError, ValueError):
                            pass

            try:
                ziel2 = zug.fahrplan[-2]
                ausfahrt = zug.fahrplan[-1]
            except IndexError:
                pass
            else:
                if ausfahrt.ausfahrt:
                    fahrzeit = self.auswertung.fahrzeit_schaetzen(zug.name, ziel2.gleis, ausfahrt.gleis)
                    if not np.isnan(fahrzeit):
                        try:
                            ausfahrt.an = ausfahrt.ab = seconds_to_time(time_to_seconds(ziel2.ab) + fahrzeit)
                            logger.debug(f"ausfahrt {ziel2.gleis} - {ausfahrt.gleis} korrigiert: {ausfahrt.an}")
                        except (AttributeError, ValueError):
                            pass

    def verspaetungen_korrigieren(self):
        zids = list(filter(lambda z: self.zugliste[z].stammzug is None, self.zugliste.keys()))
        while zids:
            zid = zids.pop(0)
            try:
                zug = self.zugliste[zid]
            except KeyError:
                continue
            else:
                self.zugverspaetung_korrigieren(zug)

    def zugverspaetung_korrigieren(self, zug: ZugDetailsPlanung, start: int = None, stop: int = None):
        verspaetung = zug.verspaetung

        if start is None:
            start = zug.ziel_index
        if start is None:
            start = 0

        # aktuelle verspaetung uebernehmen
        try:
            if start >= 1:
                zug.fahrplan[start-1].verspaetung_ab = verspaetung
        except IndexError:
            pass

        try:
            einfahrt = zug.fahrplan[0]
            if einfahrt.einfahrt:
                einfahrt.verspaetung_an = einfahrt.verspaetung_ab
        except IndexError:
            pass

        sl = slice(start, stop)
        for ziel in zug.fahrplan[sl]:
            ziel.verspaetung_ab = ziel.verspaetung_an = verspaetung

            try:
                ziel.auto_korrektur.anwenden(zug, ziel)
            except AttributeError:
                pass

            try:
                ziel.fdl_korrektur.anwenden(zug, ziel)
            except AttributeError:
                pass

            verspaetung = ziel.verspaetung_ab

    def korrekturen_definieren(self):
        for zug in self.zugliste.values():
            if not zug.korrekturen_definiert:
                result = self.zug_korrekturen_definieren(zug)
                zug.korrekturen_definiert = zug.folgezuege_aufgeloest and result

    def zug_korrekturen_definieren(self, zug: ZugDetailsPlanung) -> bool:
        result = True
        for ziel in zug.fahrplan:
            ziel_result = self.ziel_korrekturen_definieren(ziel)
            result = result and ziel_result
        return result

    def ziel_korrekturen_definieren(self, ziel: ZugZielPlanung) -> bool:
        if ziel.einfahrt or ziel.ausfahrt or ziel.durchfahrt():
            ziel.mindestaufenthalt = 0
            return True

        result = True

        if ziel.richtungswechsel():
            ziel.mindestaufenthalt = 2
        elif ziel.lokumlauf():
            ziel.mindestaufenthalt = 2
        elif ziel.lokwechsel():
            ziel.mindestaufenthalt = 5

        if ziel.ersatz_zid():
            ziel.auto_korrektur = Ersatzzug(self)
            anschluss = AnkunftAbwarten(self)
            anschluss.ursprung = ziel
            try:
                ziel.ersatzzug.fahrplan[0].auto_korrektur = anschluss
            except (AttributeError, IndexError):
                result = False
        elif ziel.kuppel_zid():
            ziel.auto_korrektur = Kupplung(self)
            anschluss = AnkunftAbwarten(self)
            anschluss.ursprung = ziel
            try:
                kuppel_ziel = ziel.kuppelzug.find_fahrplanzeile(plan=ziel.plan)
                kuppel_ziel.auto_korrektur = anschluss
            except (AttributeError, IndexError):
                result = False
        elif ziel.fluegel_zid():
            ziel.auto_korrektur = Fluegelung(self)
            ziel.mindestaufenthalt = 1
            anschluss = AbfahrtAbwarten(self)
            anschluss.ursprung = ziel
            anschluss.wartezeit = 2
            try:
                ziel.fluegelzug.fahrplan[0].auto_korrektur = anschluss
            except (AttributeError, IndexError):
                result = False
        elif ziel.auto_korrektur is None:
            ziel.auto_korrektur = PlanmaessigeAbfahrt(self)

        return result

    def ereignis_uebernehmen(self, ereignis: Ereignis):
        """
        daten von einem ereignis uebernehmen.

        noch nicht implementiert.

        :param ereignis:
        :return:
        """
        try:
            zug = self.zugliste[ereignis.zid]
        except KeyError:
            return None

        if ereignis.art == 'xxx':
            zug.sichtbar = False
            zug.amgleis = False
            zug.gleis = ""
            zug.plangleis = ""
