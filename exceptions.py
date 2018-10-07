
"""

CUSTOM EXCEPTIONS

"""


class SubredditNotExist(Exception):
    pass


class SubredditIsNSFW(Exception):
    pass


class PostIsNSFW(Exception):
    pass


class NoPostsReturned(Exception):
    pass


class UnknownException(Exception):
    pass


class GfycatProcessError(Exception):
    pass


class GfycatMissingCredentials(Exception):
    pass


class GfycatInvalidCredentials(Exception):
    pass


class InvalidRedditURL(Exception):
    pass


class RedditOAuthException(Exception):
    pass


class EmbedNotExistError(Exception):
    pass


class NoCommentsException(Exception):
    pass