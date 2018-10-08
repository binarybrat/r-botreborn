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
import itertools
from commentmessage import *
import collections



Config = config.Config('config.ini')
bot = commands.Bot(command_prefix=Config.bot_prefix,
                   description='R-BotReborn v0.3.1 \n https://github.com/colethedj/r-botreborn')
Logger = logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

@bot.command(pass_context=True, description="Get comments from the last post")
async def rcl(ctx):

    await bot.delete_message(ctx.message)
    if ctx.message.channel.id in Config.r_last_post_url[ctx.message.server.id]:
        loading_message = RedditLoadingEmbed()
        loading_message.create_embed(footer_text="Getting comments for the previous post",
                                    custom_message="Getting comments... This will take a moment")
        bot_message = await bot.send_message(ctx.message.channel, embed=loading_message.get_embed())

        
        cmessage = await create_commentmessage(reddit2, Config.r_last_post_url[ctx.message.server.id][ctx.message.channel.id]['id'],
                                                    Config.r_last_post_url[ctx.message.server.id][ctx.message.channel.id]['title'],
                                                    Config.r_last_post_url[ctx.message.server.id][ctx.message.channel.id]['preview'], 
                                                    Config.r_last_post_url[ctx.message.server.id][ctx.message.channel.id]['url'], 
                                                    Config.r_last_post_url[ctx.message.server.id][ctx.message.channel.id]['type'], 
                                                    ctx.message.channel)
    
        cmessage.manual_message = bot_message
        await cmessage.goto_page(bot, 0)
    
        Config.comment_messages[ctx.message.server.id][ctx.message.channel.id][cmessage.message.id] = cmessage
    

    else:
        embed = RedditErrorEmbed()
        embed.create_embed(title=":warning: No last post saved from this channel in the current session!")
        await bot.send_message(ctx.message.channel, embed=embed.get_embed())

    
@bot.command(pass_context=True, description="Get posts from a Reddit link. \n"
                                            "Can also grab comments from that post if needed (add argument 'comments' or 'getc' or 'getcomments' after url)")
async def ru(ctx, url: str, *args):
    if args:
        if "comments" or "getc" or "getcomments" in args:
            comments = True
        else:
            comments = False
        
    else:
        comments = False
    await reddit_handler(ctx, comments=comments, url=url)


@bot.command(pass_context=True, description="Get posts with comments from Reddit")
async def rc(ctx, subreddit: str, *post_count: int):
    if post_count:
        post_count = post_count[0]
    else:
        post_count = Config.r_postcount


    await reddit_handler(ctx, subreddit=subreddit, post_count=post_count, comments=True)


@bot.command(pass_context=True, description="Get posts from reddit (any type)")
async def r(ctx, subreddit: str, *post_count: int):
    if post_count:
        post_count = post_count[0]
    else:
        post_count = Config.r_postcount

    await reddit_handler(ctx, subreddit=subreddit, post_count=post_count, image=None)


@bot.command(pass_context=True, description="Get image-only posts from reddit")
async def ri(ctx, subreddit: str, *post_count: int):
    if post_count:
        post_count = post_count[0]
    else:
        post_count = Config.r_postcount

    await reddit_handler(ctx, subreddit=subreddit, post_count=post_count, image=True)


@bot.command(pass_context=True, description="Get text-only posts from reddit")
async def rt(ctx, subreddit: str, *post_count: int):
    # TODO
    if post_count:
        post_count = post_count[0]
    else:
        post_count = Config.r_postcount

    await reddit_handler(ctx, subreddit=subreddit, post_count=post_count, image=False)


# where all the reddit commands use

