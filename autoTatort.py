#!/usr/bin/python
import sys, codecs, locale
import feedparser
import datetime
import urlparse
from urllib import urlopen, urlretrieve
import json

#Wrap sysout so we don't run into problems when printing unicode characters to the console.
#This would otherwise be a problem when we are invoked on Debian using cron: 
#Console will have encoding NONE and fail to print some titles with umlauts etc
#might also fix printing on Windows consoles
#see https://wiki.python.org/moin/PrintFails
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout);

RSS_URL = "http://www.ardmediathek.de/tv/Tatort/Sendung?documentId=602916&bcastId=602916&rss=true"

#0=256x144 (61k audio)
#1=512x288 (125k audio)
#2=640x360 (189k audio)
#3=960x544 (189k audio)
QUALITY = 3

TARGET_DIR = "/data/tatort/"


feed = feedparser.parse( RSS_URL )

items = feed.entries

today = datetime.date.today()

for item in items:
   year = item["date_parsed"][0];
   month = item["date_parsed"][1];
   day = item["date_parsed"][2];
   feedDate = datetime.date(item["date_parsed"][0], item["date_parsed"][1], item["date_parsed"][2])

   if feedDate == today:
      title = item["title"]
      link = item["link"]
      parsed = urlparse.urlparse(link)
      docId = urlparse.parse_qs(parsed.query)['documentId']
      docUrl = 'http://www.ardmediathek.de/play/media/' + docId[0] + '?devicetype=pc&features=flash'

      response = urlopen(docUrl)
      html = response.read()

      try:
        media = json.loads(html)
      except ValueError, e:
        print e
        print "Could not get item with title '" + title + "'. Original item link is '" + link + "' and parsed docId[0] is '" + docId[0] + "', but html response from '" + docUrl + "' was '" + html + "'"

      if '_mediaArray' not in media or len(media["_mediaArray"]) == 0:
        print "Skipping " + title + " because it does not have any mediafiles"
        continue
      mediaLinks = media["_mediaArray"][1]["_mediaStreamArray"]

      for mediaLink in mediaLinks:
         if QUALITY == mediaLink["_quality"]:
            mediaURL = mediaLink["_stream"]
            fileName = "".join([x if x.isalnum() or x in "- " else "" for x in title])
            urlretrieve(mediaURL, TARGET_DIR + fileName + ".mp4")
            print "Downloaded '" + title + "'"
