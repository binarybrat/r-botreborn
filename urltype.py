
class UrlType:

    
    """
    usage example:
    image_type = UrlType("url").get_url_type()

    """

    def __init__(self, image_url):

        self.url = image_url.lower()
        self.possible_video_types = [".mov", ".mp4", ".webm", ".mpeg", ".gifv"] # video extensions
        self.possible_image_types = [".jpg", ".jpeg", ".png"] # image extensions

    def get_url_type(self):

        if self.check_image_types():
            return "image"
            # is an image

        elif self.check_video_types():
            return "video"

        elif "v.redd.it" in self.url:
            return "video"

        elif self.url.endswith(".gif") or self.url.__contains__(".gif"):
            return "gif"

        elif "youtube" in self.url or "youtu.be" in self.url: # TODO: rewrite using the domain given by reddit
            return "youtube"

        elif "gfycat" in self.url:
            return "gfycat"

        elif "imgur" in self.url:
            return "imgur"

        elif "vimeo" in self.url:
            return "vimeo"
        elif "reddit" in self.url:
            return "reddit"
        else:
            return "link"

    def check_video_types(self): # this should finish very fast so / shrug
        for video_format in self.possible_video_types:
            if self.url.endswith(video_format) or self.url.__contains__(video_format):
                return True # is a video format
        return False # not present

    def check_image_types(self):
        for image_format in self.possible_image_types:
            if self.url.endswith(image_format):
                return True # is a video format
        return False # not present

