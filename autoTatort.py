#!/usr/bin/python
import sys
import feedparser
import datetime
import urlparse
from urllib import urlopen, urlretrieve
import json

RSS_URL = "http://www.ardmediathek.de/tv/Tatort/Sendung?documentId=602916&bcastId=602916&rss=true"

#1=512x288
#2=640x360
#3=960x544
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

      media = json.loads(html)
      mediaLinks = media["_mediaArray"][1]["_mediaStreamArray"]
      for mediaLink in mediaLinks:
         if QUALITY == mediaLink["_quality"]:
            mediaURL = mediaLink["_stream"]
            fileName = "".join([x if x.isalnum() or x in "- " else "" for x in title])
            urlretrieve(mediaURL, TARGET_DIR + fileName + ".mp4")
            print "Downloaded '" + title + "'"
