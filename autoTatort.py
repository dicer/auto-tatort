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

#set to False if you don't want subtitles
SUBTITLES = True

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

      if 'http://www.ardmediathek.de/-/stoerung' == response.geturl():
        print "Could not get item with title '" + title + "'. Got redirected to '" + response.geturl() + "'. This is probably because the item is still in the RSS feed, but not available anymore."
        continue

      try:
        media = json.loads(html)
      except ValueError as e:
        print e
        print "Could not get item with title '" + title + "'. Original item link is '" + link + "' and parsed docId[0] is '" + docId[0] + "', but html response from '" + docUrl + "' was '" + html + "'"
        continue

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

            #download subtitles
            try:
              if SUBTITLES and '_subtitleUrl' in media and len(media["_subtitleUrl"]) > 0:
                offset = 0
                if '_subtitleOffset' in media:
                 offset = media["_subtitleOffset"]

                subtitleURL = 'http://www.ardmediathek.de/' + media["_subtitleUrl"]
                urlretrieve(subtitleURL, TARGET_DIR + fileName + "_subtitleOffset_" + str(offset) + ".xml")
            except Exception as e:
              #print and resume with download
              print e
              print subtitleURL

