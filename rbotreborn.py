import discord
import asyncio
from discord.ext import commands
import praw
import logging
import config
from gfycat import Gfycat
from custom_embeds import *
from reddit import *
from exceptions import *
from processors import *
from commentmessage import *
from psutil import cpu_percent, virtual_memory
import datetime


Config = config.Config('config.ini')
bot = commands.Bot(command_prefix=Config.bot_prefix,
                   description=f'R-BotReborn v{Config.version} \n https://github.com/colethedj/r-botreborn')

Logger = logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


@bot.command(pass_context=True)
async def gif(ctx, url):
    """
    Create a gif from a URL via GfyCat
    """

    await bot.delete_message(ctx.message)
    processing_embed = GfycatLoadingEmbed(url)
    bot_message = await bot.send_message(ctx.message.channel, embed=processing_embed.get_embed())
    try:
        # # TODO: Rewrite this when handling already gfycat links.
        # if "gfycat.com" in url:
        #     post_gfycat = Gfycat(Config.gfycat_client_id, Config.gfycat_client_secret)
        #     # TODO: This may not work, test
        #     gfyjson = await post_gfycat.get_gfy_info(str(url)[19:(len(str(url)))])
        #     print(gfyjson)  # TODO: fails if starts with http://
        #     image_url = gfyjson['gfyItem']['max5mbGif']
        #     color = gfyjson['gfyItem']['color']
        # else:
        image_url, color = await gfycat_url_handler(url)
    except TypeError:
        pass
    except KeyError:
        pass
    if isinstance(image_url, GfycatErrorEmbed):
        await bot.edit_message(bot_message, embed=image_url.get_embed())
        return
    gfy_embed = GfycatEmbed()
    gfy_embed.create_embed(title="GIF", image=image_url, color=(int(color[1:], 16)) + 0x200, url=url, description=f"<@{ctx.message.author.id}>")
    await bot.edit_message(bot_message, embed=gfy_embed.get_embed())


@bot.command(pass_context=True, description="Get info about yourself")
async def me(ctx):
    """
    Give user info about user requesting the command
    """

    me_embed = discord.Embed(title=ctx.message.author.display_name if str(ctx.message.author.display_name) != ctx.message.author.name else discord.Embed.Empty,
                             colour=ctx.message.author.colour,
                             description=f"ID: {ctx.message.author.id}\n"
                                         f"Account Created {ctx.message.author.created_at.strftime('%d-%m-%Y at %H:%M:%S')} UTC")
    me_embed.set_author(name=ctx.message.author.name,
                        icon_url=ctx.message.author.avatar_url if ctx.message.author.avatar_url is not "" else ctx.message.author.default_avatar_url)

    me_embed.add_field(name="Joined at", value=f"{ctx.message.author.joined_at.strftime('%d-%m-%Y at %H:%M:%S')} UTC")
    me_embed.add_field(name="Status", value=str(ctx.message.author.status).title())
    me_embed.set_thumbnail(url=ctx.message.author.avatar_url if ctx.message.author.avatar_url is not "" else ctx.message.author.default_avatar_url)

    me_embed.add_field(name="Playing", value=ctx.message.author.game if ctx.message.author.game is not None else "Nothing")
    me_embed.add_field(name="Roles", value=', '.join(list(map(lambda y: y.name, list(filter(lambda x: x.name != "@everyone",ctx.message.author.roles))))), inline=False)
    await bot.send_message(ctx.message.channel, embed=me_embed)


@bot.command(pass_context=True, description="Display current channel info")
async def channel(ctx):
    """
    Display current channel info
    """
    channel_embed = discord.Embed(title=f"Channel Info for {ctx.message.channel.name}",
                                  colour=0x3498db,
                                  description=f"ID: {ctx.message.channel.id}\n"
                                              f"Created on "
                                              f"{ctx.message.channel.created_at.strftime('%d-%m-%Y at %H:%M:%S')} UTC")
    channel_embed.set_thumbnail(url=ctx.message.server.icon_url)
    channel_embed.add_field(name="NSFW Enabled", value=str(await check_nsfw(ctx)), inline=True)
    channel_embed.add_field(name="Type", value=str(ctx.message.channel.type).title(), inline=True)
    topic = ctx.message.channel.topic if ctx.message.channel.topic is not "" else "None"
    channel_embed.add_field(name="Topic", value=topic, inline=False)

    await bot.send_message(ctx.message.channel, embed=channel_embed)