# REQUEST TYPES: 'default', 'url'
async def reddit_handler(ctx, **kwargs):
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

    if str(ctx.message.channel.id) in Config.nsfw_channels[ctx.message.server.id]:
        nsfw = True
    else:
        nsfw = False

    # start off with getting posts
    red = Reddit(reddit2)
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
                                 description="check your spelling")
    except SubredditIsNSFW:
        error_embed = RedditErrorEmbed()
        error_embed.create_embed(title="r/" + str(subreddit) + " is a NSFW subreddit",
                                 description="This channel is not set as a NSFW channel. "
                                             "If you want to add this channel as a NSFW channel, "
                                             "use the command -addnsfw.")
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
                                 description="""R-BOT has not been programmed to handle this error.
                                             Error Output: """ + str(e))

    finally:
        if error_embed is not None:
            await bot.edit_message(bot_message, embed=error_embed.get_embed())
            return
    # TODO: ERROR HANDLERS
    # handle the post types

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
                # TODO: maybe some error handling here?
            elif post_type == "imgur":

                post['post_text'] = "R-BotReborn: Imgur Links are not supported yet"

            else:

                processing_embed = GfycatLoadingEmbed(post.get('post_permalink'))
                await bot.edit_message(bot_message, embed=processing_embed.get_embed())

                image_url = await gfycat_url_handler(post.get('post_url'))
                print(image_url)
                if image_url is GfycatErrorEmbed:
                    # time to send error to channel

                    await bot.edit_message(bot_message, embed=error_embed.get_embed())
                    image_url = None
                    return

        elif post_type == "gif" or post_type == "image":  # either gif or image

            image_url = post.get('post_url')

    elif post_type == "link":
        
        if Config.enable_sumy:
            # tldrify if user wants
            # TODO: add this function
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
                                    custom_message="Getting comments... This will take a moment")
        the_message = await bot.send_message(ctx.message.channel, embed=loading_message.get_embed())

        cmessage = await create_commentmessage(reddit2, post.get('post_id'), post.get('post_title'), post.get('post_preview'), post.get('post_permalink'), post.get('post_type'), ctx.message.channel)
        cmessage.manual_message = the_message
        comment_embed = await cmessage.goto_page(bot, 0)
        Config.comment_messages[ctx.message.server.id][ctx.message.channel.id][cmessage.message.id] = cmessage

    
    Config.r_last_post_url[str(ctx.message.server.id)][str(ctx.message.channel.id)] = {'id': post_id, 'title': str(post.get('post_title')), 'url': str(post.get('post_permalink')), 'type': str(post.get('post_type')),'preview': str(post.get('post_preview'))}
    

@bot.group(pass_context=True, description="Add/Remove NSFW on current channel. \n"
                                            "usage: {}nsfw <add>/<remove>".format(Config.bot_prefix))
async def nsfw(ctx):
    if ctx.invoked_subcommand is None:
        await bot.send_message(ctx.message.channel, 'usage: {}nsfw <add>/<remove>'.format(Config.bot_prefix))

@nsfw.command(pass_context=True, description="Add the current channel as a NSFW channel")
async def add(ctx):
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
    new_channels, message = config.UpdateConfig('config.ini').remove_nsfw_channels(str(ctx.message.server.id),
                                                                                   str(ctx.message.channel.id))
    Config.nsfw_channels = new_channels

    if message is None:
        embed = discord.Embed(title=":wastebasket: Removed this channel as a NSFW Channel")
    else:
        embed = discord.Embed(title=":warning: " + str(message))

    await bot.say(embed=embed)


@bot.event
async def on_ready():
    logging.info('Logged into discord as:')
    logging.info(bot.user.name)
    logging.info(bot.user.id)
    await bot.change_presence(game=discord.Game(name=Config.bot_game))


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



@bot.event
async def on_reaction_add(reaction, user):
    print("Reaction Detected: " + str(reaction.emoji) + " from user "+ str(user))

    if str(user.id) != str(bot.user.id):
        if Config.comment_messages[reaction.message.server.id][reaction.message.channel.id][reaction.message.id] is not None:

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

                await bot.delete_message(reaction.message)
                # delete this message from the dctionary
                del Config.comment_messages[reaction.message.server.id][reaction.message.channel.id][reaction.message.id]
    else:
        print("This reaction is from this bot so ignoring")


if __name__ == '__main__':

    reddit2 = connect_reddit()

    start()
