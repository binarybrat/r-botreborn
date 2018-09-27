# R-BotReborn
## A simple python discord bot that displays Reddit contents in discord

### Usage

`python3 rbotreborn.py`

Current Commands:

*gets posts by hot*
* -r [subreddit] [amount of posts to randomly iterate through (optional)] **- gets image/text etc based posts**
* -ri [subreddit] [amount of posts...] **- gets image-based posts only (gif, video etc)**
* -rt [subreddit] [amount of posts...] **- gets text-based posts only (reddit or links)**
* -rc [subreddit] [amount of comments to grab] **- gets a post (image/text) and displays x amount of top level comments**
* -ru [reddit post URL] [amount of comments to grab] **- gets a post from a Reddit URL, displays x amount top-level of comments (opt)**
* -rcl [amount of comments to grab] **-get x amount of comments from last post in channel**
### Installing

**Requirements:**

`pip3 install -r requirements.txt`

Basically you need:
* discord.py
* praw
* sumy

sumy requires you to download some stuff

`python3 -c "import nltk; nltk.download('punkt')"`


#### Config File (config.ini)

* Under discord.cred need your bot token
* Under reddit.cred need to add your reddit api stuff. This is used by PRAW.
* Under Gfycat need to add Gfycat API Credentials. 

#### Hosting
Works well on a Free Tier AWS EC2 instance

#### Note: this was just a little project I worked on while learning Python, so the code quality could be very poor and is very messy. It "works"
