import sys
import xbmcgui
import xbmcplugin
import urllib
import urlparse
from resources.lib.f1tv import api

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])
_api = api.api()

def build_url(query):
    return base_url + '?' + urllib.urlencode(query)

def run():
    mode = args.get('mode', None)
    if mode is None:
        xbmcplugin.setContent(addon_handle, 'videos')
        data = _api.getUpcoming()
        for race in data:
            for episode in race['sessionoccurrence_urls']:
                if (episode['status'] == 'replay') or (episode['status'] == 'live'):
                    url = build_url({'mode': 'play',
                                     'episode': episode['channel_urls'][0]})
                    li = xbmcgui.ListItem(episode['session_name'], iconImage='DefaultVideo.png')
                    li.setProperty('IsPlayable', 'true')
                    li.setInfo('video', {'title': episode['session_name'],
                                                'genre': "Motorsport",
                                                'mediatype': 'video'})

                    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=False)
        xbmcplugin.endOfDirectory(addon_handle)
    elif mode[0] == 'play':
        episode = args.get('episode')
        p = _api.getStream(episode[0])
        play_item = xbmcgui.ListItem(path=p)
        xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)