@bot.command(pass_context=True, description="Display server info")
async def server(ctx):
    """
    Displays current server stats
    """
    server_embed = discord.Embed(description=f"ID: {ctx.message.server.id}\n "
                                             f"Created on "
                                             f"{ctx.message.server.created_at.strftime('%d-%m-%Y at %H:%M:%S')} UTC",
                                 colour=0x3498db)

    server_embed.set_author(name=ctx.message.server.name, icon_url=ctx.message.server.icon_url)
    server_embed.set_thumbnail(url=ctx.message.server.icon_url)
    server_embed.add_field(name=f"Members ({ctx.message.server.member_count})",
                           value=f"Online: {len(list(filter(lambda x: x.status is discord.Status.online,ctx.message.server.members)))}\n"
                                 f"Idle/DND: {len(list(filter(lambda x: x.status is discord.Status.idle or x.status is discord.Status.do_not_disturb,ctx.message.server.members)))}\n"
                                 f"Offline: {len(list(filter(lambda x: x.status is discord.Status.offline,ctx.message.server.members)))}")
    server_embed.add_field(name="Server Owner", value=ctx.message.server.owner)
    server_embed.add_field(name="Region", value=str(ctx.message.server.region).title())
    server_embed.add_field(name="Channels", value=str(len(list(filter(lambda y: y.type is discord.ChannelType.voice or y.type is discord.ChannelType.text, ctx.message.server.channels)))))
    server_embed.add_field(name="Roles", value=str(len(ctx.message.server.roles)))
    server_embed.add_field(name="Verification Level", value=str(ctx.message.server.verification_level).title())
    await bot.send_message(ctx.message.channel, embed=server_embed)


@bot.command(description="Displays system Status of the bot")
async def about():
    """
    Display system status of the bot
    """
    about_embed = discord.Embed(title="About", description=f"R-BotReborn v{Config.version} by colethedj#6071"                          
                                f"\n[Github](https://github.com/colethedj/r-botreborn)",
                                colour=0x3498db)

    about_embed.set_thumbnail(url='https://www.redditstatic.com/desktop2x/img/favicon/apple-icon-120x120.png')
    about_embed.add_field(name="System CPU Usage", value=f"{cpu_percent(interval=None)}%")
    about_embed.add_field(name="System Memory Usage", value=f"{virtual_memory().percent} %"
                          f"({'%.2f' % (((virtual_memory().percent/100) * virtual_memory().total)/1073741824)}GB/"
                          f"{'%.2f' % (virtual_memory().total/1073741824)}GB)")
    about_embed.add_field(name="Alive since", value=str(bot.uptime) + " UTC", inline=True)
    about_embed.add_field(name="Servers connected to", value=str(len(bot.servers)))
    about_embed.set_footer(text=f"For current server info use {Config.bot_prefix}server")
    await bot.say(embed=about_embed)


@bot.command(pass_context=True, description="Get comments from the last post")
async def rcl(ctx):
    """
    Displays comments for the last post in requested channel
    rcl = Reddit Comment Last
    """
    await bot.delete_message(ctx.message)
    if ctx.message.channel.id in Config.r_last_post_url[ctx.message.server.id]:
        loading_message = RedditLoadingEmbed()
        loading_message.create_embed(footer_text="Getting comments for the previous post",
                                     custom_message="Getting comments... This will take a moment")
        bot_message = await bot.send_message(ctx.message.channel, embed=loading_message.get_embed())

        comment_message = await create_commentmessage(reddit_object, Config.r_last_post_url[ctx.message.server.id][ctx.message.channel.id]['id'],
                                                      Config.r_last_post_url[ctx.message.server.id][ctx.message.channel.id]['title'],
                                                      Config.r_last_post_url[ctx.message.server.id][ctx.message.channel.id]['preview'],
                                                      Config.r_last_post_url[ctx.message.server.id][ctx.message.channel.id]['url'],
                                                      Config.r_last_post_url[ctx.message.server.id][ctx.message.channel.id]['type'],
                                                      ctx.message.channel)
    
        comment_message.manual_message = bot_message
        await comment_message.goto_page(bot, 0)
    
        Config.comment_messages[ctx.message.server.id][ctx.message.channel.id][comment_message.message.id] = comment_message

    else:
        embed = RedditErrorEmbed()
        embed.create_embed(title=":warning: No last post saved from this channel in the current session!")
        await bot.send_message(ctx.message.channel, embed=embed.get_embed())

    
