# R-BotReborn
A simple discord bot that displays reddit content in discord.

## Features Outline
* Grab hot posts from any subreddit
* Get comments for the posts
* Display those posts and comments in nicely formatted interactive discord embeds!

* Configurable NSFW channel permissions

**NOTE: Currently there are no permissions with this bot (like allowing/disallowing discord users to use certain functions).**
#### Screenshot Example

![Post + Comments](screenshots/example.png "Post + Comments Example")

[(post in screenshot)](https://reddit.com/r/pics/comments/6v6dqp/amazing_photo_of_totality_in_oregon_by/)

## Installation

Note: exact commands may differ between systems

#### Requirements:
* Python 3 *(preferably 3.6, Python 3.7 is currently not supported by discord.py)*
* Modules listed in requirements.txt (instructions below)
* Reddit API access (instructions below)
* Gfycat API access (instructions below)
* Discord API access (instructions below)

#### Instructions

Clone this Repository (or download release from the releases tab)
```
git clone https://github.com/colethedj/rbotreborn.git
```
Install Requirements
```
cd rbotreborn
pip3 install -r requirements.txt
```

Open config.ini in your favorite text editor. I'm using gedit here.

```
gedit config.ini
```

**Discord API**

Follow [these instructions](https://github.com/reactiflux/discord-irc/wiki/Creating-a-discord-bot-&-getting-a-token) to get a discord bot account and add it to your server. 


Add the bot token in config.ini (TOKEN NOT ID)

```
[discord.cred]
# token for discord API
token = TOKEN_HERE
```

**Reddit API**

Go to https://reddit.com/prefs/apps/ and create a new app.

Give it a name. For the redirect uri you can make it go to this repository (or wherever)

Copy the id (below the 'personal use script' text) and the secret and paste it in the config.ini file

```
[reddit.cred]
client_id =  CLIENT_ID_HERE
client_secret = CLIENT_SECRET_HERE
```

**Gfycat API**

This is used to convert videos etc into gifs so they are viewable in a discord embed (as videos and other formats are not supported by discord embeds)

Sign in with your gfycat account [here](https://developers.gfycat.com/signup/) (create an account if you don't have one already)

Fill in the key request form (again app URL can just go to this respository)

Paste the API credientials you recieved in your email in the config.ini file

```
[gfycat]
client_id = CLIENT_ID_HERE
client_secret = CLIENT_SECRET_HERE
```

Edit any other values in the config.ini file to suit you.


**Launch!**

```
python3 rbotreborn.py
```
```
type <chosen prefix>help in the chat to display available commands
```

**Note: You may have to add a role to the bot in your server to give enough permissions (read, send, delete messages and reactions)**


## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/colethedj/rbotreborn/blob/master/LICENSE) file for details

## Current Issues

See the [Issues tab](https://github.com/colethedj/rbotreborn/issues) for latest known issues and fixes.

but basically some things I'm aware of:

* No Permissions to control what functions users can use
* If a url has "youtube" or other keywords I used in my lazy-defined urltype handler in the url when it isn't, say, a youtube link then it will still pass it on to gfycat and crash (so gfycat load looks like it's going on forever)

## Other info and Q&A

Q: Why is it "reborn"

A: I had another earlier "test" bot for this idea named "R-BOT" (reddit-bot) and I just wanted to rewrite it so named it RbotReborn


#### Note: This was my first python (and github) project I've worked on. I've used this as a way to learn the python programming langauge. So excuse any 'bad code' (feel free to make improvements). 
