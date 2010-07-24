#This file contains all the DB Models used in the application

import datetime
from google.appengine.ext import db
from google.appengine.api import users

""" This is Blog(Category) model storing the unique blogname for each Blogpost Category.
	Any Blogpost that will be added will fall into any of the categories stored in this model"""
	
class Blog(db.Model):
	blogname = db.StringProperty(verbose_name='Blog Name', required=True)
	blogtitle = db.StringProperty(verbose_name='Blog Title', required=True)
	hasperm = db.BooleanProperty(verbose_name='Permission', required=True)

	def get_absolute_url(self):
		return "/category/%s/" % self.blogname

""" This model represents the Blogposts. """
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
			return self.posttext[:500] + "<a href='/post/%s/'>more</a>" % self.post_id
		else:
			return self.posttext

	def get_absolute_url(self):
		return "/post/%s/" % self.post_id

#Comments Model for managing comments.

class Comments(db.Model):
	blogpost = db.ReferenceProperty(Blogpost, collection_name='comments')
	commentid = db.IntegerProperty(required=True)
	commenttext = db.TextProperty(required=True)
	commentby = db.UserProperty(auto_current_user_add=True)
	commenton = db.DateTimeProperty(auto_now_add=True)

	def get_absolute_url(self):
		return "/post/%s/#comments" % self.blogpost.post_id

#Datamodel for BUZZ Acess Token
""" This Model first stores the request_token obtained by the service provider and is subsequently replaced by the
	access_token after authorization. Actually request_token should be stored in 'session' but ass GAE doesn't provide
	service for sessions I've stored it in db.But this approach should not be followed as it gives rise to a bug"""
class TokenStore(db.Model):
	buzzuser = db.UserProperty()
	buzzuserid = db.StringProperty(required=True)
	tokenkey = db.StringProperty(required=True)
	tokensecret = db.StringProperty(required=True)
	tokentype = db.StringProperty(required=True)