@bot.command(pass_context=True, description="Get posts from a Reddit link. \n"
                                            "Can also grab comments from that post "
                                            "(add argument 'c' or 'getc' after url)")
async def ru(ctx, url: str, *args):
    """
    Request Reddit content by a Reddit submission URL
    """
    if args:
        comments = True if "c" or "getc" in args else False
    else:
        comments = False
    await reddit_handler(ctx, comments=comments, url=url)


@bot.command(pass_context=True, description="Get posts with comments from Reddit")
async def rc(ctx, subreddit: str, *post_count: int):
    """
    Request Reddit posts from a subreddit and get comments from
    that post as well.

    :param subreddit: Subreddit to request from
    :param post_count: Amount of posts to randomize through. Optional

    """
    post_count = post_count[0] if post_count else Config.r_postcount

    await reddit_handler(ctx, subreddit=subreddit, post_count=post_count, comments=True)


@bot.command(pass_context=True, description="Get posts from reddit (any type)")
async def r(ctx, subreddit: str, *post_count: int):
    """
    Request posts from a certain subreddit, ignoring which type (image,text etc)
    :param subreddit: Subreddit to request from
    :param post_count: Amount of posts to randomize through. Optional
    """

    post_count = post_count[0] if post_count else Config.r_postcount

    await reddit_handler(ctx, subreddit=subreddit, post_count=post_count, image=None)


@bot.command(pass_context=True, description="Get image-only posts from reddit")
async def ri(ctx, subreddit: str, *post_count: int):
    """
    Request Image-Only posts from a certain subreddit.

    :param subreddit: Subreddit to request from
    :param post_count: Amount of posts to randomize through. Optional
    """
    post_count = post_count[0] if post_count else Config.r_postcount

    await reddit_handler(ctx, subreddit=subreddit, post_count=post_count, image=True)


@bot.command(pass_context=True, description="Get text-only posts from reddit")
async def rt(ctx, subreddit: str, *post_count: int):
    """
    Request text-only posts from a certain subreddit.
    :param subreddit: Subreddit to request from
    :param post_count: Amount of posts to randomize through. Optional
    """
    post_count = post_count[0] if post_count else Config.r_postcount

    await reddit_handler(ctx, subreddit=subreddit, post_count=post_count, image=False)


