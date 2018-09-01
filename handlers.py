"""

handlers for various url image types returned and need to be processed in a way to display in a discord embed


"""

from custom_embeds import *
from exceptions import *
from gfycat import Gfycat
from rbotreborn import Config


# from PyTeaserPython3.pyteaser import SummarizeUrl
async def gfycat_url_handler(url: str):
    error_embed = None
    try:
        post_gfycat = Gfycat(Config.r_gfycat_client_id, Config.r_gfycat_client_secret)
        gfyjson = await post_gfycat.get_url_from_link(url)
        print(gfyjson)
        return gfyjson['5mb_gif_url']
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
            return error_embed

# TODO: add a summary thing for url based posts (for news articles etc)
# use like pyteaser but need to add a cli arguments to be able to run python2 code
# then save output to a file
# and make this optional
# async def tldrify_url(url):
#     print("tldrifying")
#     loop = asyncio.get_event_loop()
#
#     def do_stuff():
#         return SummarizeUrl(url)
#
#     future = loop.run_in_executor(None, do_stuff)
#     summary = await future
#
#     return summary[0]
