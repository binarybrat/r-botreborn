"""

handlers for various url image types returned and need to be processed in a way to display in a discord embed


"""
from __future__ import absolute_import
from __future__ import division, print_function, unicode_literals

from custom_embeds import *
from exceptions import *
from gfycat import Gfycat
from rbotreborn import Config
import asyncio
# SUMY imports

from sumy.parsers.html import HtmlParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words



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


async def tldrify_url(url):
    print("tldrifying")
    print(url)
    loop = asyncio.get_event_loop()

    # TODO: have these in config file

    LANGUAGE="english"
    SENTENCES_COUNT="3"


    def do_stuff():
        summard = ""
        parser = HtmlParser.from_url(url, Tokenizer(LANGUAGE))
        stemmer = Stemmer(LANGUAGE)
        summarizer = Summarizer(stemmer)
        summarizer.stop_words = get_stop_words(LANGUAGE)
        for sentence in summarizer(parser.document, SENTENCES_COUNT):
            summard = summard + " " + str(sentence)
        return summard

    future = loop.run_in_executor(None, do_stuff)
    summary = await future

    return summary