async def reddit_handler(ctx, **kwargs):
    """
    Main handler for processing and displaying reddit content.

    TODO: Better Description Here
    """
    subreddit = kwargs.get('subreddit', None)
    url = kwargs.get('url', None)
    post_count = int(kwargs.get('post_count', 1))
    image = kwargs.get('image', None)
    get_comments = kwargs.get('comments', False)
    request_type = 'default'

    if subreddit is not None:
        subreddit = subreddit.lower()

    if url is not None:
        request_type = 'url'

    # this is already done in reddit.py but we want to show how much posts we are getting in chat
    if post_count is not None:
        if post_count > Config.r_maxpostcount:
            post_count = Config.r_maxpostcount
    else:
        post_count = 1

    # delete the request message
    await bot.delete_message(ctx.message)

    # send a message to show the requester whats happening
    loading_message = RedditLoadingEmbed()
    loading_message.create_embed(subreddit=('unknown' if subreddit is None else subreddit), post_count=post_count)
    bot_message = await bot.send_message(ctx.message.channel, embed=loading_message.get_embed())

    # check if discord channel is marked as NSFW
    nsfw = await check_nsfw(ctx)

    # start off with getting posts
    red = Reddit(reddit_object)
    error_embed = None
    try:

        post = await red.get(subreddit=subreddit,
                             post_count=post_count,
                             nsfw=nsfw,
                             get_image=image,
                             request_type=request_type,
                             url=url)

    except SubredditNotExist:
        error_embed = RedditErrorEmbed()
        error_embed.create_embed(title="r/" + str(subreddit) + " does not exist.",
                                 description="Check your spelling")
    except SubredditIsNSFW:
        error_embed = RedditErrorEmbed()
        error_embed.create_embed(title="r/" + str(subreddit) + " is a NSFW subreddit",
                                 description="This channel is not set as a NSFW channel. "
                                             "If you want to add this channel as a NSFW channel, "
                                             "use the command -nsfw add.")
    except NoPostsReturned:
        error_embed = RedditErrorEmbed()
        error_embed.create_embed(title="No Posts Returned",
                                 description="Maybe try again with larger post count. "
                                             "If you are getting only images or only text,"
                                             " some subreddits may not have e.g only images.")

    except InvalidRedditURL:
        error_embed = RedditErrorEmbed()
        error_embed.create_embed(title="Invalid Reddit Submission URL entered",
                                 description="Make sure the URL you entered is correct and links "
                                             "to a post.")

    except RedditOAuthException as e:
        error_embed = RedditErrorEmbed()
        error_embed.create_embed(title="Reddit Authentication Failure",
                                 description="Make sure you have enter credentials and that they are correct"
                                             "in the config file. Also make sure only application using your "
                                             "API credentials at once. " + str(e))
    except UnknownException as e:
        error_embed = RedditErrorEmbed()
        error_embed.create_embed(title="Unknown Error",
                                 description="""R-BotReborn has not been programmed to handle this error.
                                             Error Output: """ + str(e))

    finally:
        if error_embed is not None:
            await bot.edit_message(bot_message, embed=error_embed.get_embed())
            return

    post_type = post.get('post_type')
    post_text = post.get('post_text')
    post_id = post.get('post_id')
    image_url = "NONE"  # had issues with None being turned to a str type for some reason
    if post_type != "link" and post_type != "reddit":
        if post_type != "gif" and post_type != "image":
            if post_type == "gfycat":
                post_gfycat = Gfycat(Config.gfycat_client_id, Config.gfycat_client_secret)
                gfyjson = await post_gfycat.get_gfy_info(str(post.get('post_url'))[19:(len(str(post.get('post_url'))))])
                print(gfyjson)  # TODO: fails if starts with http://
                image_url = gfyjson['gfyItem']['max5mbGif']

                if isinstance(image_url, GfycatErrorEmbed):
                    await bot.send_message(ctx.message.channel, embed=image_url.get_embed())
                    image_url = "NONE"
                # TODO: maybe some error handling here?
            elif post_type == "imgur":

                post['post_text'] = "R-BotReborn: Imgur Links are not supported yet"

            else:

                processing_embed = GfycatLoadingEmbed(post.get('post_permalink'))
                await bot.edit_message(bot_message, embed=processing_embed.get_embed())

                image_url, color = await gfycat_url_handler(post.get('post_url'))
                print(image_url)

                if isinstance(image_url, GfycatErrorEmbed):
                    await bot.send_message(ctx.message.channel, embed=image_url.get_embed())
                    image_url = "NONE"

        elif post_type == "gif" or post_type == "image":  # either gif or image

            image_url = post.get('post_url')

    elif post_type == "link":
        
        if Config.enable_sumy:
            # tldrify if user wants
            # we are going to TLDRify the link (but only if there is not text to start with)
            if post_text == "":
                post_text = "**tl;dr:** " + await sumy_url(post.get('post_url'))

    post_embed = RedditPostEmbed()
    post_embed.create_embed(title=str(post.get('post_title')),
                            url=str(post.get('post_permalink')),
                            author=str(post.get('post_author')),
                            nsfw=bool(post.get('nsfw')),
                            score=int(post.get('post_score')),
                            description=str(post_text),
                            image=str(image_url),
                            time=str(post.get('created_utc')) + " GMT",
                            subreddit=str(post.get('post_subreddit')),
                            gilded=int(post.get('gilded'))

                            )

    await bot.edit_message(bot_message, embed=post_embed.get_embed())

    if get_comments:
        loading_message = RedditLoadingEmbed()
        loading_message.create_embed(footer_text="Getting comments for post '" + str(post.get('post_title'))[:16] + " (...)'",
                                     custom_message="Getting comments... This may take a moment")
        the_message = await bot.send_message(ctx.message.channel, embed=loading_message.get_embed())

        cmessage = await create_commentmessage(reddit_object, post.get('post_id'), post.get('post_title'), post.get('post_preview'), post.get('post_permalink'), post.get('post_type'), ctx.message.channel)
        cmessage.manual_message = the_message
        await cmessage.goto_page(bot, 0)
        Config.comment_messages[ctx.message.server.id][ctx.message.channel.id][cmessage.message.id] = cmessage

    Config.r_last_post_url[str(ctx.message.server.id)][str(ctx.message.channel.id)] = {'id': post_id,
                                                                                       'title': str(post.get('post_title')),
                                                                                       'url': str(post.get('post_permalink')),
                                                                                       'type': str(post.get('post_type')),
                                                                                       'preview': str(post.get('post_preview'))}
    

@bot.group(pass_context=True, description=f"Add/Remove NSFW on current channel. \n"
                                          f"usage: {Config.bot_prefix}nsfw <add>/<remove>")
