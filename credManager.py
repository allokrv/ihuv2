import os
import json

import google.oauth2.credentials
import jsbeautifier


# better than saving an empty document and getting read errors later lol
import requests
from google_auth_oauthlib.flow import InstalledAppFlow


def store_keys(at="", rt="", api=""):
    # only use given params
    with open("KEYS", "r") as kfile:
        _d = kfile.read()
    _api, _at, _rt = _d.split("\n")
    if at == "":
        at = _at
    if rt == "":
        rt = rt
    if api == "":
        api = _api
    # storing keys in file
    print("Refreshing KEYS file..")
    data = [api, at, rt]
    with open("KEYS", "w") as kfile:
        kfile.write("\n".join(data))


# just to avoid some errors that will prolly never occur
def create_dummy_keys_file():
    with open("KEYS", "w") as kfile:
        kfile.write("PUTyourAPIkeyHERE\n" +
                    "LEAVEmeHERE\n" +
                    "MEtooWEREgonnaBEreplaced")


class AppCredentials:
    credset = False
    at = None
    rt = None
    api = None
    secret = None
    creds = None
    scope = "https://www.googleapis.com/auth/youtube"

    # set session keys
    def set_keys(self, access, refresh):
        if access == "LEAVEmeHERE" and refresh == "MEtooWEREgonnaBEreplaced":
            print("Wrong keys passed")
            return
        elif access == "LEAVEmeHERE":
            self.rt = refresh
        elif refresh == "MEtooWEREgonnaBEreplaced":
            self.creds = google.oauth2.credentials.Credentials(access)
            self.credset = True
            self.at = access
        else:
            self.creds = google.oauth2.credentials.Credentials(access)
            self.credset = True
            self.at = access
            self.rt = refresh

    def debug_print(self):
        print("\n------------------DEBUG------------------")
        print("Access Token: " + str(self.at))
        print("Refresh Token: " + str(self.rt))
        print("API Token: " + str(self.api))
        print("Credentials: " + str(self.creds))
        s_dump = jsbeautifier.beautify(json.dumps(self.secret))
        print("Secret: " + s_dump)

    # checks if any important attributes are null
    def ready(self):
        if None in [self.at, self.rt, self.api, self.secret, self.creds]:
            print("[WARNING] Credentials not set up yet!")
            # self.debug_print(self)
            self.init_creds(self)
            return self.ready(self)
        else:
            print("[SUCCESS] Credentials ready!")
            return True

    # set session credentials for auth
    def set_credentials(self, credentials):
        self.credset = True
        print("Setting session-credentials..")
        self.creds = credentials
        self.at = credentials.token
        self.rt = credentials.refresh_token
        store_keys(at=self.at, rt=self.rt, api=self.api)

    def set_api_key(self, api_key):
        print("Setting session API-Key..")
        self.api = api_key

    # get client secret file
    def get_client_secret(self):
        if os.path.isfile("client_secret.json"):
            print("Loading secret file..")
            with open("client_secret.json", "r") as cs:
                data = cs.read()
                # parsing json data from file into _data
                _data = json.loads(data)
            self.secret = _data['installed']
            return True
        else:
            print("Couldn't find a 'client_secret.json' please download, rename and put into ihuv2 folder\nYou can " +
                  "download / create a client_secret.json here: https://console.developers.google.com/apis/credentials")
            print("At the top you should see a 'Create Credentials' button, create a Client-ID as Desktop Application\n"
                  "Download that file, it's gonna have a long, weird name so just rename it to 'client_secret.json'\n"
                  "and put it into the main ihuv folder.")

            print("The Secret file is necessary for ihuv2 to work!")
            exit(1)
            return False

    def init_creds(self):
        # Use the client_secret.json file to identify the application requesting
        # authorization. The client ID (from that file) and access scopes are required.
        print("Creating flow..")
        flow = InstalledAppFlow.from_client_secrets_file("client_secret.json", [self.scope])

        # set redirect uri for automatic token accept
        flow.redirect_uri = self.secret['redirect_uris'][0]

        # get credentials (opens a browser with google sign in)
        print("Opening a browser to get Authorization from user")
        credentials = flow.run_local_server(host='localhost',
                                           port=8080,
                                           authorization_prompt_message='Please visit this URL: {url}',
                                           success_message='Authorization granted, haxored Kappa\n'
                                                           'You can now close this window',
                                           open_browser=True)

        if credentials is not None:
            print("[SUCCESS] Authorization flow complete!")
            self.set_credentials(self, credentials)

    # reading keys from file
    def get_key_files(self):
        if os.path.isfile("KEYS"):
            print("Loading Keys..")
            with open("KEYS", "r") as kfile:
                data = kfile.read()
            if not data:
                print("[WARNING] Something went wrong with your KEYS file, attempting to fix..")
                create_dummy_keys_file()
                with open("KEYS", "r") as kfile:
                    data = kfile.read()

            _data = data.split()
            if _data[0] == "PUTyourAPIkeyHERE":
                print("Please enter an API Key:" +
                      "\n*You can get an API key here: https://console.developers.google.com/apis/credentials")
                print("At the top you should see a 'Create Credentials' button, create an API Key")
                key = input("Key~")
                if len(key) != 39:
                    print("[ERROR] Invalid Key entered, you can specify it in the \"KEYS\" file in your ihuv2 folder "
                          "too.")
                    return False
                else:
                    _data[0] = key
                    print("[SUCCESS] Saving key to file..")
                    with open("KEYS", "w") as kfile:
                        kfile.write("\n".join(_data))

            self.set_api_key(self, _data[0])
            return True

        else:
            create_dummy_keys_file()
            self.get_key_files(self)

    # get new refreshToken
    def refresh_rt(self):
        print("Refreshing tokens..")
        authorization_url = "https://oauth2.googleapis.com/token"  # self.secret['auth_uri']
        params = {"grant_type": "refresh_token",
                  "client_id": self.secret['client_id'],
                  "client_secret": self.secret['client_secret'],
                  "refresh_token": self.rt}

        r = requests.post(authorization_url, data=params)
        _r = json.loads(r.content)
        if r.ok:
            print("[SUCCESS] Got new Token, saving..")
        else:
            print("[ERROR] Couldn't get new Access Token.")
            exit(1)
        print("Getting session Credentials")
        tcreds = google.oauth2.credentials.Credentials(_r['access_token'])
        print(tcreds)
        exit(0)
