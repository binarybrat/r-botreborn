import discord

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
        if is_nsfw:
            nsfw_text = " | NSFW"
        else:
            nsfw_text = ""

        self._embed = discord.Embed(title=title, url=url, description=description, colour=self._colour)

        print(type(image_url))
        if image_url != "NONE":
            print("setting image")
            self._embed.set_image(url=image_url)

        if time:
            time = " | " + str(time)
        else:
            time = " "
        self._embed.set_footer(text="u/" + author + " via r/" + subreddit + " | Score: " + str(
            post_score) + nsfw_text + time,
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
        self._colour = 0xf1c40f

    def create_embed(self, **kwargs):
        comments = kwargs.get('comments', [])

        self._embed = discord.Embed(title="Comments", description=str(len(comments)) + " top-level comments received", colour=self._colour)
        for comment in comments:
            try:
                self._embed.add_field(name="u/" + str(comment.author) + " | Score: " + str(comment.score) + " | " + str(comment.created_utc) + " UTC", value=str(comment.body), inline=False)
            except IndexError:
                pass
        self._embed.set_footer(icon_url=self._reddit_icon_url, text="reddit")



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

    def __init__(self):
        super().__init__()
        self._loading_gif = 'https://www.drupal.org/files/issues/throbber_13.gif'

        self.create_embed(title='Encoding on Gfycat',
                          description='Please wait, this may take a while',
                          thumbnail=self._loading_gif
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




