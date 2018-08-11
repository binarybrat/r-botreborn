import requests
import logging
import asyncio
from exceptions import *
import json
logging = logging.basicConfig(level=logging.DEBUG)

# TODO: possibly rewrite or tidy up, this looks like kind of a mess

class Gfycat:

    def __init__(self, client_id, client_secret):
        self._api_url = "https://api.gfycat.com/v1"
        self.__client_id = str(client_id)
        self.__client_secret = str(client_secret)

        if self.__client_id is None or self.__client_secret is None:
            raise GfycatMissingCredentials

    async def get_api_token(self, api_url):

        data = {"client_id": self.__client_id,
                "client_secret": self.__client_secret,
                "grant_type": "client_credentials"}

        def do_req():
            return requests.post(api_url, data=str(data)).json()

        loop4 = asyncio.get_event_loop()
        req = loop4.run_in_executor(None, do_req)
        response = await req
        print(response)
        try:
            return response['access_token']
        except KeyError:
            if response['errorMessage']['code'] == 'InvalidClient':
                raise GfycatInvalidCredentials
            else:
                raise UnknownException("Exception after KeyError in getting "
                                       "gfycat API token. " + str(response))

    async def __upload_by_link(self, token:str, url:str, api_url):

        data = {
            "fetchUrl": url
        }

        def do_req():
            return requests.post(api_url, data=str(data)).json()

        loop3 = asyncio.get_event_loop()
        req = loop3.run_in_executor(None, do_req)
        response1 = await req

        try:
            return response1['gfyname']
        except KeyError:
            raise GfycatProcessError(str(response1))
        except Exception as e:
            raise UnknownException("Gfycat.py unknown error in url_from_link: " + (str(e)) + ".")

    async def get_upload_status(self, gfy_name, api_url):

        loop = asyncio.get_event_loop()
        future1 = loop.run_in_executor(None, requests.get, (api_url + "/fetch/status/" + gfy_name))

        response1 = await future1

        return response1.json()

    async def get_gfy_info(self, gfy_name):
        loop = asyncio.get_event_loop()
        api_url = "https://api.gfycat.com/v1"
        future2 = loop.run_in_executor(None, requests.get, api_url + "/gfycats/" + gfy_name)
        reponse = await future2
        print(reponse)
        return reponse.json()

    async def get_url_from_link(self, link:str):
        access_token = await self.get_api_token(self._api_url + "/oauth/token")
        gfy_name = await self.__upload_by_link(access_token, link, self._api_url + "/gfycats")

        data = await asyncio.ensure_future(self.wait_till_finished(gfy_name))
        return data

    async def wait_till_finished(self, gfy_name):

        refresh = True
        while refresh:

            status = await self.get_upload_status(gfy_name, self._api_url + "/gfycats")
            if status['task'] == 'complete':
                refresh = False
                print(status)

                try:
                    return {'5mb_gif_url': status['max5mbGif'], 'name': status['gfyName'],
                            'color': status['avgColor']}
                except KeyError:
                    gif_info = await self.get_gfy_info(gfy_name)
                    return {'5mb_gif_url': gif_info['gfyItem']['max5mbGif'], 'name': gif_info['gfyItem']['gfyName'], 'color': gif_info['gfyItem']['avgColor']}
            elif status['task'] == 'error':
                raise GfycatProcessError(status)

