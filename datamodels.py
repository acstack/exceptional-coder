import datetime
from google.appengine.ext import db
from google.appengine.api import users

class Blog(db.Model):
	blogname = db.StringProperty(verbose_name='Blog Name', required=True)
	blogtitle = db.StringProperty(verbose_name='Blog Title', required=True)
	hasperm = db.BooleanProperty(verbose_name='Permission', required=True)

	def get_absolute_url(self):
		return "/category/%s/" % self.blogname

class Blogpost(db.Model):
	blog = db.ReferenceProperty(Blog, collection_name='blogposts')
	post_id = db.IntegerProperty(required=True)
	posttitle = db.StringProperty(verbose_name='Post Title', required=True)
	posttext = db.TextProperty(verbose_name='Post Text', required=True)
	poston = db.DateTimeProperty(auto_now_add=True)
	postby = db.UserProperty(auto_current_user_add=True)
	
	def get_limited_text(self):
		length = len(self.posttext)
		if length > 500:
			return posttext[:500] + "<a href='/post/%s/'>more</a>" % self.post_id
		else:
			return self.posttext

	def get_absolute_url(self):
		return "/post/%s/" % self.post_id

class Comments(db.Model):
	blogpost = db.ReferenceProperty(Blogpost, collection_name='comments')
	commentid = db.IntegerProperty(required=True)
	commenttext = db.TextProperty(required=True)
	commentby = db.UserProperty(auto_current_user_add=True)
	commenton = db.DateTimeProperty(auto_now_add=True)

	def get_absolute_url(self):
		return "/post/%s/#comments" % self.blogpost.post_id