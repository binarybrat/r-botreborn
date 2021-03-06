import configparser
import json
import collections


def makehash():
    return collections.defaultdict(makehash)


class Config:
    """
    Loads configurations from the config file
    """
    def __init__(self, config_file):
        config = configparser.ConfigParser()
        config.read(config_file)

        # now set values to the values in the config file

        self.discord_token = config.get('discord.cred', 'token', fallback=None)

        # discord.bot

        self.bot_prefix = config.get('discord.bot', 'prefix', fallback=ConfigDefaults.box_prefix)
        self.bot_game = str(config.get('discord.bot', 'game', fallback=ConfigDefaults.game))
        self.nsfw_channels = makehash()  # so we don't get index problems
        self.nsfw_channels = json.loads(config.get('discord.bot', 'nsfwchannels', fallback=None))
        self.version = ConfigDefaults.version
        # reddit.cred

        self.r_client_id = config.get('reddit.cred', 'client_id', fallback=None)
        self.r_client_secret = config.get('reddit.cred', 'client_secret', fallback=None)
        self.r_user_agent = ConfigDefaults.r_user_agent
        self.r_username = config.get('reddit.cred', 'username', fallback=None)
        self.r_password = config.get('reddit.cred', 'password', fallback=None)

        # reddit defaults

        self.r_postcount = config.getint('reddit.default', 'post_count', fallback=ConfigDefaults.r_post_count)
        self.r_maxpostcount = config.getint('reddit.default', 'max_post_count', fallback=ConfigDefaults.r_maxpostcount)
        self.r_ignore_users = json.loads(config.get('reddit.default', 'ignore_users', fallback=ConfigDefaults.ignore_users))
        self.r_skip_mod_posts = config.get('reddit.default', 'skip_mod_posts', fallback=ConfigDefaults.r_skip_mod_posts)
        self.r_skip_stickied_posts = config.get('reddit.default', 'skip_stickied_posts', fallback=ConfigDefaults.r_skip_stickied_posts)
        self.r_skip_stickied_comments = config.get('reddit.default', 'skip_stickied_comments', fallback=ConfigDefaults.r_skip_sticked_comments)

        self.r_skip_stickied_comments = False if self.r_skip_stickied_comments.lower() == 'false' else True
        self.r_skip_stickied_posts = False if self.r_skip_stickied_posts.lower() == "false" else True
        self.r_skip_mod_posts = False if self.r_skip_mod_posts.lower() == "false" else True

        self.page_comment_num = int(config.get('reddit.default', 'comments_per_page', fallback=ConfigDefaults.comments_per_page))

        self.r_last_post_url = makehash()
        self.comment_messages = makehash()

        # gfycat
        self.gfycat_client_id = config.get('gfycat', 'client_id')
        self.gfycat_client_secret = config.get('gfycat', 'client_secret')

        # sumy
        self.enable_sumy = config.get('sumy', 'enabled', fallback=ConfigDefaults.sumy_enabled)

        if self.enable_sumy.lower() == "false":
            self.enable_sumy = False
        else:
            self.enable_sumy = True

        self.sumy_lang = str(config.get('sumy', 'language', fallback=ConfigDefaults.sumy_lang))
        self.sumy_num_sentences = str(config.get('sumy', 'number_of_sentences', fallback=ConfigDefaults.sumy_num_sentences))


class ConfigDefaults:
    """
    Default/fallback Configurations if something goes wrong
    Doesn't account for missing credentials
    """
    version = "0.3.3"
    box_prefix = "-"
    game = "type -help"
    r_user_agent = f"r-botreborn v{version} (discord bot)"
    r_post_count = 15
    r_maxpostcount = 500
    r_skip_mod_posts = "True"
    r_skip_stickied_posts = "True"
    r_skip_sticked_comments = "True"
    sumy_lang = 'english'
    sumy_num_sentences = 2
    sumy_enabled = "True"
    comments_per_page = 3

    ignore_users = ["AutoModerator"]


class UpdateConfig:

    def __init__(self, config_file):
        self.__config = configparser.ConfigParser()
        self.__config.read(config_file)
        self.__config_file = config_file

    def remove_nsfw_channels(self, server_id, channel_id):

        nsfw_servers = json.loads(self.__config.get('discord.bot', 'nsfwchannels', fallback=None))
        message = None
        if server_id in nsfw_servers.keys():
            if channel_id in nsfw_servers[server_id]:
                nsfw_servers[server_id].remove(channel_id)
            else:
                message = "This channel is not set as a NSFW channel!"
        else:
            message = "This channel is not set as a NSFW channel!"

        nsfw_c = json.dumps(nsfw_servers)
        self.__config['discord.bot']['nsfwchannels'] = nsfw_c

        with open(self.__config_file, 'w') as configfile:
            self.__config.write(configfile)
            configfile.close()

        return nsfw_servers, message

    def add_nsfw_channels(self, server_id, channel_id):

        nsfw_servers = json.loads(self.__config.get('discord.bot', 'nsfwchannels', fallback=None))
        message = None

        # {server:[that servers nsfw channels], server:[another servers nsfw channels]}
        if server_id in nsfw_servers.keys():
            if channel_id not in nsfw_servers[server_id]:
                nsfw_servers[server_id].append(channel_id)
            else:
                message = "This channel is already set as a NSFW channel!"
        else:
            nsfw_servers[server_id] = [channel_id]

        nsfw_c = json.dumps(nsfw_servers)
        self.__config['discord.bot']['nsfwchannels'] = nsfw_c

        with open(self.__config_file, 'w') as configfile:
            self.__config.write(configfile)
            configfile.close()

        return nsfw_servers, message


