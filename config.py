import configparser
import json

class Config:

    def __init__(self, config_file):
        config = configparser.ConfigParser()
        config.read(config_file)

        # now set values to the values in the config file

        self.discord_token = config.get('discord.cred', 'token', fallback=None)
        self.discord_server = config.get('discord.cred', 'server', fallback=None)

        # discord.bot

        self.bot_prefix = config.get('discord.bot', 'prefix', fallback=ConfigDefaults.box_prefix)
        self.bot_game = str(config.get('discord.bot', 'game', fallback=ConfigDefaults.server))
        self.nsfw_channels = json.loads(config.get('discord.bot', 'nsfwchannels', fallback=None))
        # reddit.cred

        self.r_client_id = config.get('reddit.cred', 'client_id', fallback=None)
        self.r_client_secret = config.get('reddit.cred', 'client_secret', fallback=None)
        self.r_user_agent = config.get('reddit.cred', 'user_agent', fallback=ConfigDefaults.r_user_agent)
        self.r_username = config.get('reddit.cred', 'username', fallback=None)
        self.r_password = config.get('reddit.cred', 'password', fallback=None)

        # reddit defaults

        self.r_comment_total_length = int(config.get('reddit.default', 'redditdiscordcommentlengthlimit', fallback=ConfigDefaults.r_comment_total_length))
        self.r_postcount = config.getint('reddit.default', 'postcount', fallback=ConfigDefaults.r_post_count)
        self.r_maxpostcount = config.getint('reddit.default', 'maxpostcount', fallback=ConfigDefaults.r_maxpostcount)
        self.r_ignore_users = json.loads(config.get('reddit.default', 'redditignoreusers', fallback=None))
        self.r_post_length_discord = int(config.get('reddit.default', 'redditdiscordpostlimit', fallback=ConfigDefaults.r_post_length_discord))
        self.r_skip_mod_posts = bool(config.get('reddit.default', 'skipmodposts', fallback=ConfigDefaults.r_skip_mod_posts))
        self.r_skip_stickied_posts = bool(config.get('reddit.default', 'skipstickedposts', fallback=ConfigDefaults.r_skip_stickied_posts))
        self.r_default_comment_count = int(config.get('reddit.default', 'default_comment_count', fallback=ConfigDefaults.r_default_comment_count))
        # gfycat
        self.r_gfycat_client_id = config.get('gfycat', 'client_id')
        self.r_gfycat_client_secret = config.get('gfycat', 'client_secret')



class ConfigDefaults:
    box_prefix = "-"
    server = "discord"
    r_user_agent = "rbotreborn_discord"
    r_post_count = 100
    r_maxpostcount = 1000
    r_post_length_discord = 1850
    r_skip_mod_posts = True
    r_skip_stickied_posts = True
    r_comment_total_length = 1200
    r_default_comment_count = 10

class UpdateConfig:

    def __init__(self, config_file):
        self.__config = configparser.ConfigParser()
        self.__config.read(config_file)
        self.__config_file = config_file

    def update_nsfw_channels(self, channel):
        nsfw_channels = json.loads(self.__config.get('discord.bot', 'nsfwchannels', fallback=None))
        message = None
        if channel not in nsfw_channels:
            nsfw_channels.append(channel)

            nsfw_c = json.dumps(nsfw_channels)
            self.__config['discord.bot']['nsfwchannels'] = nsfw_c

            with open(self.__config_file, 'w') as configfile:
                self.__config.write(configfile)
                configfile.close()
        else:
            message = "This channel is already set as a NSFW channel!"
        return nsfw_channels, message