async def nsfw(ctx):
    """
    Set NSFW Permissions
    Use the subcommands
    """
    if ctx.invoked_subcommand is None:
        await bot.send_message(ctx.message.channel, f"usage: {Config.bot_prefix}nsfw <add>/<remove>")


@nsfw.command(pass_context=True, description="Add the current channel as a NSFW channel")
async def add(ctx):
    """
    Add the current channel as a NSFW channel to allow
    NSFW content on it
    """
    new_channels, message = config.UpdateConfig('config.ini').add_nsfw_channels(str(ctx.message.server.id),
                                                                                str(ctx.message.channel.id))
    Config.nsfw_channels = new_channels
    if message is None:
        embed = discord.Embed(title=":underage: Added this channel as a NSFW Channel")
    else:
        embed = discord.Embed(title=":warning:" + str(message))

    await bot.say(embed=embed)


@nsfw.command(pass_context=True, description="Remove the current channel as a NSFW channel")
async def remove(ctx):
    """
        Remove the current channel as a NSFW channel to disallow
        NSFW content on it
        """
    new_channels, message = config.UpdateConfig('config.ini').remove_nsfw_channels(str(ctx.message.server.id),
                                                                                   str(ctx.message.channel.id))
    Config.nsfw_channels = new_channels

    if message is None:
        embed = discord.Embed(title=":wastebasket: Removed this channel as a NSFW Channel")
    else:
        embed = discord.Embed(title=":warning: " + str(message))

    await bot.say(embed=embed)


async def check_nsfw(ctx):
    """
    Check if the channel in ctx is nsfw or not
    :param ctx:
    :return: True or False (for being NSFW or not)
    """
    try:
        return True if str(ctx.message.channel.id) in Config.nsfw_channels[ctx.message.server.id] else False
    except KeyError:
        return False  # server doesn't exist


@bot.event
async def on_reaction_add(reaction, user):
    print("Reaction Detected: " + str(reaction.emoji) + " from user "+ str(user))

    if str(user.id) != str(bot.user.id):

        if isinstance(Config.comment_messages[reaction.message.server.id][reaction.message.channel.id][reaction.message.id], CommentMessage):

            cmsg = Config.comment_messages[reaction.message.server.id][reaction.message.channel.id][reaction.message.id]
        
            if reaction.emoji == "▶":

                await cmsg.next_page(bot, 1)
                Config.comment_messages[reaction.message.server.id][reaction.message.channel.id][reaction.message.id] = cmsg
                await bot.remove_reaction(reaction.message, "▶", user)

            elif reaction.emoji == "◀":

                await cmsg.prev_page(bot, 1)
                Config.comment_messages[reaction.message.server.id][reaction.message.channel.id][reaction.message.id] = cmsg
                await bot.remove_reaction(reaction.message, "◀", user)

            elif reaction.emoji == "↩":
               
                await cmsg.goto_page(bot, 0)
                Config.comment_messages[reaction.message.server.id][reaction.message.channel.id][reaction.message.id] = cmsg
                await bot.remove_reaction(reaction.message, "↩", user)

            elif reaction.emoji == "🔄":

                await cmsg.refresh(bot)
                Config.comment_messages[reaction.message.server.id][reaction.message.channel.id][reaction.message.id] = cmsg
                await bot.remove_reaction(reaction.message, "🔄", user)

            elif reaction.emoji == "🚫":
                print("deleting message")
                await bot.delete_message(reaction.message)
                # delete this message from the dictionary
                del Config.comment_messages[reaction.message.server.id][reaction.message.channel.id][reaction.message.id]
    else:
        print("This reaction is from this bot so ignoring")


@bot.event
async def on_ready():

    logging.info('Logged into discord as:')
    logging.info(bot.user.name)
    logging.info(bot.user.id)
    await bot.change_presence(game=discord.Game(name=Config.bot_game))
    if not hasattr(bot, 'uptime'):
        bot.uptime = (datetime.datetime.utcnow()).strftime("%d-%m-%Y %H:%M:%S")
    logging.info(f"Recording uptime from: {bot.uptime}")


# main method run when starting
def start():
    # connect to discord
    bot.run(Config.discord_token)


# connect to reddit (instance)
def connect_reddit():
    reddit = praw.Reddit(client_id=Config.r_client_id,
                         client_secret=Config.r_client_secret,
                         user_agent=Config.r_user_agent,
                         )
    return reddit


if __name__ == '__main__':
    reddit_object = connect_reddit()
    start()
