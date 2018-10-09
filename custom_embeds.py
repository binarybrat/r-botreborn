import discord
from exceptions import EmbedNotExistError

from math import floor, ceil
import sys
import copy
"""

REDDIT EMBED TEMPLATES

"""


class RedditPostEmbed:

    def __init__(self):
        self._colour = 0x992d22
        self._reddit_icon_url = 'https://www.redditstatic.com/desktop2x/img/favicon/apple-icon-57x57.png'
        self._embed = None

        # some length restrictions 
        self.MAX_FIELD_LENGTH = 1024
        self.MAX_FOOTER_LENGTH = 100
        self.MAX_CHEADER_LENGTH = 100
        self.MAX_TITLE_LENGTH = 256
        self.MAX_NUM_FIELDS = 25
        self.MAX_EMBED_LENGTH = 6000

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
        self._update_time = None
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
        custom_message = str(kwargs.get('custom_message', 'Getting posts... This will take a moment'))
        footer_text = str(kwargs.get('footer_text', "Randomising through " + str(post_count) + " posts from r/" + str(subreddit)))
        self._embed = discord.Embed(title=custom_message,
                                    colour=self._colour).set_footer(text=footer_text)


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
        footer_message = kwargs.get('footer_message', " ")
        current_length_left = self.MAX_EMBED_LENGTH
 
        if len(comments) > self.MAX_NUM_FIELDS:
            comments = comments[:self.MAX_NUM_FIELDS - 1]
        # CONSTRUCTING AND CALCULATING THE TITLE SIZE

        if post_media_type is not None:
            p3_type = " [" + str(post_media_type) + "]"
        else:
            p3_type = ""

        p1 = "Comments for: "
        max_ctitle_length = self.MAX_TITLE_LENGTH - (len(p1) + len(p3_type)) # length of the title comes last, type and p1 more priority
        
        if len(post_title) > max_ctitle_length:
            post_title = (post_title[:max_ctitle_length - 6] + '(...)')

        if len(footer_message) > self.MAX_FOOTER_LENGTH:
            footer_message = footer_message[:self.MAX_FOOTER_LENGTH - 1]

        checked_title = p1 + post_title + p3_type
        current_length_left = current_length_left - len(checked_title) - len(footer_message)
        #print(current_length_left)

        self._embed = discord.Embed(title=checked_title, url=post_link, colour=self._colour, inline=False)

        if preview is not None:
            if "http" in preview.lower():
                self._embed.set_thumbnail(url=preview)

        extracted_comment_info = {}

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

                author_length = len(str(comment.author))
                if comment.author_flair_text:
                    flair_length = len(str(comment.author_flair_text))
                else:
                    flair_length = 0
                # if both are under max_comment_header then its fine if one is longer than 50. 
                if (author_length + flair_length) > self.MAX_CHEADER_LENGTH - 6: # -5 here because of the u/ and space, two `` 
                    if author_length > (self.MAX_CHEADER_LENGTH/2):
                        comment.author = str(comment.author)[:(self.MAX_CHEADER_LENGTH/2) - 3] # -3 because of u/

                    if flair_length > (self.MAX_CHEADER_LENGTH/2):
                        comment.author_flair_text = str(comment.author_flair_text)[:(self.MAX_CHEADER_LENGTH/2) - 4] # -4 here because of space and ` ` that will be added

                if comment.author_flair_text:
                    comment.author_flair_text = " `" + str(comment.author_flair_text) + "`"
                else:
                    comment.author_flair_text = ""


                name = op_text + " u/" + str(comment.author) + comment.author_flair_text # I know we have op_text here, we won't count that towards max length
                
                # now calculating the footer of the comment

                comment_footer = "\n\n [L](" + str(comment.permalink) + ") `Score: " + str(comment.score) + " | " + str(comment.created_utc) + " GMT " + str(edited_text) + gilded_text + "`"
                
                current_length_left = current_length_left - len(comment_footer) - len(name)

                #print("Current length left" + str(current_length_left))

                extracted_comment_info[str(comment.id)] = {'header': name,
                                                            'footer': comment_footer, 
                                                            'body': str(comment.body), 
                                                            'body_length': len(str(comment.body)),
                                                            'footer_length': len(comment_footer),
                                                            'allowed_length': 0,
                                                            }

                
            except IndexError: # TODO: check this
                pass

       # print(extracted_comment_info)
        
        recommended_comment_size = floor((current_length_left)/(len(extracted_comment_info))) # round this to lowest int to be safe 
        
        

        processed_comments = {}
       # print("Processed Comments = "  +str(processed_comments))
       # print("Recommended Comment Size = " + str(recommended_comment_size))
        extracted_to_delete = []
        free_char_spaces = 0

        # deciding what comments we are saving
        for key, value in extracted_comment_info.items(): 
          #  print("each comment:")
         #   print(str(key) + str(value))# for each comments
            

            # for comments that are below the reconmended and are totally safe
            # so this would be comments that are:

            # comment_size < recommended:
            #   add extra space to free_char_spaces - so if recommened was > 1024, we'll grab all the space the comment doesn't take up. 
            # -- only issue with this is that if comment recon is > 1024 then none of the comments will be ablke to utilize that space. But we 
            # -- still want accurate sizing
            # but then check if the comment_size is below or equal to recommended_max_size - comment_footer_size
            # if it is equal to: add to the all clear list
            # if not, do nothing so it will be processed. 
          #  print(str(value.get('body_length')) + "  < " + str(recommended_comment_size))
            if value.get('body_length') < recommended_comment_size:
                possible_free_sizes = recommended_comment_size - value.get('body_length')
               # print("Possible Free Sizes from this comment: " + str(possible_free_sizes))
                if possible_free_sizes > 0: # if this ever goes into negative we'll catch that (should never). If it is negative then we dont add anything. 
                    free_char_spaces = free_char_spaces + possible_free_sizes

                # basically check if the comment is greater than what can fit in the field
               # print(str(value.get('body_length')) + " plus " + str(value.get('footer_length')) + "  <= " + str(self.MAX_FIELD_LENGTH))
                if value.get('body_length') + value.get('footer_length') <= self.MAX_FIELD_LENGTH:
                  #  print(str(value.get('body_length')) + " plus " + str(value.get('footer_length')) + " IS  <= " + str(self.MAX_FIELD_LENGTH))
                    # its safe
                    #processed_comments() (comment) # comments that are good
                    #extracted_to_delete # remove it from raw comments list
                   # print("This comment is totally safe, adding it to processed comments and deleting it")
                    #print(comment)
                    
                    processed_comments[key] = value
                    extracted_to_delete.append(key)
                    

                #else:
                   # print(str(value.get('body_length')) + " plus " + str(value.get('footer_length')) + " IS  NOT <= " + str(self.MAX_FIELD_LENGTH))
                   # print("that comment is not safe")


            #else:

              #  print(str(value.get('body_length')) + " IS NOT  < " + str(recommended_comment_size))
               # print("that comment is definitly not safe")
            # and now we will delete the good comments in raw comments list
        
       # print("Free Char Spaces Available: "+ str(free_char_spaces))
        
        # remove already safe/processed comments from the main comment list
        if len(extracted_to_delete) > 0:
            for key in extracted_to_delete:
                extracted_comment_info.pop(key)


       # print("Extracted Comment Info Size:")
       # print(len(extracted_comment_info))
       # print("extracted comment info / comments left::")
       # print(extracted_comment_info)


       # print("Processed Comments:")
       # print(processed_comments)


        # if there are comments left to shorten we are going to deal with them
        if len(extracted_comment_info) > 0:
            

          #  print("getting sorted sizes")
            #free_char_spaces = 1
            if free_char_spaces > 0:
              #  print("There is character spaces available.")
                extracted_comment_info = self.__share_chars_csort(extracted_comment_info, free_char_spaces, recommended_comment_size)

            else:
             #   print("There are no spaces available so cutting down to reconmended. ")
                for key, value in extracted_comment_info.items():
                    extracted_comment_info[key]['allowed_length'] = recommended_comment_size
                    if extracted_comment_info[key]['allowed_length'] + extracted_comment_info[key]['footer_length'] > self.MAX_FIELD_LENGTH:
                        extracted_comment_info[key]['allowed_length'] = self.MAX_FIELD_LENGTH - extracted_comment_info[key]['footer_length']


         #   print("So the final comments (not shoirtened yet) are") 
         #   print(str(extracted_comment_info)) 

         #   print("there are no free characters available")



            # TIME FOR THE ACTUAL TRIMMING


            for key in extracted_comment_info:
                extracted_comment_info[key]['body'] = str(extracted_comment_info[key]['body'])[:int(extracted_comment_info[key]['allowed_length']) - 6] + " (...)"
                processed_comments[key] = extracted_comment_info[key]
            

         # update the time
        for comment_id, value in processed_comments.items():
            #print(processed_comments)
          #  print(value)
            self._embed.add_field(name=value.get('header'), value=str(value.get('body')) + str(value.get('footer')), inline=False)
            # indexs_max_size -> extracted_to_delete

        self._embed.set_footer(icon_url=self._reddit_icon_url, text=footer_message)

       
    def __share_chars_csort(self, comments:dict, free_char_spaces:int, recommended_comment_size:int):
        
            extra_free_char = 0
            delete_from_legal = []
            legal_comments = copy.deepcopy(comments) # create a copy of the comments so we can work with them
            if len(legal_comments) > 0:
                # share out the free character spaces
                comment_extra_size = self.__share_chars_calculation(legal_comments, free_char_spaces) # share out the free character spaces
                #print(legal_comments)
                i = 0
                for key, value in legal_comments.items(): # iterate through all the 'legal' comments
                    print("Comment Reconmended size: " + str(recommended_comment_size))
                    length = int(legal_comments[key]['allowed_length']) + comment_extra_size[i] + recommended_comment_size
                    
                    i = i + 1
                    #print("New Length: " + str(length))
                    
                    #print(key)

                    #if int(value.get('body_length')) + length + int(value.get('footer_length')) > max_field_length: # the new length is too long, shorten to the max and remove it
                    if length + int(value.get('footer_length')) > self.MAX_FIELD_LENGTH:
                        #print("the new length plus the footer length is longer than the maximum allowed for a field")
                        length_ori = length
                        length = self.MAX_FIELD_LENGTH - int(value.get('footer_length'))
                        
                       # print("New Length now is " + str(length))
                        extra_free_char = extra_free_char + (length_ori - length)
                       # print("Extra Free Char is " + str(extra_free_char))
                        if extra_free_char < 0:
                            extra_free_char = 0

                         #   print("Its 0 WUT, Extra Free Char is " + str(extra_free_char))
                        #length = max_field_length - int(value.get('footer_length')) - int(value.get('body_length')) # this is calculating the final length :/ now should be the extra max length
                        delete_from_legal.append(key)
                       # print("Adding to delete from legal: " + str(key))

                    elif length + int(value.get('footer_length')) == self.MAX_FIELD_LENGTH: # == 1024, we dont need to do anything more
                        delete_from_legal.append(key)
                    comments[key]['allowed_length'] = length

                for key2 in delete_from_legal: # removed processed comments
                    legal_comments.pop(key2)

                if extra_free_char > 0 and len(legal_comments) > 0: # hey we still have some points to share out
                    #print("recusing again cause still fre char and legal comments")
                    newer_comments = self.__share_chars_csort(legal_comments, extra_free_char, recommended_comment_size)

                    for key3, value3 in newer_comments.items():
                        comments[key3] = value3
           # else:
               # print("There are no legal comments. Meaning no comments were passed in...")

            return comments

    # calculate the amount of free characters we can give comments
    # returns a list in format [numlower, numlower, numlower, numupper...] etc
    @staticmethod
    def __share_chars_calculation(comments_dict, free_char_spaces):
        numcomments = len(comments_dict)
        comment_extra_size = []
        if numcomments > 0 and free_char_spaces > 0:
           # print("Number of comments: " + str(numcomments))
            upper = ceil(free_char_spaces/numcomments)
            lower = floor(free_char_spaces/numcomments)

           # print("Upper: " + str(upper))
          #  print("Lower: " + str(lower))
            remainder = free_char_spaces - (lower * numcomments)
            numupper = remainder
            numlower = numcomments - remainder
           # print("Num Upper: " + str(numupper))
           # print("Num lower: " + str(numlower))

            for x in range(0, numupper):
                comment_extra_size.append(upper)
                
            for x in range(numupper, numcomments):
                comment_extra_size.append(lower)
        else:
            
                comment_extra_size = [0 for i in range (0, numcomments)]

    
        return comment_extra_size   

    def edit_footer(self, message):
        if self._embed is not None:
            self._embed.set_footer(icon_url=self._reddit_icon_url, text=str(message))
        return self._embed

    

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
        extra_info = kwargs.get('extra', "")

        if extra_info is not "":
            extra_info = " | " + str(extra_info)

        self._embed = discord.Embed(title=title, description=description, colour=self._colour)
        self._embed.set_footer(icon_url=self._ICON_URL, text="gfycat" + extra_info)




