#!/usr/bin/python
import sys, codecs, locale
import feedparser
import datetime
import urlparse
from urllib import urlopen, urlretrieve
import json
import os.path
import re

#Wrap sysout so we don't run into problems when printing unicode characters to the console.
#This would otherwise be a problem when we are invoked on Debian using cron: 
#Console will have encoding NONE and fail to print some titles with umlauts etc
#might also fix printing on Windows consoles
#see https://wiki.python.org/moin/PrintFails
sys.stdout = codecs.getwriter(locale.getpreferredencoding())(sys.stdout)

DB_VERSION_REQUIRED = 5


def debug(text):
  if myConfig["debug"] == 1:
    print text


def excludeFeedBasedOnTitle(feedConfig, title):
  if "exclude" not in feedConfig or len(feedConfig["exclude"])==0:
    debug("No exclude section found")
    return False

  for exclude in feedConfig["exclude"]:
    p = re.compile(exclude["regexp"])
    if p.match(title) != None:
      debug("Title '" + title + "' was excluded by regexp '" + exclude["regexp"] + "'")
      return True
    else:
      debug("Title '" + title + "' was NOT excluded by regexp '" + exclude["regexp"] + "'")

  return False


def filterTitle(feedConfig, title):
  if "titleFilters" not in feedConfig or len(feedConfig["titleFilters"])==0:
    debug("No titleFilters section found")
    return title
  for filter in feedConfig["titleFilters"]:
    debug("Using replace filter '" + filter["replace"] + "'")
    title = title.replace(filter["replace"], ""); 
  return title


def saveDownloadedFeedsDB():
  open(downloadedFeedItemsDatabaseFile, "w").write(json.dumps(myDownloadedFeedItemsDatabase))


def markDocIdDownloaded(feedId, docId):
  if feedId not in myDownloadedFeedItemsDatabase:
    debug("Feed not yet in db. Addind feed '" + feedId + "' and docId '" + docId + "'")
    myDownloadedFeedItemsDatabase[feedId] = [docId]
    saveDownloadedFeedsDB()
  else:
    debug("Adding docId '" + docId + "' to seen-db")
    myDownloadedFeedItemsDatabase[feedId].append(docId)
    saveDownloadedFeedsDB()



configFile = os.path.dirname(os.path.realpath(__file__)) + os.sep + "config.json"
if (os.path.isfile(configFile)) != True:
  print "Could not find the config file 'config.json' at " + configFile
  sys.exit(1)

myConfig = json.loads(open(configFile).read())

myConfigVersion = myConfig["version"]
if myConfigVersion != DB_VERSION_REQUIRED:
  print "Your config.json version is not up to date. JSON: " + str(myConfigVersion) + "; Required: " + str(DB_VERSION_REQUIRED) + ". Please compare to config.json.sample, update your configuration and increase the version number in it"
  sys.exit(1)

downloadedFeedItemsDatabaseFile = os.path.dirname(os.path.realpath(__file__)) + os.sep + myConfig["downloadedFeedItemsDatabase"]
dbJson = ""
if (os.path.isfile(downloadedFeedItemsDatabaseFile)) != True:
  debug("Creating downloadedFeedItemsDatabase")
  dbJson = "{}"
else:
  dbJson = open(downloadedFeedItemsDatabaseFile).read()

myDownloadedFeedItemsDatabase = json.loads(dbJson)


