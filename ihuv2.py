import os
import sys
import json

import googleapiclient.discovery
import jsbeautifier

import ihuvapi
import requests


def get_video_info(vId, pl=False):
    part = "snippet"
    r = requests.get(f"https://www.googleapis.com/youtube/v3/videos?part={part}&id={vId}&key={ihuvapi.get_api_key()}")
    response = json.loads(r.content)
    if r.status_code != 200:
        print("[WARNING] Error in api: ")
        print(f"{response['error']['code']}: {response['error']['message']}")
        print("Possible Fix: go to https://console.developers.google.com/apis/library/youtube.googleapis.com "
              "and enable the Youtube API!")
        return False
    dbr = jsbeautifier.beautify(json.dumps(response))
    if len(response['items']) == 0:
        print("[ERROR] Invalid Video ID passed in ihuv2.py>get_video_info")
        return False
    print(f"<Response [{r.status_code}]> - {response['items'][0]['snippet']['title']}")

    # download if specified
    if (pl and ihuvapi.ihuv_settings.get_playlist_video_snippet) \
            or (not pl and ihuvapi.ihuv_settings.get_single_video_snippet):
        items = response['items'][0]
        path = f"results/{items['snippet']['channelTitle']}"
        if not os.path.exists("results"):
            os.mkdir("results")
        if not os.path.exists(path):
            os.mkdir(path)

        with open(path + f"/{vId}.json", "w") as file:
            file.write(jsbeautifier.beautify(json.dumps(response)))

    return response


def get_uploads(cId):
    part = "contentDetails"
    r = requests.get(f"https://www.googleapis.com/youtube/v3/channels?part={part}&id={cId}&key={ihuvapi.get_api_key()}")
    response = json.loads(r.content)
    if len(response['items']) == 0:
        print("[ERROR] Invalid Channel ID passed in ihuv2.py>get_uploads")
        return False
    plId = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    print(f"[SUCCESS] Found uploads playlist with id: {plId}")
    return plId


def get_all_uploads(plId):
    part = "contentDetails"
    APIKEY = ihuvapi.get_api_key()
    print("Trying to fetch playlist")
    r = requests.get(f"https://www.googleapis.com/youtube/v3/playlistItems" +
                     f"?part={part}" +
                     f"&maxResults=9999" +
                     f"&playlistId={plId}" +
                     f"&key={APIKEY}")

    vAmount = json.loads(r.content)['pageInfo']['totalResults']

    test = input(f"[YOUTUBE LIMITS RATINGS TO ~150 PER DAY!!!] Found {vAmount} videos in playlist.\n"
                 f"Starting in rating-mode '{ihuvapi.ihuv_settings.mode}', continue? y/n/c(chance) ~")
    if test == "c":
        test = input("Like / Dislike / Skip ? ~")
        test = test.strip().lower()
        if test in ["like", "dislike", "skip"]:
            input(f"Setting mode to {test}. Enter to continue ~")
            ihuvapi.ihuv_settings.mode = test
        else:
            print("[IDIOT] Why are you torturing me ?!")
            exit(1)

    elif test == "n":
        print("Canceling..")
        exit(0)
    if r.status_code != 200:
        print("[FATAL] Something went wrong fetching the playlist")
        print(jsbeautifier.beautify(json.dumps(json.loads(r))))
        exit(1)

    def run_pl(pageToken="00"):
        if pageToken != "00":
            _r = requests.get(f"https://www.googleapis.com/youtube/v3/playlistItems" +
                              f"?part={part}" +
                              f"&maxResults=9999" +
                              f"&playlistId={plId}" +
                              f"&pageToken={pageToken}" +
                              f"&key={APIKEY}")
        else:
            _r = r

        response = json.loads(_r.content)

        youtube = None
        mode = ihuvapi.ihuv_settings.mode
        if mode != "skip":
            youtube = googleapiclient.discovery.build(
                "youtube", "v3", credentials=ihuvapi.ihuv_credentials.creds)
            if youtube == "None":
                print("[FATAL] Something went horribly wrong.. sorry")
                exit(1)

        # For each video... // CODE HERE
        for video in response['items']:
            vId = video['contentDetails']['videoId']
            get_video_info(vId, pl=True)
            if mode != "skip":
                if mode == "like":
                    print("Liking..")
                    request = youtube.videos().rate(
                        id=vId,
                        rating="like"
                    )
                elif mode == "dislike":
                    print("Disliking..")
                    request = youtube.videos().rate(
                        id=vId,
                        rating="dislike"
                    )
                else:
                    print("[FATAL] Wrong parameter in settings.json > mode")
                    exit(1)

                try:
                    request.execute()
                except (Exception):
                    print("[ERROR] Error while rating Video!")
                    continue
                print("success!\n")


        try:
            if _r['nextPageToken']:
                run_pl(response['nextPageToken'])
        except Exception:
            pass
    run_pl("00")
    return True


def main():
    passed_arg = sys.argv[1]
    if len(passed_arg) == 11:
        vr = get_video_info(passed_arg)
        try:
            vr = vr['items'][0]
        except (Exception):
            print("[CRITICAL] Error getting Video Info, did you configure your "
                  "Google project to have Access to the Youtube API ?")
            exit(1)
        if not vr:
            print("[FATAL] Error while getting Video")
            exit(1)
        if ihuvapi.ihuv_settings.lookup_channel_after_video:
            print(f"[SUCCESS] Channel: {vr['snippet']['channelTitle']} ({vr['snippet']['channelId']})")
            ur = get_uploads(vr['snippet']['channelId'])
            if not ur:
                print("[FATAL] Something went wrong while looking up uploads playlist!")
                exit(1)
            if ihuvapi.ihuv_settings.get_all_channel_uploads:
                get_all_uploads(ur)

    elif len(passed_arg) == 24:
        vr = get_uploads(passed_arg)
        if not vr:
            print("[FATAL] Error while getting Uploads")
            exit(1)
        get_all_uploads(vr)

    else:
        print("What did you just try?!")
        exit(1)

    print("done.")
    exit(0)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Expected 1 argument as string: YoutubeVideoID/YoutubeChannelID")
        exit(1)
        ihuvapi.init(sys.argv[1], True)
    else:
        ihuvapi.init(sys.argv[1])
