import asyncio
import praw
import config
Config = config.Config('config.ini')
from time import sleep
import random
import time
from exceptions import *
from urltype import UrlType
from prawcore.exceptions import NotFound



class Reddit:

    def __init__(self, praw_object):
        self._praw_object = praw_object

    async def get(self, **kwargs):
        subreddit = kwargs.get('subreddit', None)
        post_count = int(kwargs.get('post_count', Config.r_postcount))
        image = kwargs.get('get_image', None)
        nsfw = bool(kwargs.get('nsfw', False))
        comment_count = int(kwargs.get('comment_count', 0))

        if post_count > Config.r_maxpostcount:
            post_count = Config.r_maxpostcount

        # check if the subreddit exists, using do_req function to keep async shit however it works
        def do_req():
            return self.check_if_sub_exists(subreddit)
        # have to do some asyncio shit
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(None, do_req)

        if_sub_exists = await future # should be either True (exists) or False (doesnt exist)

        # if subreddit does not exist, raise an error
        if not if_sub_exists:
            raise SubredditNotExist(str(subreddit) + " does not exist (returned to search page)")

        # check if the sub is nsfw if requested for no nsfw stuff

        if not nsfw:
            def nsfw_req():
                return self.check_if_over18(subreddit)
            future2 = loop.run_in_executor(None, nsfw_req)
            result = await future2
            print(result)
            if result:
                raise SubredditIsNSFW(str(subreddit) + " is a NSFW subreddit")

        # now time for the fun stuff

        # grabbing the posts

        def get_the_posts():
            return self.__get_posts(subreddit, post_count, image, nsfw, comment_count)
        future3 = loop.run_in_executor(None, get_the_posts)
        posts = await future3

        # check if we actually have posts
        posts_length = len(posts)
        print(posts)
        if posts_length < 1:
            raise NoPostsReturned("No Posts Returned for subreddit " + str(subreddit) + " with a post count of " + str(post_count))
        # now we need to randomly grab a post

        random_post_num = random.randint(0, posts_length -1)
        # grabbing the comments if requested


        if comment_count > 0:
            def get_the_comments():
                return self.__get_comments(posts[random_post_num].get('post_id'), comment_count)

            future4 = loop.run_in_executor(None, get_the_comments)
            comments = await future4
        else:
            comments = []

        # and finally return everything

        return posts[random_post_num], comments


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
                #TODO: handle other errors that may arise

    def check_if_over18(self, subreddit):
        try:
            if self._praw_object.subreddit(subreddit).over18:
                return True
            return False
        except NotFound:
            # subreddit cannot be checked for 18+
            return False

    def __get_posts(self, subreddit, post_count, image, nsfw, comment_count):

        posts = []

        for post in self._praw_object.subreddit(subreddit).hot(limit=post_count):
            skip_post = False
            # check if post is NSFW marked
            post_nsfw = post.over_18
            post_url = str(post.url)
            post_author = str(post.author)
            if post.over_18 and not nsfw:
                skip_post = True
            post_text = str(post.selftext)
            # get the type of post (based on the URL)
            post_type = UrlType(post_url).get_url_type() # TODO - this is a asynced class shit need to fix

            # if image is true, only get image based posts
            # if not, only get links and post
            # if None, any post type

            if image is not None:
                if image:

                    if post_type == "link" or post_type == "reddit":
                        print("skipping post due to being link")
                        print(post_type)
                        skip_post = True
                else:
                    if post_type != "link" and post_type != "reddit":
                        print("skipping post not due to being link " + str(post_type))
                        skip_post = True


            # skip any posts with a blacklisted author
            if post_author in Config.r_ignore_users:
                print("skipping post due ignore use")
                skip_post = True

            # skip any mod posts if set
            if (post.distinguished == "moderator") and Config.r_skip_mod_posts:
                skip_post = True
                print("skipping post due to being mod")

            # skip any stickied posts if set
            if post.stickied and Config.r_skip_stickied_posts:
                print("skipping post due to being skitcied")
                skip_post = True

            # skip any removed posts
            if post.removal_reason is not None:

                skip_post = True
                print("skipping post due to being removed")

            # save this post

            if skip_post is False:

                # check post length
                if len(post_text) > Config.r_post_length_discord:
                    post_text = (post_text[:Config.r_post_length_discord] + '... [go to reddit post to read more]')

                created_utc = int(post.created_utc)
                created_utc = time.strftime('%Y-%m-%d %H:%M', time.gmtime(created_utc))

                posts.append({'post_id': str(post.id),
                              'post_url':post_url,
                              'post_author':post_author,
                              'nsfw':bool(post_nsfw),
                              'post_title':str(post.title),
                              'post_score':int(post.score),
                              'post_length':len(post_text),
                              'post_text':post_text,
                              'post_type':post_type,
                              'post_permalink': "https://reddit.com" + str(post.permalink),
                              'post_subreddit':subreddit,
                              'created_utc':created_utc
                              })



        return posts


    # def __process_posts(self, posts):

    def __get_comments(self, post_id, comment_num):

        submission = self._praw_object.submission(id=str(post_id))

        # loop through comments
        comments = []
        total_length = 0
        for x in range(0, comment_num):

            try:
                skip_comment = False
                if submission.comments[x].author not in Config.r_ignore_users:

                    if Config.r_skip_stickied_posts and bool(submission.comments[x].stickied):
                        skip_comment = True

                    created_utc = int(submission.comments[x].created_utc)
                    created_utc = time.strftime('%Y-%m-%d %H:%M', time.gmtime(created_utc))

                    comment_body = str(submission.comments[x].body)
                    total_length = total_length + len(comment_body)

                    # check if the total length of all comments combined doesnt exceed a limit (discord has a limit, staying well below that)
                    print("Total Length is " + str(total_length))
                    if total_length < Config.r_comment_total_length:
                        if not skip_comment:
                            comments.append({'id':str(submission.comments[x].id),
                                             'body':str(submission.comments[x].body),
                                             'author':str(submission.comments[x].author),
                                             'score':int(submission.comments[x].score),
                                             'created_utc':created_utc,
                                             'link':"https://reddit.com" + str(submission.comments[x].permalink)})

                    else:
                        total_length = total_length - len(comment_body)
                        print("skipping post as exceeds set")
            except IndexError:
                pass
            except Exception as e:
                raise UnknownException(str(e) + " COMMENTS")
                #TODO: if an exception for this, fix it

        return comments