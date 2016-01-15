auto-tatort
===========

Kleines Script um die aktuellen Tatort Folgen automatisiert (cron) aus der ARD Mediathek zu laden.

Wer ein weniger automatisiertes Script benoetigt und einfach nur eine Folge (bzw beliebige Sendung aus der Mediathek) runterladen moechte, schaut am besten bei Leo Gaggl vorbei: https://github.com/leogaggl/media/

Einsatz
=======

Die Datei config.json.sample nach config.json kopieren. Darin wenigstens mit targetFolder den Pfad angeben in dem die Dateien abgelegt werden sollen.
Die Vergabe des Dateinames erfolgt automatisch und basiert auf dem Titel des RSS Feed Eintrags.

Dann Script via cron automatisiert ausfuehren lassen:

30 * * * * python ~/bin/auto-tatort/autoTatort.py

Das Script laed alle Folgen, die es bisher noch nicht runtergeladen hat (siehe Config: downloadedFeedItemsDatabase) und fuer die es keine exclude-Filter gibt (siehe Config: exclude). Es kann daher beliebig haeufig ausgefuehrt werden, jedoch sollte es nicht haeufiger als alle 30 Minuten gestartet werden um nicht unnoetig Last auf der Mediathek zu erzeugen.

Untertitel
==========

Die meisten oder alle Tatortfolgen scheinen auch Untertitel zu enthalten. Diese werden automatisch mit runter geladen und im gleichen Verzeichnis abgelegt. Bisher sind das rohe XML Dateien, mit denen man noch nicht viel anfangen kann. Es wird spaeter mal einen Konverter geben, der diese in gebraeuchliche Formate umwandeln kann.
Wenn keine Untertitel gewuenscht sind, kann man das entsprechend in der Config anpassen.

Config
======

Die Konfiguration findet in der Datei config.json statt. Ein Beispiel findet sich in config.json.sample. Dabei ist das JSON-Format einzuhalten (hauptsaechlich weil sich dadurch keine weitere Bibliotheksabhaengigkeit ergibt).
Folgende Optionen koennen veraendert werden:

- debug: Sollen debug Informationen ausgegeben werden? Kann auf 1 gesetzt werden, allerdings bekommt man dann natuerlich jeden Tag eine Mail, sofern das Script via cron eingebunden ist
- feeds: Hier koennen mehrere RSS-Feeds aus der Mediathek abgefragt werden. Per Default ist der Tatortfeed voreingestellt.
  - enabled: Hier koennen einzelne Feeds deaktiviert werden, ohne sie aus der Config entfernen zu muessen
  - id: Eindeutige Id fuer den Feed. Wird aktuell nur zur besseren Wiedererkennung verwendet.
  - quality:
  - subtitles: Mit option 1 werden die teilweise angebotenen Untertitel-XML-Dateien runterladen.
  - targetFolder: Ordner in dem die runtergeladenen Dateien abgelegt werden sollen
  - url: http URL zu einem Mediathek RSS Feed
  - exclude: Eine Auflistung von RegExp (https://docs.python.org/2/howto/regex.html) mit denen Feeditems vom Download ausgeschlossen werden koennen. Matched auf den Titel. \ muss als \\ escaped werden
  - titleFilters: Eine Auflistung von replace-Strings: Diese Strings werden aus dem Titel (und damit spaeter dem Dateinamen) entfernt.
  - downloadedFeedItemsDatabase: Dateiname fuer die Ablage der schon runter geladenen Folgen. In dieser Datei werden die Mediathek documentIds gespeichert, die erfolgreich runter geladen wurden.
- version: Gibt die Schemaversion der Config-Datei an

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

Wurde nicht mit Python3 getestet, sollte aber vorher mit dem 2to3 Tool konvertiert werden!

Credits
=======
Author: Felix Knecht  
Die Idee hierzu ist aus den Scripten von Robin Gareus entstanden: http://www.rg42.org/wiki/tatort-dl
