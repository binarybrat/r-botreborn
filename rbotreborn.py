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
Config = config.Config('config.ini')
bot = commands.Bot(command_prefix=Config.bot_prefix,
                          description='R-BOT Reborn')
# will hold the reddit instance
reddit = None


@bot.command(pass_context=True, description="Get posts with comments from Reddit")
async def rc(ctx, subreddit:str, *comment_count:int):
    if comment_count:
        comment_count = comment_count[0]
    else:
        comment_count = Config.r_postcount

    await reddit_handler(ctx, subreddit, Config.r_postcount, None, comment_count)


@bot.command(pass_context=True, description="Get posts from reddit (any type)")
async def r(ctx, subreddit:str, *post_count:int):
    if post_count:
        post_count = post_count[0]
    else:
        post_count = Config.r_postcount

    await reddit_handler(ctx, subreddit, post_count, None, 0)

@bot.command(pass_context=True, description="Get image-only posts from reddit")
async def ri(ctx, subreddit:str, *post_count:int):
    if post_count:
        post_count = post_count[0]
    else:
        post_count = Config.r_postcount

    await reddit_handler(ctx, subreddit, post_count, True, 0)


@bot.command(pass_context=True, description="Get text-only posts from reddit")
async def rt(ctx, subreddit:str, *post_count:int):
    # TODO
    if post_count:
        post_count = post_count[0]
    else:
        post_count = Config.r_postcount

    await reddit_handler(ctx, subreddit, post_count, False, 0)


# where all the reddit commands use
async def reddit_handler(ctx, subreddit, post_count, image, comment_num):

    # this is already done in reddit.py but we want to show how much posts we are getting in chat
    if post_count > Config.r_maxpostcount:
        post_count = Config.r_maxpostcount
    # delete the request message
    await bot.delete_message(ctx.message)

    # send a message to show the requester whats happening

    loading_message = RedditLoadingEmbed()
    loading_message.create_embed(subreddit=subreddit, post_count=post_count)
    bot_message = await bot.send_message(ctx.message.channel, embed=loading_message.get_embed())
    # check if discord channel is marked as NSFW

    if str(ctx.message.channel) in Config.nsfw_channels:
        nsfw = True
    else:
        nsfw = False

    # start off with getting posts
    red = Reddit(reddit)
    error_embed = None
    try:
        post, comments = await red.get(subreddit=str(subreddit.lower()), post_count=int(post_count), nsfw=nsfw, get_image=image, comment_count=comment_num)

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
    print(post)
    post_type = post.get('post_type')
    image_url = "NONE" # had issues with None being turned to a str type for some reason
    if post_type != "link" and post_type != "reddit":

        if post_type != "gif" and post_type != "image":

            if post_type == "gfycat":

                post_gfycat = Gfycat(Config.r_gfycat_client_id, Config.r_gfycat_client_secret)
                gfyjson = await post_gfycat.get_gfy_info(str(post.get('post_url'))[19:(len(str(post.get('post_url'))))])
                print(gfyjson) # TODO: fails if starts with http://
                image_url = gfyjson['gfyItem']['max5mbGif']
                # TODO: maybe some error handling here?
            elif post_type == "imgur":

                post['post_text'] = "R-BotReborn: Imgur Links are not supported yet"

            else:

                processing_embed = GfycatLoadingEmbed()
                await bot.edit_message(bot_message, embed=processing_embed.get_embed())
                try:
                    post_gfycat = Gfycat(Config.r_gfycat_client_id, Config.r_gfycat_client_secret)
                    gfyjson = await post_gfycat.get_url_from_link(str(post.get('post_url')))
                    print(gfyjson)
                    image_url = gfyjson['5mb_gif_url']
                except KeyError as e:
                    error_embed = GfycatErrorEmbed()
                    error_embed.create_embed(title="Something went wrong with processing the GIF",
                                             description="KeyError. " + str(e))
                except GfycatProcessError as e:
                    error_embed = GfycatErrorEmbed()
                    error_embed.create_embed(title="Something went wrong when processing the GIF",
                                             description="GfycatProcessError: " + str(e))
                except GfycatMissingCredentials:
                    error_embed = GfycatErrorEmbed()
                    error_embed.create_embed(title="Missing Gfycat API Credentials",
                                             description="Make sure your "
                                                         "client id and client secret are in the config file"
                                                         " and correct.")

                except GfycatInvalidCredentials:
                    error_embed = GfycatErrorEmbed()
                    error_embed.create_embed(title="Invalid Gfycat API Credentials",
                                             description="Make sure your "
                                                         "client id and client secret are in the config file"
                                                         " and correct."
                                             )
                except UnknownException as e:
                    error_embed = GfycatErrorEmbed()
                    error_embed.create_embed(title="Unknown Exception in Gfycat.py",
                                             description=str(e))
                finally:
                    if error_embed is not None:

                        # time to send error to channel
                        await bot.edit_message(bot_message, embed=error_embed.get_embed())
                        return

        elif post_type == "gif" or post_type == "image": # either gif or image

            image_url = post.get('post_url')

    # create reddit embed
    comment_embed = None
    if len(comments) > 0:
        comment_embed = RedditCommentEmbed()
        comment_embed.create_embed(comments=comments)
    post_embed = RedditPostEmbed()
    post_embed.create_embed(title=str(post.get('post_title')),
                            url=str(post.get('post_permalink')),
                            author=str(post.get('post_author')),
                            nsfw=bool(post.get('nsfw')),
                            score=int(post.get('post_score')),
                            description=str(post.get('post_text')),
                            image=str(image_url),
                            time=str(post.get('created_utc')) + " UTC",
                            subreddit=str(subreddit)
                            )
    await bot.edit_message(bot_message, embed=post_embed.get_embed())


    if comment_embed is not None:
        await bot.send_message(ctx.message.channel, embed=comment_embed.get_embed())


@bot.command(pass_context = True, description="Allow NSFW on current channel")
async def addnsfw(ctx):

    new_channels, message = config.UpdateConfig('config.ini').update_nsfw_channels(str(ctx.message.channel))
    Config.nsfw_channels = new_channels

    if message is None:
        embed = discord.Embed(title="Added this channel as a NSFW Channel")
    else:
        embed = discord.Embed(title=str(message))
    embed.set_thumbnail(url='https://cdn.discordapp.com/emojis/282783839980355585.png')
    await bot.send_message(ctx.message.channel, embed=embed)

@bot.event
# when ready display this shit
async def on_ready():
    logging.info('Logged into discord as:')
    logging.info(bot.user.name)
    logging.info(bot.user.id)

    logging.info("Logged into reddit as:")
    logging.info(reddit.user.me())
    logging.info('------')
    await bot.change_presence(game=discord.Game(name=Config.bot_game))


# main method run when starting
def start():
    # connect to discord
    print(Config.discord_token)
    bot.run(Config.discord_token)
    


# connect to reddit (instance)
def connect_reddit():
    global reddit
    reddit = praw.Reddit(client_id=Config.r_client_id,
                         client_secret=Config.r_client_secret, password=Config.r_password,
                         user_agent=Config.r_user_agent, username=Config.r_username)


if __name__ == '__main__':

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    connect_reddit()

    start()
  



