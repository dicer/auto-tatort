#!/usr/bin/python
import sys, codecs, locale
import feedparser
import datetime
import urlparse
from urllib import urlopen, urlretrieve
import json
import os.path

#Wrap sysout so we don't run into problems when printing unicode characters to the console.
#This would otherwise be a problem when we are invoked on Debian using cron: 
#Console will have encoding NONE and fail to print some titles with umlauts etc
#might also fix printing on Windows consoles
#see https://wiki.python.org/moin/PrintFails
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)


def debug(text):
  if myConfig["debug"] == 1:
    print text



configFile = os.path.dirname(os.path.realpath(__file__)) + os.sep + "config.json"
if (os.path.isfile(configFile)) != True:
    print "Could not find the config file 'config.json' at " + configFile
    sys.exit(1)

myConfig = json.loads(open(configFile).read())



for feed in myConfig["feeds"]:
  
  if feed["enabled"] != 1:
    continue

  rssUrl = feed["url"]
  debug(rssUrl)

  # -1 = download highest quality available
  # 0.0 320x180 (53k audio)i
  # 1.0 512x288 (93k audio)
  # 1.1 480x270 (61k audio)
  # 2.0 640x360 (189k audio)
  # 2.1 960x540 (189k audio)

  #you can currently only select the highest quality within one tier. So 1 will dowload 1.1 and 2 will download 2.1. 0 will download 0.0
  quality = feed["quality"]
  debug(quality)

  #set to False if you don't want subtitles
  downloadSubs = feed["subtitles"]
  debug(downloadSubs)

  targetDir = feed["targetFolder"]
  debug(targetDir)

  feed = feedparser.parse( rssUrl )

  items = feed.entries

  today = datetime.date.today()
  #today = datetime.date(2015,8,30)


  for item in items:
    year = item["date_parsed"][0];
    month = item["date_parsed"][1];
    day = item["date_parsed"][2];
    feedDate = datetime.date(item["date_parsed"][0], item["date_parsed"][1], item["date_parsed"][2])

    if feedDate != today:
      continue

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

    downloadQuality = quality

    #get best quality?
    if downloadQuality == -1:
      downloadQuality = 0
      for mediaLink in mediaLinks:
        if mediaLink["_quality"] > downloadQuality and '_stream' in mediaLink:
          downloadQuality = mediaLink["_quality"]


    downloadedSomething = 0

    for mediaLink in mediaLinks:
      if downloadQuality != mediaLink["_quality"]:
        continue

      stream = mediaLink["_stream"]
      mediaURL = ""
      #check if the selected quality has two stream urls
      if type(stream) is list or type(stream) is tuple:
        if len(stream) > 1:
          mediaURL = stream[1]
        else:
          mediaURL = stream[0]
      else:
        mediaURL = stream

      fileName = "".join([x if x.isalnum() or x in "- " else "" for x in title])
      urlretrieve(mediaURL, TARGET_DIR + fileName + ".mp4")
      downloadedSomething = 1
      print "Downloaded '" + title + "'"

      #download subtitles
      try:
        if downloadSubs and '_subtitleUrl' in media and len(media["_subtitleUrl"]) > 0:
          offset = 0
          if '_subtitleOffset' in media:
            offset = media["_subtitleOffset"]

          subtitleURL = 'http://www.ardmediathek.de/' + media["_subtitleUrl"]
          urlretrieve(subtitleURL, TARGET_DIR + fileName + "_subtitleOffset_" + str(offset) + ".xml")
      except Exception as e:
        #print and resume with download
        print e
        print subtitleURL

    #check whether we download something
    if downloadedSomething == 0:
      print "Could not download '" + title + "' because of an error or nothing matching your quality selection"




def debug(text):
  if config["debug"] == 1:
    print text
