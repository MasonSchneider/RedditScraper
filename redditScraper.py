import urllib2
import urllib
import json
import os
import time
import sys
import re
import math


def getHot(subreddit, limit = "25"):
	req = urllib2.urlopen("http://www.reddit.com/r/"+subreddit+"/top/.json?limit="+limit)
	time.sleep(5);
	js = json.load(req)
	if not os.path.exists("dump"): os.makedirs("dump")
	for i in range(0,len(js['data']['children'])):
		author = js['data']['children'][i]['data']['author']
		title = js['data']['children'][i]['data']['title']
		src = js['data']['children'][i]['data']['url']		
		title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
		if len(title) > 50:
			title = title[-50:]
		if src.endswith(".jpg") or src.endswith(".gif") or src.endswith(".png"):
			if not os.path.exists("dump\\"+author): os.makedirs("dump\\"+author)
			urllib.urlretrieve(src, "dump\\"+author+"\\"+title + src[-4:])
			time.sleep(2)
			getUserSubs(author, subreddit)
		elif "/a/" not in src:
			if not os.path.exists("dump\\"+author): os.makedirs("dump\\"+author)
			urllib.urlretrieve(src+".jpg", "dump\\"+author+"\\"+title+".jpg")
			time.sleep(2)
			getUserSubs(author, subreddit)
		else:
			if not os.path.exists("dump\\"+author): os.makedirs("dump\\"+author)
			try:
				time.sleep(3)
				downloader = ImgurAlbumDownloader(src, output_messages=True)
				albumFolder = "dump\\"+author+"\\"
				time.sleep(3)
				downloader.save_images(albumFolder)
			except ImgurAlbumException as e:
				print "Error: " + e.msg
				print ""
				print help_message
			getUserSubs(author, subreddit)
			
def getUserSubs(user, sub):
	print "Processing " + user + "..."
	sys.stdout.flush()
	time.sleep(10)
	try:
		reqest = urllib2.urlopen("http://www.reddit.com/user/"+user+"/submitted/.json?limit=90")
	except:
		return getUserSubs(user,sub)
	time.sleep(2)
	js = json.load(reqest)
	for i in range(0,len(js['data']['children'])):
		if js['data']['children'][i]['data']['subreddit'] == sub:
			title = js['data']['children'][i]['data']['title']
			src = js['data']['children'][i]['data']['url']
			title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
			if len(title) > 50:
				title = title[-50:]
			if src.endswith(".jpg") or src.endswith(".gif") or src.endswith(".png"):
				urllib.urlretrieve(src, "dump\\"+user+"\\"+title + src[-4:])
			elif "/a/" not in src:
				urllib.urlretrieve(src+".jpg", "dump\\"+user+"\\"+title+".jpg")
			else:
				try:
					time.sleep(4)
					downloader = ImgurAlbumDownloader(src, output_messages=True)
					albumFolder = "dump\\"+user+"\\"
					time.sleep(4)
					downloader.save_images(albumFolder)
				except ImgurAlbumException as e:
					print "Error: " + e.msg
					print ""
					print help_message



help_message = '''
Quickly and easily download an album from Imgur.

Format:
$ python imguralbum.py [album URL] [destination folder]

Example:
$ python imguralbum.py http://imgur.com/a/uOOju#6 /Users/alex/images

If you omit the dest folder name, the utility will create one with the same name as the
album (for example for http://imgur.com/a/uOOju it'll create uOOju/ in the cwd)

'''


class ImgurAlbumException(Exception):
    def __init__(self, msg=False):
        self.msg = msg


class ImgurAlbumDownloader:
    def __init__(self, album_url, output_messages=False):
        """
Constructor. Pass in the album_url. Seeing as this is mostly a shell tool, you can have the
class output messages too.
"""
        self.album_url = album_url
        self.output_messages = output_messages

        # Check the URL is actually imgur:
        match = re.match('(https?)\:\/\/(www\.)?imgur\.com/a/([a-zA-Z0-9]+)(#[0-9]+)?', album_url)
        if not match:
            raise ImgurAlbumException("URL must be a valid Imgur Album")

        self.protocol = match.group(1)
        self.album_key = match.group(3)

        # Read the no-script version of the page for all the images:
        noscriptURL = 'http://imgur.com/a/' + match.group(3) + '/noscript'
        self.response = urllib.urlopen(noscriptURL)

        if self.response.getcode() != 200:
            raise ImgurAlbumException("Error reading Imgur: Error Code %d" % self.response.getcode())

    def save_images(self, foldername=False):
        """
		Saves the images from the album into a folder given by foldername.
		If no foldername is given, it'll use the album key from the URL.
		"""
        html = self.response.read()
        self.images = re.findall('<img src="(\/\/i\.imgur\.com\/([a-zA-Z0-9]+\.(jpg|jpeg|png|gif)))"', html)

        if self.output_messages:
            print "Found %d images in album" % len(self.images)

        # Try and create the album folder:
        if foldername:
            albumFolder = foldername
        else:
            albumFolder = self.album_key

        if not os.path.exists(albumFolder):
            os.makedirs(albumFolder)

        # And finally loop through and save the images:
        for (counter, image) in enumerate(self.images, start=1):
            image_url = "%s:%s" % (self.protocol, image[0])
            if self.output_messages:
                print "Fetching Image: " + image_url
            prefix = "%0*d-" % (
                int(math.ceil(math.log(len(self.images) + 1, 10))),
                counter)
            path = os.path.join(albumFolder, prefix + image[1])
            urllib.urlretrieve(image_url, path)

        if self.output_messages:
            print ""
            print "Done!"


if __name__ == '__main__':
    getHot("wallpapers","90")
    