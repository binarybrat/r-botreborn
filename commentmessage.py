from custom_embeds import RedditCommentEmbed, RedditErrorEmbed
from reddit import Reddit
import asyncio
import copy
import itertools
from rbotreborn import Config
from praw.models import MoreComments
from exceptions import *
from time import gmtime, strftime
# message timestamp


async def create_commentmessage(reddit, submission_id:str, submission_title:str, submission_preview:str, submission_url:str, submission_type:str, channel):
    comment_message = CommentMessage(reddit, submission_id, submission_title, submission_preview, submission_url, submission_type, channel)
    await comment_message._init()
    return comment_message


class CommentMessage:

    # post info
    # discord channel no
    # WARNING: sending in reddit object may expire (?) might want to check
    def __init__(self, reddit, submission_id:str, submission_title:str, submission_preview:str, submission_url:str, submission_type:str, channel):

        self.reddit = reddit # TODO: check if this reddit instance ever times out or whatever
        self.message = None
        self.manual_message = None
        self.__initial_comments = []
        self.__comments = []
        self.channel = channel

        # Reddit Stuff
        self.SUBMISSION_ID = submission_id
        self.SUBMISSION_TITLE = submission_title
        self.SUBMISSION_PREVIEW = submission_preview
        self.SUBMISSION_URL = submission_url
        self.SUBMISSION_TYPE = submission_type

        self.pages = []
        self.current_page = 0 # 0 is page 1
        self.current_page_comments = []
        self.current_morecomment_depth = 0 # amount of more comment instances we have used so far
        self.current_embed = None
        self.COMMENTS_PER_PAGE = Config.page_comment_num

        self.apply_emojis = [{'prev': True}, {'next': True}, {'start':True}, {'refresh': True}, {'delete':True}]
        self.emojis = {'prev':'◀', 'next':'▶', 'start':'↩', 'refresh':'🔄', 'delete':'🚫'}
        self._last_updated = None
        # more comments stuff
        self.used_morecomments = []

        self.flattened_post = []
        
    async def _init(self):
        await self.get_initial_comments()
        await self.create_pages()
    # create new pages based on comments

    async def create_pages(self, **kwargs):

        # Thanks to https://stackoverflow.com/questions/1624883/alternative-way-to-split-a-list-into-groups-of-n#1625023
        args = [iter(list(kwargs.get('iterable', self.__comments)))] * Config.page_comment_num
        self.pages = list([e for e in t if e is not None] for t in itertools.zip_longest(*args))

    async def update_pages(self): # WE ARE ASSUMING THE SELF.COMMENTS LIST NOW HAS NO MORE COMMENT OBJECTS IN IT (and is the new comments list returned from reddit)

        new_comments = copy.deepcopy(self.__comments) # this list stores comments we just got from reddit
        current_list = self.flattened_post # this list stores the comments that were used previously to create the pages

        unused_morecomments = []
        temp_comment_sortable_list = {}

        # save the index's of each comment into a sorted list. using this so we can easily delete
        for index, c in enumerate(new_comments):
            temp_comment_sortable_list[str(c)] = index

        queued_for_removal = []
        current_queued_for_removal = []

        for index, comment in enumerate(current_list):
            # the instances should be at the end so should be fine
            if isinstance(comment, MoreComments):

                current_queued_for_removal.append(index)

                # save any MoreComment objects not in use
                if comment not in self.used_morecomments:
                    unused_morecomments.append(comment)
                continue

            # if this comment exists in new_comments list, update the current comment and queue
            # index in new_comments list for deletion. Doing it this way so we can
            # reverse the list and delete backwards (works well for large new_comments)
            # with lots of duplicate comments
            current_comment_index = temp_comment_sortable_list.get(comment.id)
            if current_comment_index is not None:

                current_list[index] = new_comments[current_comment_index]
                queued_for_removal.append(current_comment_index)

        # remove comments from new comments list that have already replace ones in current list
        queued_for_removal = sorted(queued_for_removal)
        for removal in reversed(queued_for_removal):
            del new_comments[removal]

        for removal in reversed(current_queued_for_removal):
            del current_list[removal]

        # add on the unused more_comments to the new_comments list
        # and then append whats left in the new_comments list to the
        # current list
        new_comments.extend(unused_morecomments)
        current_list.extend(new_comments)

        self.flattened_post = copy.deepcopy(current_list)

        # split into x size lists
        await self.create_pages(iterable=current_list)

    async def return_embed(self, page):
        try:
            await self.check_current_page_comments()

            if len(self.pages) - 1 < page:
                if len(self.pages) - 1 >= self.current_page:
                    page = self.current_page

                else:
                    page = 0

            #print(page)
            #print(len(self.pages) - 1)
            #print(self.current_page)
            self.current_embed = RedditCommentEmbed()
            self.current_embed.create_embed(comments=self.pages[page],
                                            title=self.SUBMISSION_TITLE,
                                            url=self.SUBMISSION_URL,
                                            post_type=self.SUBMISSION_TYPE,
                                            preview=self.SUBMISSION_PREVIEW,
                                            footer_message= "Last Updated: " + self._last_updated + " | Page " + str(page)

                                            )
            for x in range(0, len(self.apply_emojis)):

                self.apply_emojis[x][next(iter(self.apply_emojis[x]))] = True

        except NoCommentsException:
            self.current_embed = RedditErrorEmbed()
            self.current_embed.create_embed(title="No Comments Recieved",
                                            description="No Comments recieved for post " + str(self.SUBMISSION_TITLE)[:20])
            

            # only apply delete emoji
            for x in range(0, len(self.apply_emojis)):
                if next(iter(self.apply_emojis[x])) != 'delete':
                    self.apply_emojis[x][next(iter(self.apply_emojis[x]))] = False

        return self.current_embed.get_embed()

    async def check_current_page_comments(self):

        try:
            for comment in self.pages[self.current_page]:

                if isinstance(comment, MoreComments):
                    self.used_morecomments.append(comment)
                    await self.get_more_comments(comment)
                    #print(comment)

                    print("getting more comments as we have hit a more comments object")
                    await self.update_pages()

                    await self.check_current_page_comments()
                    return
                    # time to grab some more comments

                # TODO: shortening stuff
        except IndexError: # we've hit the end of the comments or that page doesn't exist. 
            if len(self.pages) == 0:
                # hey we actually don't have any pages
                raise NoCommentsException

            #print("Pages: " + str(self.pages))
            if self.current_page > 0:
                self.current_page = self.current_page - 1

            await self.check_current_page_comments()

        # if a comment is a more comments, request new comments, update pages, call the method again

    async def get_more_comments(self, mc_object:MoreComments):
        # TODO: Error Handling
        try:
            loop = asyncio.get_event_loop()

            def get_from_reddit():
                red = Reddit(self.reddit)
                return red.get_more_comments(mc_object)
            
            future = loop.run_in_executor(None, get_from_reddit)
            self.__comments = await future

        except UnknownException as e:
            print("Unknown Exception! " + str(e))
            # TODO: have some kind of warning on screen

    async def get_initial_comments(self):

        # TODO: Error Handling
        loop = asyncio.get_event_loop()

        def get_from_reddit():
            red = Reddit(self.reddit)
            return red.get_comments_by_list(self.SUBMISSION_ID)

        future = loop.run_in_executor(None, get_from_reddit)
        self.__initial_comments = await future
        self.__comments = copy.deepcopy(self.__initial_comments)
        self.flattened_post = copy.deepcopy(self.__comments)
        await self._update_last_updated()

    async def next_page(self, discord_object, num_pages=1):  # returns embed with comments of the next page
        embed = self.current_embed
        await self.send_message(discord_object, embed.edit_footer("Loading more comments... please wait a moment"))
        
        self.current_page = self.current_page + num_pages
        embed = await self.return_embed(self.current_page)
        await self.send_message(discord_object, embed)

    async def prev_page(self, discord_object, num_pages=1):  # returns embed with comments of previous page
        embed = self.current_embed
        
        if self.current_page > 0:
            self.current_page = self.current_page - num_pages
            await self.send_message(discord_object, embed.edit_footer("Loading previous comments... please wait a moment"))
        else:
            await self.send_message(discord_object, embed.edit_footer("There are no more previous comments!"))
        embed = await self.return_embed(self.current_page)
        await self.send_message(discord_object, embed)

    async def goto_page(self, discord_object, page:int):
        if self.current_embed is not None:
            embed = self.current_embed
            await self.send_message(discord_object, embed.edit_footer("Going to page " + str(page) + "... please wait a moment"))
        # pages start at 0
        if page < 0:  # if somehow below 0 accidentally passed in.
            page = 0
        if len(self.pages) >= page + 1:
            self.current_page = page
        embed = await self.return_embed(self.current_page)
        await self.send_message(discord_object, embed)

    async def refresh(self, discord_object):
        embed = self.current_embed
        await self.send_message(discord_object, embed.edit_footer("Refreshing with latest comments... please wait a moment"))
        self.__initial_comments = []
        self.__comments = []

        self.pages = []
        self.current_page = 0
        self.current_page_comments = []
        self.current_morecomment_depth = 0  # amount of more comment instances we have used so far
        self.current_embed = None

        # more comments stuff
        self.used_morecomments = []

        self.flattened_post = []
        await self.get_initial_comments()
        await self.create_pages()
        return await self.goto_page(discord_object, 0)

    async def send_message(self, discord_object, embed):

        if self.message is not None:
            await discord_object.edit_message(self.message, embed=embed)
        else:
            print("sending message")
            if self.manual_message is not None:
                self.message = self.manual_message
                self.manual_message = None
                await discord_object.edit_message(self.message, embed=embed)
            else:
                self.message = await discord_object.send_message(self.channel, embed=embed)

            for x in range(0, len(self.apply_emojis)):
                if self.apply_emojis[x][next(iter(self.apply_emojis[x]))]:
                    await discord_object.add_reaction(self.message, str(self.emojis[next(iter(self.apply_emojis[x]))]))

    async def delete_message(self, discord_object):
        await discord_object.delete_message(self.message)

    async def _update_last_updated(self):
        self._last_updated = str(strftime("%Y-%m-%d %H:%M:%S", gmtime())) + " GMT" 
