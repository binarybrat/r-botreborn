# R-BotReborn
## A (very basic) discord bot written in Python 3 that displays Reddit posts in discord
Using discord.py

### Usage

`python3 rbotreborn.py`

Current Commands:
*gets posts by hot*
* -r [subreddit] [amount of posts to randomly iterate through (optional)] **- gets image/text etc based posts**
* -ri [subreddit] [amount of posts...] **- gets image-based posts only (gif, video etc)**
* -rt [subreddit] [amount of posts...] **- gets text-based posts only (reddit or links)**
* -rc [subreddit] [amount of comments to grab] **- gets a post (image/text) and displays x amount of top level comments**

### Installing

**Requirements:**
`pip3 install -r requirements.txt`

Basically you need:
* discord.py
* praw


#### Config File (config.ini)

* Under discord.cred need your bot token
* Under reddit.cred need to add your reddit credentials (including api keys). This is used by Praw.
* Under Gfycat need to add Gfycat API Credentials. 

### Current Issues:

**Probably Lots**
* Imgur links currently not supported yet (need to maybe a. use imgur api to grab image url or b. some time of parser)

#### Note: this was just a little project I worked on while learning Python, so the code quality could be very poor and is very messy. It "works"
