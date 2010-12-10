# PMS plugin framework
import re, string, datetime
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

####################################################################################################

VIDEO_PREFIX = "/video/hgtvca"

NAME = L('Title')

ART           = 'art-default.png'
ICON          = 'icon-default.jpg'

HGTV_SHOW_LIST = "http://www.hgtv.ca/ontv"

FEED_LIST    = "http://feeds.theplatform.com/ps/JSON/PortalService/2.2/getReleaseList?PID=W_qa_mi18Zxv8T8yFwmc8FIOolo_tp_g&startIndex=1&endIndex=500&query=contentCustomBoolean|Clip%20Type|%s&query=contentCustomText|Show|%s&sortField=airdate&sortDescending=true&field=airdate&field=author&field=description&field=length&field=PID&field=thumbnailURL&field=title&contentCustomField=title"

FEEDS_LIST    = "http://feeds.theplatform.com/ps/JSON/PortalService/2.2/getReleaseList?PID=HmHUZlCuIXO_ymAAPiwCpTCNZ3iIF1EG&startIndex=1&endIndex=500&query=contentCustomText|Show|%s&query=BitrateEqualOrGreaterThan|400000&query=BitrateLessThan|601000&&sortField=airdate&sortDescending=true&field=airdate&field=author&field=description&field=length&field=PID&field=thumbnailURL&field=title&contentCustomField=title"


DIRECT_FEED = "http://release.theplatform.com/content.select?format=SMIL&pid=%s&UserName=Unknown&Embedded=True&Portal=HGTV&TrackBrowser=True&Tracking=True&TrackLocation=True"

####################################################################################################

def Start():
    Plugin.AddPrefixHandler(VIDEO_PREFIX, MainMenu, L('VideoTitle'), ICON, ART)

    Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    MediaContainer.art = R(ART)
    MediaContainer.title1 = NAME
    DirectoryItem.thumb = R(ICON)


####################################################################################################
def MainMenu():
    dir = MediaContainer(viewGroup="List")
    dir.Append(Function(DirectoryItem(ShowsPage, "Shows A-F"), pageUrl = HGTV_SHOW_LIST, showtime='//ul[@id="AF"]/li/a'))
    dir.Append(Function(DirectoryItem(ShowsPage, "Shows G-L"), pageUrl = HGTV_SHOW_LIST, showtime='//ul[@id="GL"]/li/a'))
    dir.Append(Function(DirectoryItem(ShowsPage, "Shows M-Z"), pageUrl = HGTV_SHOW_LIST, showtime='//ul[@id="MZ"]/li/a'))
    return dir
    
####################################################################################################
def VideoPlayer(sender, pid):
    videosmil = HTTP.Request(DIRECT_FEED % pid)
    player = videosmil.split("ref src")
    player = player[2].split('"')
    if ".mp4" in player[1]:
        player = player[1].replace(".mp4", "")
        clip = player.split(";")
        clip = "mp4:" + clip[4]
    else:
        player = player[1].replace(".flv", "")
        clip = player.split(";")
        clip = clip[4]
    #Log(player)
    #Log(clip)
    return Redirect(RTMPVideoItem(player, clip))
    
####################################################################################################
def VideosPage(sender, showname):
    dir = MediaContainer(title2=sender.itemTitle, viewGroup="InfoList")
    pageUrl = FEEDS_LIST % (showname)
    feeds = JSON.ObjectFromURL(pageUrl)
    Log(feeds)
    for item in feeds['items']:
        title = item['title']
        pid = item['PID']
        summary =  item['description'].replace('In Full:', '')
        duration = item['length']
        thumb = item['thumbnailURL']
        airdate = int(item['airdate'])/1000
        subtitle = 'Originally Aired: ' + datetime.datetime.fromtimestamp(airdate).strftime('%a %b %d, %Y')
        dir.Append(Function(VideoItem(VideoPlayer, title=title, subtitle=subtitle, summary=summary, thumb=thumb, duration=duration), pid=pid))
    return dir
    
#def ClipsPage(sender, showname):
    #dir = MediaContainer(title2=sender.itemTitle, viewGroup="InfoList")
    #dir.Append(Function(DirectoryItem(VideosPage, "Full Episodes"), clips="episode", showname=showname))
    #dir.Append(Function(DirectoryItem(VideosPage, "Clips"), clips="", showname=showname))
    #return dir
    
####################################################################################################
def ShowsPage(sender, pageUrl, showtime):
    dir = MediaContainer(title2=sender.itemTitle, viewGroup="List")
    content = XML.ElementFromURL(pageUrl, True)
    for item in content.xpath(showtime):
        title = item.text
        thumb = "" #item.get('src')
        showname = title
        if "American Dad" in showname or "Entertainment Tonight" in showname or "The Simpsons" in showname:
            continue             ### NO VIDEOS FOR THESE SHOWS
        showname = showname.replace(' ', '%20').replace('&', '%26')  ### FORMATTING FIX
        Log(showname)
        dir.Append(Function(DirectoryItem(VideosPage, title, thumb=thumb), showname=showname))
    return dir