import asyncio
import random
import time
from praw.exceptions import ClientException
from prawcore.exceptions import NotFound
#import logging
import config
from exceptions import *
from urltype import UrlType
from praw.models import MoreComments
Config = config.Config('config.ini')


class Reddit:

    def __init__(self, praw_object):
        self._praw_object = praw_object

    async def get(self, **kwargs):
        subreddit = kwargs.get('subreddit', None)
        post_count = int(kwargs.get('post_count', Config.r_postcount))
        image = kwargs.get('get_image', None)
        nsfw = bool(kwargs.get('nsfw', False))
        request_type = kwargs.get('request_type', 'default')
        url = kwargs.get('url', None)
        loop = asyncio.get_event_loop()

        if request_type == 'url':  # subreddit is set to the url in this case

            print("Request Type is URL")

            def get_from_url():
                return self.__get_post_from_url(url)

            
            future10 = loop.run_in_executor(None, get_from_url)
            post_data = await future10

            return post_data

        # if not a url continue with normal post-grabbing
        if post_count > Config.r_maxpostcount:
            post_count = Config.r_maxpostcount

        # check if the subreddit exists, using do_req function to keep async shit however it works
        def do_req():
            return self.check_if_sub_exists(subreddit)

        # have to do some asyncio shit

        future = loop.run_in_executor(None, do_req)

        if_sub_exists = await future  # should be either True (exists) or False (doesnt exist)

        # if subreddit does not exist, raise an error
        if not if_sub_exists:
            raise SubredditNotExist(str(subreddit) + " does not exist (returned to search page)")

        # check if the sub is nsfw if requested for no nsfw stuff

        if not nsfw:
            def nsfw_req():
                return self.check_if_over18(subreddit)

            future2 = loop.run_in_executor(None, nsfw_req)
            result = await future2

            if result:
                raise SubredditIsNSFW(str(subreddit) + " is a NSFW subreddit")

        # now time for the fun stuff

        # grabbing the posts

        def get_the_posts():
            return self.__get_posts(subreddit, post_count, image, nsfw)

        future3 = loop.run_in_executor(None, get_the_posts)
        posts = await future3

        # check if we actually have posts
        posts_length = len(posts)
        if posts_length < 1:
            raise NoPostsReturned(
                "No Posts Returned for subreddit " + str(subreddit) + " with a post count of " + str(post_count))
        # now we need to randomly grab a post

        random_post_num = random.randint(0, posts_length - 1)

        # and finally return everything

        return posts[random_post_num]

    def check_if_sub_exists(self, subreddit):
        try:
            test = self._praw_object.subreddit(subreddit).new(limit=1)
            test.next()
            return True
        except Exception as e:
            if str(e) == "Redirect to /subreddits/search":
                return False
            else:
                raise UnknownException(str(e))
                # TODO: handle other errors that may arise

    def check_if_over18(self, subreddit):
        try:
            if self._praw_object.subreddit(subreddit).over18:
                return True
            return False
        except NotFound:
            # subreddit cannot be checked for 18+
            return False

    def __get_posts(self, subreddit, post_count, image, nsfw):

        posts = []

        for post in self._praw_object.subreddit(subreddit).hot(limit=post_count):
            skip_post = False
            post_url = str(post.url)
            post_author = str(post.author)
            if post.over_18 and not nsfw:
                skip_post = True
            # get the type of post (based on the URL)
            post_type = UrlType(post_url).get_url_type()  # TODO - this is a asynced class shit need to fix

            # if image is true, only get image based posts
            # if not, only get links and post
            # if None, any post type

            if image is not None:
                if image:
                    if post_type == "link" or post_type == "reddit":
                        skip_post = True
                else:
                    if post_type != "link" and post_type != "reddit":
                        skip_post = True

            # skip any posts with a blacklisted author
            if post_author in Config.r_ignore_users:
                skip_post = True

            # skip any mod posts if set
            if (post.distinguished == "moderator") and Config.r_skip_mod_posts:
                skip_post = True

            # skip any stickied posts if set
            if post.stickied and Config.r_skip_stickied_posts:
                skip_post = True

            # skip any removed posts
            if post.removal_reason is not None:
                skip_post = True

            # save this post

            if skip_post is False:
                posts.append(self.__get_post_data(post, post_type, post_url, subreddit))

        return posts

    def __get_post_from_url(self, url):
        try:
            submission = self._praw_object.submission(url=url)
        except ClientException as e:
            raise InvalidRedditURL("Invalid Reddit Submission URL. Details (ClientException): " + str(e))
        except NotFound as e:
            raise InvalidRedditURL("Invalid Reddit Submission URL. Details (NotFound Exception): " + str(e))
        except Exception as e:
            raise UnknownException("Unknown Exception when trying to get submission from URL. Maybe invalid url?")
        # get post type
        try:
            post_type = UrlType(submission.url).get_url_type()
        except NotFound as e:
            raise InvalidRedditURL("Invalid Reddit Submission URL. Details (NotFound Exception): " + str(e))
        # get post data

        #print(self.__get_post_data(submission, post_type, url, str(submission.subreddit)))

        return self.__get_post_data(submission, post_type, submission.url, str(submission.subreddit))

    def __get_post_data(self, post, post_type, post_url, subreddit):

        # check post length
        post_text = post.selftext
        post_title = post.title
        if len(post_text) > 1850:
            post_text = (post_text[:1850] + '... [go to link to read more]')

        # we also need to check the title length as discord embed titles are limited to 256 characters long

        if len(post_title) > 256:
            post_title = (post_title[:253] + '...')

        created_utc = int(post.created_utc)
        created_utc = time.strftime('%Y-%m-%d %H:%M', time.gmtime(created_utc))

        return {'post_id': str(post.id),
                'post_url': post_url,
                'post_author': str(post.author),
                'nsfw': bool(post.over_18),
                'post_title': str(post_title),
                'post_score': int(post.score),
                'post_length': len(post_text),
                'post_text': post_text,
                'post_type': post_type,
                'post_permalink': "https://reddit.com" + str(post.permalink),
                'post_subreddit': subreddit,
                'created_utc': created_utc,
                'post_preview': str(post.thumbnail),
                'gilded': int(post.gilded)

                }

   
    def get_comments_by_list(self, submission_id, **kwargs):

        submission = self._praw_object.submission(submission_id)
        return self.process_comments(submission.comments.list()[0:int(kwargs.get('max_comments', len(submission.comments.list())))])


    
    # Where MoreComments is a MoreComments object
    # gets the comments the MoreComments object represents
    def get_more_comments(self, morecomments):
       
       
        # # See PRAW docs for more info
        # # https://praw.readthedocs.io/en/latest/code_overview/other/commentforest.html#praw.models.comment_forest.CommentForest.replace_more
       
        if isinstance(morecomments, MoreComments):
            comments = morecomments.comments(update=True)
            return self.process_comments(comments)

    # Process the comments by editing them (e.g date formatting etc)
    @staticmethod
    def process_comments(comments):

        new_comments = []
        
        for comment in comments:

            # skip if it is a MoreComments Instance
            if isinstance(comment, MoreComments):
                new_comments.append(comment)
                continue

            try:
                #skip_comment = False
                
                if comment.author in Config.r_ignore_users:
                    continue # skip
                
                if comment.depth > 0: # only want top level comments at this stage
                    continue

                if Config.r_skip_stickied_comments and str(comment.stickied).lower() == "true":
                    print("Skipping comment as it is stickied")
                    continue

                # convert the time to human readable
                comment.created_utc = time.strftime('%Y-%m-%d %H:%M', time.gmtime(
                            int(comment.created_utc)))

                comment.permalink = "https://reddit.com" + str(comment.permalink)
                new_comments.append(comment)              

            except IndexError:
                pass
            except Exception as e:
                raise UnknownException(str(e) + " COMMENTS")
                # TODO: if an exception for this, fix it

       
        return new_comments

