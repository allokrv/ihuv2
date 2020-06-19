# ihuv2 - I Hate Your Videos 2.0
Small script to dislike or like entire Youtube Channels.
You can also download basic data, a "snippet", about every Video that's being processed.
You will need a Google Project API Key and Client Secret File, 
the script will guide you through how to get them when you need them.


## The Google Project
All this Key and Secret jazz is gonna be available here: https://console.developers.google.com/
You're gonna have to create a Projekt; Basically a few clicks and coming up with a stupid name.

`Everything I'm explaining here will be prompted by the script, no need to read this if you just wanna get it set up.`

At some point the script will ask for an API Key and a "client_secret.json" both are found here:
https://console.developers.google.com/apis/credentials ; At the top's a button "Create Credentials"

After that (or before if that tickles your pickle) you're gonna have to enable the Youtube API Access for your project
simply click enable here: https://console.developers.google.com/apis/library/youtube.googleapis.com

## Settings.json
```
{	"get snippet of single videos": 	    false,  //get info about the video with the passed id
	"get snippet of every video": 		    false,  //get info about every video in the uploads playlist
	"go to channel after single video":         true,   //after the video get the channel info
	"get all uploads of channel": 		    true,   //after channel info get the uploads playlist
	"ratingmode":				    "skip", //rate the video(s) (or skip it)
	"mode_comment": "mode can be like/dislike/skip"        }
```

## Usage
It's rather simple you just run the Script with a Video-ID or a Channel-ID as argument

Example: "`python ihuv2.py 6E5m_XtCX3c`" (from: https://www.youtube.com/watch?v=6E5m_XtCX3c)

You're gonna be asked if you really wanna like/dislike the few thousand Videos you just put it

So even a messed up json should worst case lead to a crash and re-download



###### This is a small private project which may or may not be further maintained or outdated
