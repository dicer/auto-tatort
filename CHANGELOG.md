2.3.0
=====
Unterstuetzung der neuen JSON Struktur. Die alte scheint noch direkt nach Ausstrahlung zu funktionieren, aber wenn man ein paar Tage später versucht die Sendung runter zu laden, kam es zu Fehlern.

2.2.0
=====
- Workaround fuer kaputte Download aus 2.1.00 in README verlinkt
- Unterstuetzung von HD files, sofern diese gefunden werden koennen. Das Feature wurde aus Mediathekview adaptiert: https://github.com/mediathekview/MServer/blob/master/src/main/java/mServer/crawler/sender/MediathekArd.java#L151

2.1.01
======
Issue #16 behoben: Download laed nun wieder mp4s anstatt wenige Kilobyte grosse Version

2.1.00
======
Support um xml Untertitel nach srt zu konvertieren

2.0.01
======
Anpassung an neues Datumsformat im RSS feed

2.0.00
======

- Konfiguration aus Script in eine Config-Datei im Json-Format ausgelagert
- Unterstuetzt nun nicht nur den Tatort RSS-Feed, sondern beliebige ARD Mediathek RSS Feeds und das gleichzeitig in einer Config. Allerdings ohne speziellen Support. Ziel ist nach wie vor hauptsaechlich der Tatortfeed.
- Erfolgreich runtergeladene Folgen werden in einer Json-Datei gemerkt und nicht nochmal runtergeladen. Dadurch beliebige Startzeiten und Pausen bei der Ausfuehrung
- Fehlermeldungen bei Verbindungsfehlern
- Der Folgentitel kann nun gefiltert werden. Dadurch wird der Dateiname etwas schoener.
- Das Datum der Folge kann vor den Titel gehaengt werden. Dadurch Unterstuetzung fuer Mediathek-Feeds wo alle Folgen den gleichen Namen haben.
- Auf Basis vom Titel koennen Folgen beim Download uebersprungen werden (Keine Hoerfassung etc)
- Im Zielverzeichnis schon vorhandene Dateien werden nicht nochmal runter geladen

Hinweis: Nach dem Update von Version 1, muss einmalig die config.json.sample nach config.json kopiert und angepasst werden.

1.0.00
======

Commit 88dba4f24dd69c76fd1c82422d157c301898537d wird nachtraeglich zu Version 1.0.00 erklaert