for feed in myConfig["feeds"]:

  feedId = feed["id"]

  if feed["enabled"] != 1:
    continue

  rssUrl = feed["url"]
  debug(rssUrl)

  quality = feed["quality"]
  debug(quality)

  #set to False if you don't want subtitles
  downloadSubs = feed["subtitles"]
  debug(downloadSubs)

  targetDir = feed["targetFolder"]
  debug(targetDir)

  titlePrependItemDate = feed["titlePrependItemDate"]
  debug("Prepending item date: " + str(titlePrependItemDate))

  feedItemList = feedparser.parse( rssUrl )

  if feedItemList.bozo == 1:
    print "Could not connect to link '" + rssUrl + "'."
    print feedItemList.bozo_exception
    continue

  if feedItemList.status >= 400:
    print "Could not connect to link '" + rssUrl + "'. Status code returned: " + feedItemList.status
    continue

  items = feedItemList.entries

  for item in items:

    link = item["link"]
    parsed = urlparse.urlparse(link)
    docId = urlparse.parse_qs(parsed.query)['documentId'][0]
    docUrl = 'http://www.ardmediathek.de/play/media/' + docId + '?devicetype=pc&features=flash'

    #already downloaded?
    if feedId in myDownloadedFeedItemsDatabase and docId in myDownloadedFeedItemsDatabase[feedId]:
      continue

    year = item["date_parsed"][0];
    month = item["date_parsed"][1];
    day = item["date_parsed"][2];
    itemDate = datetime.date(item["date_parsed"][0], item["date_parsed"][1], item["date_parsed"][2])

    title = item["title"]

    if excludeFeedBasedOnTitle(feed, title):
      continue

    title = filterTitle(feed, title)
    debug(u"Filtered title to '" + title + "'")

    try:
      response = urlopen(docUrl)
    except IOError as e:
      print "Could not connect to link '" + docUrl + "'"
      print e
      continue

    if 'http://www.ardmediathek.de/-/stoerung' == response.geturl() or response.getcode() >= 400:
      print docUrl
      print "Could not get item with title '" + title + "'. Got redirected to '" + response.geturl() + "'. Status code is " + response.getcode() + ". This is probably because the item is still in the RSS feed, but not available anymore."
      continue

    html = response.read()

    try:
      media = json.loads(html)
    except ValueError as e:
      print e
      print "Could not get item with title '" + title + "'. Original item link is '" + link + "' and parsed docId[0] is '" + docId[0] + "', but html response from '" + docUrl + "' was '" + html + "'"
      continue

    if '_mediaArray' not in media or len(media["_mediaArray"]) < 2:
      print "Skipping " + title + " because it seems it does not have any mediafiles or none that we support"
      continue
    mediaLinks = media["_mediaArray"][1]["_mediaStreamArray"]

    downloadQuality = quality

    #get best quality?
    if downloadQuality == -1:
      downloadQuality = 0
      for mediaLink in mediaLinks:
        if mediaLink["_quality"] > downloadQuality and '_stream' in mediaLink:
          downloadQuality = mediaLink["_quality"]
    debug("Downloading quality " + str(downloadQuality))

    downloadedSomething = 0

    for mediaLink in mediaLinks:
      if downloadQuality != mediaLink["_quality"]:
        continue

      stream = mediaLink["_stream"]
      mediaURL = ""
      #check if the selected quality has two stream urls
      if type(stream) is list or type(stream) is tuple:
        if len(stream) > 1:
          debug("We have " + str(len(stream)) + " streams. Will download 2nd")
          mediaURL = stream[1]
        else:
          debug("We have only one stream in the list. Will download it")
          mediaURL = stream[0]
      else:
        mediaURL = stream
        debug("We have only one stream. Will download it")

      fileName = "".join([x if x.isalnum() or x in "- " else "" for x in title])

      if titlePrependItemDate == 1:
        fileName = str(itemDate) + " - " + fileName

      try:
        fullFileName = targetDir + fileName + ".mp4"
        if (os.path.isfile(fullFileName)) == True:
          print u"Skipping file '" + fullFileName + "' cause it already exists"
          continue
        urlretrieve(mediaURL, fullFileName)
      except IOError as e:
        print "Could not connect to link '" + mediaURL + "'"
        print e
        continue
      if response.getcode() >= 400:
        print mediaURL
        print "Could not get item with title '" + title + "'. Status code is " + response.getcode()
        continue

      downloadedSomething = 1

      markDocIdDownloaded(feedId, docId)

      print "Downloaded '" + title + "'"

      #download subtitles
      try:
        if downloadSubs and '_subtitleUrl' in media and len(media["_subtitleUrl"]) > 0:
          offset = 0
          if '_subtitleOffset' in media:
            offset = media["_subtitleOffset"]

          subtitleURL = media["_subtitleUrl"]
          
          urlretrieve(subtitleURL, targetDir + fileName + "_subtitleOffset_" + str(offset) + ".xml")
          if response.getcode() >= 400:
             print subtitleURL
             print "Could not get the subtitles for item with title '" + title + "'. Status code is " + response.getcode()
             continue

      except Exception as e:
        #print and resume with download
        print e
        print subtitleURL

    #check whether we download something
    if downloadedSomething == 0:
      print "Could not download '" + title + "' because of an error or nothing matching your quality selection"



