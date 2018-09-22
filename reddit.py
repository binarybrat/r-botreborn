import asyncio
import random
import time
from praw.exceptions import ClientException
from prawcore.exceptions import NotFound
import config
from exceptions import *
from urltype import UrlType

Config = config.Config('config.ini')


class Reddit:

    def __init__(self, praw_object):
        self._praw_object = praw_object

    async def get(self, **kwargs):
        subreddit = kwargs.get('subreddit', None)
        post_count = int(kwargs.get('post_count', Config.r_postcount))
        image = kwargs.get('get_image', None)
        nsfw = bool(kwargs.get('nsfw', False))
        comment_count = int(kwargs.get('comment_count', 0))
        request_type = kwargs.get('request_type', 'default')
        url = kwargs.get('url', None)
        loop = asyncio.get_event_loop()

        # check if we are authenticated with reddit correctly
        # try:
        #    self._praw_object.user.me()
        # except OAuthException as e:
        #    raise RedditOAuthException(str(e))
        # except AttributeError:
        #    raise RedditOAuthException
        # checking if the request is a url (for when we want to get a post from a url.# TODO: maybe post id?
        if request_type == 'url':  # subreddit is set to the url in this case

            print("Request Type is URL")

            def get_from_url():
                return self.__get_post_from_url(url)

            def get_the_comments():
                return self.get_comments(post_data.get('post_id'), comment_count)
            future10 = loop.run_in_executor(None, get_from_url)
            post_data = await future10

            if comment_count > 0:
                future11 = loop.run_in_executor(None, get_the_comments)
                comment_data = await future11
            else:
                comment_data = []
            return post_data, comment_data

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
            return self.__get_posts(subreddit, post_count, image, nsfw, comment_count)

        future3 = loop.run_in_executor(None, get_the_posts)
        posts = await future3

        # check if we actually have posts
        posts_length = len(posts)
        if posts_length < 1:
            raise NoPostsReturned(
                "No Posts Returned for subreddit " + str(subreddit) + " with a post count of " + str(post_count))
        # now we need to randomly grab a post

        random_post_num = random.randint(0, posts_length - 1)
        # grabbing the comments if requested

        if comment_count > 0:
            def get_the_comments():
                return self.get_comments(posts[random_post_num].get('post_id'), comment_count)

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
                # TODO: handle other errors that may arise

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

        print(self.__get_post_data(submission, post_type, url, str(submission.subreddit)))

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
                'created_utc': created_utc
                }

    def get_comments(self, post_id, comment_num):

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

                    total_length = total_length + len(str(submission.comments[x].body))

                    # check if the total length of all comments combined doesnt exceed a limit
                    # (discord has a limit, staying well below that) limiting to 1200

                    if total_length < 1200:
                        if not skip_comment:

                            # convert the time to human readable
                            submission.comments[x].created_utc = time.strftime('%Y-%m-%d %H:%M', time.gmtime(
                                int(submission.comments[x].created_utc)))

                            # change the link of the comment to full url
                            submission.comments[x].permalink = "https://reddit.com" + str(submission.comments[x].permalink)
                            comments.append(submission.comments[x])

                    else:
                        total_length = total_length - len(str(submission.comments[x].body))

            except IndexError:
                pass
            except Exception as e:
                raise UnknownException(str(e) + " COMMENTS")
                # TODO: if an exception for this, fix it

        return comments
