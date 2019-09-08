import sys
import xbmcgui
import xbmcplugin
from resources.lib.f1tv import api
addon_handle = int(sys.argv[1])



def run():
    xbmcplugin.setContent(addon_handle, 'movies')
    _api = api.api()
    url = 'http://localhost/some_video.mkv'
    li = xbmcgui.ListItem('My First Video!', iconImage='DefaultVideo.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

    xbmcplugin.endOfDirectory(addon_handle)