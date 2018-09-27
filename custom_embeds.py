import discord
from exceptions import EmbedNotExistError
from time import gmtime, strftime
"""

REDDIT EMBED TEMPLATES

"""


class RedditPostEmbed:

    def __init__(self):
        self._colour = 0x992d22
        self._reddit_icon_url = 'https://www.redditstatic.com/desktop2x/img/favicon/apple-icon-57x57.png'
        self._embed = None

    def get_embed(self):
        return self._embed

    def create_embed(self, **kwargs):
        subreddit = str(kwargs.get('subreddit', "unknown"))
        is_nsfw = bool(kwargs.get('nsfw', False))
        post_score = int(kwargs.get('score', 0))
        author = str(kwargs.get('author', "unknown"))
        image_url = kwargs.get('image', "NONE")
        url = kwargs.get('url', discord.Embed.Empty)
        description = kwargs.get('description', discord.Embed.Empty)
        title = kwargs.get('title', discord.Embed.Empty)
        time = kwargs.get('time', None)
        gilded = int(kwargs.get('gilded', 0))
        if is_nsfw:
            nsfw_text = " | NSFW"
        else:
            nsfw_text = ""

        if gilded > 0:
            if gilded > 1:
                gilded_text = " | ⭐ x" + str(gilded)
            else:
                gilded_text = " | ⭐"
        else:
            gilded_text = ""

        self._embed = discord.Embed(title=title, url=url, description=description, colour=self._colour)

        if image_url != "NONE":
            self._embed.set_image(url=image_url)

        if time:
            time = " | " + str(time)
        else:
            time = " "
        self._embed.set_footer(text="u/" + author + " via r/" + subreddit + " | Score: " + str(
            post_score) + nsfw_text + time + gilded_text,
                         icon_url=self._reddit_icon_url)


class RedditLoadingEmbed(RedditPostEmbed):

    def __init__(self):
        super().__init__()
        self._colour = 0x546e7a
        print(self._reddit_icon_url)

    def create_embed(self, **kwargs):
        subreddit = str(kwargs.get('subreddit', "unknown")).lower()
        post_count = str(kwargs.get('post_count', "0"))
        comment_count = int(kwargs.get('comment_count', 0))
        custom_message = str(kwargs.get('custom_message', 'Getting posts... This will take a moment'))
        self._embed = discord.Embed(title=custom_message,
                                    colour=self._colour).set_footer(text=str(post_count) + " posts from r/" + str(subreddit) + " with " + str(comment_count) + " comments.")


class RedditErrorEmbed(RedditPostEmbed):

    def __init__(self):
        super().__init__()
        self._colour = 0xe74c3c

    def create_embed(self, **kwargs):
        title = kwargs.get('title', discord.Embed.Empty)
        description = kwargs.get('description', discord.Embed.Empty)
        extra_info = kwargs.get('extra', " ")

        if extra_info is not " ":
            extra_info = " | " + str(extra_info)

        self._embed = discord.Embed(title=title, description=description, colour=self._colour)
        self._embed.set_footer(icon_url=self._reddit_icon_url, text="reddit" + extra_info)

        
class RedditCommentEmbed(RedditPostEmbed):

    def __init__(self):
        super().__init__()
        self._colour = 0x206694

    def create_embed(self, **kwargs):
        comments = kwargs.get('comments', [])
        post_title = kwargs.get('title', "[Unknown Post Reference]")
        post_link = kwargs.get('url', discord.Embed.Empty)
        post_media_type = kwargs.get('post_type', None)
        preview = kwargs.get('preview', None)

        if len(post_title) > 50:
            post_title = (post_title[:50] + '...')

        if post_media_type is not None:
            type = "[" + str(post_media_type) + "]"
        else:
            type = ""
        title = "Comments for: " + post_title + " " + type

        self._embed = discord.Embed(title=title, url=post_link, description="*displaying " + str(len(comments)) + " comments*", colour=self._colour, inline=False)

        if preview is not None:
            if "http" in preview.lower():
                self._embed.set_thumbnail(url=preview)

        for comment in comments:
            try:
                if comment.edited:
                    edited_text = " | (edited)"
                else:
                    edited_text = " "

                if comment.is_submitter:
                    op_text = "**📢**"
                else:
                    op_text = ""

                if int(comment.gilded) > 0:
                    if int(comment.gilded) > 1:
                        gilded_text = " | ⭐ x" + str(comment.gilded)
                    else:
                        gilded_text = " | ⭐"
                else:
                    gilded_text = ""

                if comment.author_flair_text:
                    flair = " `" + str(comment.author_flair_text) + "`"
                else:
                    flair = ""
                self._embed.add_field(name=op_text + " u/" + str(comment.author) + flair, value=str(comment.body) + "\n\n [L](" + str(comment.permalink) + ") `Score: " + str(comment.score) + " | " + str(comment.created_utc) + " GMT " + str(edited_text) + gilded_text + "`", inline=False)

            except IndexError:
                pass

        self.__set_footer()

    def update_embed(self, **kwargs):

        status_message = kwargs.get('status_message', None)
        if self._embed is not None:
            self.__set_footer(status_message)

        else: # if an embed has not already been created then we will raise an exception
            raise EmbedNotExistError

    def __set_footer(self, **kwargs):
        status_message = kwargs.get('status_message', "Last Updated " + str(strftime("%Y-%m-%d %H:%M:%S", gmtime())) + " GMT")
        other_message = kwargs.get('other_message', " ")

        if other_message is not " ":
            other_message = " | " + other_message
        self._embed.set_footer(icon_url=self._reddit_icon_url, text=status_message + other_message)



"""

GFYCAT EMBED TEMPLATES

"""


class GfycatEmbed:

    def __init__(self):
        self._colour = 0xffffff
        self._ICON_URL = 'https://gfycat.com/static/favicons/favicon-96x96.png'
        self._embed = None

    def get_embed(self):
        return self._embed

    def create_embed(self, **kwargs):
        title = kwargs.get('title', 'Gfycat GIF')
        description = kwargs.get('description', discord.Embed.Empty)
        thumbnail = kwargs.get('thumbnail', None)
        url = kwargs.get('url', discord.Embed.Empty)
        colour = self._colour
        image = kwargs.get('image', None)

        self._embed = discord.Embed(title=title,
                                    description=description,
                                    url=url,
                                    colour=colour
                                    )
        if image is not None:
            self._embed.set_image(url=image)

        if thumbnail is not None:
            self._embed.set_thumbnail(url=thumbnail)

        self._embed.set_footer(text='gfycat', icon_url=self._ICON_URL)


class GfycatLoadingEmbed(GfycatEmbed):

    def __init__(self, original_url:str):
        super().__init__()
        # CREDIT TO: http://pluspng.com/png-45185.html
        self._loading_gif = 'http://pluspng.com/img-png/loader-png-powered-by-velaro-live-chat-512.gif'

        self.create_embed(title='Encoding on Gfycat',
                          description='Please wait, this may take a while',
                          thumbnail=self._loading_gif,
                          url=original_url
                          )


class GfycatErrorEmbed(GfycatEmbed):
    def __init__(self):
        super().__init__()
        self._colour = 0xe74c3c

    def create_embed(self, **kwargs):
        title = kwargs.get('title', discord.Embed.Empty)
        description = kwargs.get('description', discord.Embed.Empty)
        extra_info = kwargs.get('extra', " ")

        if extra_info:
            extra_info = " | " + str(extra_info)

        self._embed = discord.Embed(title=title, description=description, colour=self._colour)
        self._embed.set_footer(icon_url=self._ICON_URL, text="gfycat" + extra_info)




