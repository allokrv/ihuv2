import os
import json
import ihuv2
import jsbeautifier
import credManager as cM


def get_api_key():
    return ihuv_credentials.api

class AppSettings:
    get_single_video_snippet = False
    get_playlist_video_snippet = False
    lookup_channel_after_video = True
    get_all_channel_uploads = True
    download = False
    dl_format = "mp4"
    mode = "skip"

    # applying settings from file
    def set_settings(self, single_snippet, playlist_snippet, lookup_channel, get_all, download, dl_format, mode):
        self.get_single_video_snippet = single_snippet
        self.get_playlist_video_snippet = playlist_snippet
        self.lookup_channel_after_video = lookup_channel
        self.get_all_channel_uploads = get_all
        self.download = download
        if dl_format in ["mp3", "mp4"]:
            self.dl_format = dl_format
        else:
            return False
        self.mode = mode
        if mode in ["skip", "like", "dislike"]:
            self.dl_format = dl_format
        else:
            return False

        return True

    # print all class vars
    def debug_print(self):
        print("\n------------------DEBUG------------------")
        print("Get Snippet: " + str(self.get_single_video_snippet))
        print("Get All Snippets: " + str(self.get_playlist_video_snippet))
        print("Go to Channel: " + str(self.lookup_channel_after_video))
        print("Get all Uploads: " + str(self.get_all_channel_uploads))
        print("Rating Mode: " + self.mode)

    # load settings from file
    def load_settings(self):
        print("Loading settings..")
        # does file exist ?
        if os.path.isfile("settings.json"):
            # opening file in read mode
            with open("settings.json", "r") as settings:
                data = settings.read()
                # parsing json data from file to _data
                _data = json.loads(data)
            print("[SUCCESS] Applying settings..")
            r = self.set_settings(self,
                                  _data['get snippet of single videos'],
                                  _data['get snippet of every video'],
                                  _data['go to channel after single video'],
                                  _data['get all uploads of channel'],
                                  _data['download videos'],
                                  _data['download format'],
                                  _data['ratingmode'])
            if r:
                return True
            else:
                print("settings.json is corrupted, please ensure the right parameters!")
                return False
        else:
            print("[FATAL] Did you really delete the settings file ?!")
            return False


def check_credentials():
    return ihuv_credentials.ready(ihuv_credentials)


def check_required_files():
    # check settings file
    rdy_settings = ihuv_settings.load_settings(ihuv_settings)
    # check key file
    rdy_keys = ihuv_credentials.get_key_files(ihuv_credentials)
    # check client_secret
    rdy_secret = ihuv_credentials.get_client_secret(ihuv_credentials)

    if not (rdy_keys and rdy_secret and rdy_settings):
        print("[FATAL] Files are not fully configured yet\n" +
              "Please check the 'KEYS' and 'client_secret' files for validity")
        return False
    else:
        return True


# load keys from file
def load_keys():
    with open("KEYS", "r") as kfile:
        _d = kfile.read()
    _api, _at, _rt = _d.split("\n")
    ihuv_credentials.set_keys(ihuv_credentials, _at, _rt)


ihuv_settings = AppSettings
ihuv_credentials = cM.AppCredentials


def init(id, dev=False):
    # check requirements
    rdy_files = check_required_files()
    load_keys()
    rdy_creds = check_credentials()

    if dev:
        ihuv_credentials.debug_print(ihuv_credentials)
        ihuv_settings.debug_print(ihuv_settings)

    if not (rdy_files and rdy_creds):
        print(f"Error, exiting.. files: {rdy_files} creds:{rdy_creds}")
        exit(1)
    else:
        print("_________________________________________________________________________")
        print("<==============| ihuv2 is set up! Continuing to Videos.. |==============>\n")

    ihuv2.main()
