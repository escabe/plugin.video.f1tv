import requests
import json
import xbmc
import xbmcaddon
import os.path
import pyjwt
import time

__addon__ = xbmcaddon.Addon()
__profile__ = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode("utf-8")


class api:

    def saveAuth(self):
        fp = open(__profile__ + 'auth.json','w')
        json.dump(self.auth, fp)
        fp.close()

    def getJWTToken(self):
        headers = {'Content-Type': 'application/json'}
        body = {'identity_provider_url': '/api/identity-providers/iden_732298a17f9c458890a1877880d140f3/',
                'access_token': self.auth['subscriptionToken']}
        r = self.session.post('https://f1tv.formula1.com/api/social-authenticate/',
                              headers=headers, data=json.dumps(body))
        if r.ok:
            token = r.json()['token']
            self.auth['jwttoken'] = token
            info = pyjwt.decode(token, verify=False)
            self.auth['jwtexp'] = info['exp']
        else:
            raise ValueError('social-authenticate failed.')

    def login(self):
        headers = {'Content-Type': 'application/json',
                   'apikey': 'fCUCjWrKPu9ylJwRAv8BpGLEgiAuThx7'}
        body = {'Login': __addon__.getSetting('username'),
                'Password': __addon__.getSetting('password'),
                'DistributionChannel': 'd861e38f-05ea-4063-8776-a7e2b6d885a4'}
        r = self.session.post('https://api.formula1.com/v2/account/subscriber/authenticate/by-password',
                              headers=headers, data=json.dumps(body))
        if r.ok and 'Fault' not in r.json():
            self.auth['subscriptionToken'] = r.json()["data"]["subscriptionToken"]
            self.getJWTToken()
            self.saveAuth()
        else:
            raise ValueError('CreateSession failed.')

    def getUpcoming(self):
        headers = {'Content-Type': 'application/json',
                   'Authentication': 'JWT '+self.auth['jwttoken']}
        r = self.session.get('https://f1tv.formula1.com/api/event-occurrence/current-season-upcoming/?fields_to_expand=sessionoccurrence_urls,sessionoccurrence_urls__image_urls&fields=sessionoccurrence_urls,sessionoccurrence_urls__status,sessionoccurrence_urls__session_name,sessionoccurrence_urls__channel_urls,sessionoccurrence_urls__image_urls,sessionoccurrence_urls__image_urls__url',
                             headers=headers)
        if (r.ok):
            return r.json()['objects']
        else:
            raise ValueError('Unable to retrieve upcoming list.')

    def getStream(self, episode):
        headers = {'Content-Type': 'application/json',
                   'Authorization': 'JWT '+self.auth['jwttoken']}
        body = {'channel_url': episode}
        r = self.session.post('https://f1tv.formula1.com/api/viewings/', headers=headers, data=json.dumps(body))
        if r.ok:
            return r.json()['tokenised_url']
        else:
            raise ValueError('viewings failed.')

    def __init__(self):
        self.session = requests.session()
        # Try loading credentials from disk
        if os.path.exists(__profile__+'auth.json'):
            fp = open(__profile__+'auth.json')
            self.auth = json.load(fp)
            fp.close()
            # Check for expired token
            if self.auth['jwtexp'] < time.time():
                self.login()
        else:
            # No auth saved, login
            self.auth = {}
            self.login()
