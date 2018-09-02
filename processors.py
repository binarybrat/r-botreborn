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
import logging

# SUMY imports
from sumy.parsers.html import HtmlParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words


async def gfycat_url_handler(url: str):
    error_embed = None
    try:
        post_gfycat = Gfycat(Config.gfycat_client_id, Config.gfycat_client_secret)
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


# Text summarizer using Sumy https://github.com/miso-belica/sumy

# TODO: maybe adaptive sentence to request more sentences if word count is low (like max 300 words)
async def sumy_url(url):

    logging.debug("Summarizing URL " + str(url))
    loop = asyncio.get_event_loop()

    def do_stuff():
        summary_final = ""
        parser = HtmlParser.from_url(url, Tokenizer(Config.sumy_lang))
        stemmer = Stemmer(Config.sumy_lang)
        summarizer = Summarizer(stemmer)
        summarizer.stop_words = get_stop_words(Config.sumy_lang)
        for sentence in summarizer(parser.document, Config.sumy_num_sentences):
            summary_final = summary_final + " " + str(sentence)
        return summary_final

    future = loop.run_in_executor(None, do_stuff)
    summary = await future

    if len(summary) > 1850:
        summary = summary[:1850] + '... [go to link to read more]'

    return summary
