auto-tatort
===========

Kleines Script um die aktuellen Tatort Folgen automatisiert (cron) aus der ARD Mediathek zu laden.

Wer ein weniger automatisiertes Script benoetigt und einfach nur eine Folge (bzw beliebige Sendung aus der Mediathek) runterladen moechte, schaut am besten bei Leo Gaggl vorbei: https://github.com/leogaggl/media/

Einsatz
=======

Die Datei config.json.sample nach config.json kopieren. Darin wenigstens mit targetFolder den Pfad angeben in dem die Dateien abgelegt werden sollen.
Die Vergabe des Dateinames erfolgt automatisch und basiert auf dem Titel des RSS Feed Eintrags.

Dann Script via cron automatisiert ausfuehren lassen:

30 0-23/2 * * * python ~/bin/auto-tatort/autoTatort.py

Das Script laed alle Folgen, die es bisher noch nicht runtergeladen hat (siehe Config: downloadedFeedItemsDatabase) und fuer die es keine exclude-Filter gibt (siehe Config: exclude). Es kann daher beliebig haeufig ausgefuehrt werden, jedoch sollte es nicht haeufiger als alle 30 Minuten gestartet werden um nicht unnoetig Last auf der Mediathek zu erzeugen. Desweiteren ist darauf zu achten, dass das Script nicht mehrmals gleichzeitig laeuft! Dabei auch bedenken, dass der Download immer eine Weile dauert.

Wenn der Rechner cron-Ausgaben via Email weiterleitet, bekommt man so mitgeteilt, wenn eine neue Folge erfolgreich runtergeladen wurde (oder es zu Fehlern kam). Wurde keine neue Folge gefunden, gibt das Script nichts zurueck und keine Email wird versendet.

Untertitel
==========

Die meisten oder alle Tatortfolgen scheinen auch Untertitel zu enthalten. Diese werden automatisch mit runter geladen und im gleichen Verzeichnis abgelegt. Das sind rohe XML Dateien, mit denen man noch nicht viel anfangen kann. Es gibt aber einen Konverter: https://github.com/haraldF/ttaf2srt
Wird dieser im PATH gefunden, wird das XML automatisch ins SRT-Format umgewandelt und mit dem gleichen Filenamen wie das mp4 und Endung ".srt" abgelegt. Dabei ist zu beachten, dass die Untertitel im UTF8 Format abgelegt werden. Manche Player erkennen das nicht automatisch und brauchen extra Optionen. Zb bei mplayer: "-subcp utf8"
Das originale XML-File wird danach nicht geloescht, damit man bei Fehlern im Konverter spaeter noch eine Chance hat ein korrektes SRT-File zu generieren.
Wenn keine Untertitel gewuenscht sind, kann man das entsprechend in der Config anpassen.
  
Wenn man Cron benutzt, sollte man darauf achten, dass der Pfad auch das ttaf2srt Script beinhaltet. Cron setzt diesen anders als bei einem Shell-Login des Users zu dem die crontab gehoert! Eine Moeglichkeit das zu beeinflussen: https://stackoverflow.com/questions/10129381/crontab-path-and-user  
Bei Ablage des Konverters in /home/autotatort/bin also zb: PATH=/home/autotatort/bin:/usr/local/bin:/usr/bin:/bin


Config
======

Die Konfiguration findet in der Datei config.json statt. Ein Beispiel findet sich in config.json.sample. Dabei ist das JSON-Format einzuhalten (hauptsaechlich weil sich dadurch keine weitere Bibliotheksabhaengigkeit ergibt).
Folgende Optionen koennen veraendert werden:

- debug: Sollen debug Informationen ausgegeben werden? Kann auf 1 gesetzt werden, allerdings bekommt man dann natuerlich jeden Tag eine Mail, sofern das Script via cron eingebunden ist
- debugFile: Sofern debug=1 und hier eine Datei angegeben wird, werden alle Debug-Infos in diese Datei gelogged (und nicht auf stdout). Stdout bekommt immer noch alle anderen Statusinformationen und Fehler (so wie ohne debug)
- feeds: Hier koennen mehrere RSS-Feeds aus der Mediathek abgefragt werden. Per Default ist der Tatortfeed voreingestellt. Fuer andere Feeds gibt es ausdruecklich keinen Support ;) Pull-Requests werden aber gerne angesehen.
  - enabled: Hier koennen einzelne Feeds deaktiviert werden, ohne sie aus der Config entfernen zu muessen
  - id: Eindeutige Id fuer den Feed. Wird aktuell nur zur besseren Wiedererkennung verwendet.
  - quality:
    - -1 = Automatisch die hoechste Qualitaet laden (Default)
    -  0 = 320x180 (53k audio, 12.5fps)
    -  1 = 480x270 (61k audio, 25fps) (es gibt auch noch 1.0 = 512x288 (93k audio, 25fps), aber das wird im Moment nicht unterstuetzt)
    -  2 = 960x540 (189k audio, 25fps) (es gibt auch noch 2.0 = 640x360 (189k audio, 25fps), aber das wird im Moment nicht unterstuetzt)
  - subtitles: Mit option 1 werden die teilweise angebotenen Untertitel-XML-Dateien runterladen.
  - targetFolder: Ordner in dem die runtergeladenen Dateien abgelegt werden sollen
  - url: http URL zu einem Mediathek RSS Feed
  - exclude: Eine Auflistung von RegExp (https://docs.python.org/2/howto/regex.html) mit denen Feeditems vom Download ausgeschlossen werden koennen. Matched auf den Titel. \ muss escaped werden
  - titleFilters: Eine Auflistung von replace-Strings: Diese Strings werden aus dem Titel (und damit spaeter dem Dateinamen) entfernt.
  - titlePrependItemDate: Nimmt das Datum der Folge und platziert es vor dem Titel im Dateinamen. Aus "Tatort xy.mp4" wird dann "2016-01-13 - Tatort xy.mp4"
  - downloadedFeedItemsDatabase: Dateiname fuer die Ablage der schon runter geladenen Folgen. In dieser Datei werden die Mediathek documentIds gespeichert, die erfolgreich runter geladen wurden.
- version: Gibt die Schemaversion der Config-Datei an. Beim Start Wird ueberprueft, ob das Script zur verwendeten Config-Datei passt. Wenn nicht, muessen die Aenderungen aus der config.json.sample uebernommen werden und die Versionsnummer erhoeht werden.

Abhaengigkeiten
===============

import sys, codecs, locale  
import feedparser (apt-get install python-feedparser)  
import datetime  
import urlparse  
from urllib import urlopen, urlretrieve  
import json  
import os.path  
import re  
import distutils.spawn  
import subprocess  

Wurde nicht mit Python3 getestet, sollte aber vorher mit dem 2to3 Tool konvertiert werden!

Credits
=======
Author: Felix Knecht  
Die Idee hierzu ist aus den Scripten von Robin Gareus entstanden: http://www.rg42.org/wiki/tatort-dl
