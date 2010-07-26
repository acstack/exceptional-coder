# General utilities for the application

from datamodels import TokenStore, Blogpost, Comments
from google.appengine.ext import db
from google.appengine.api import users
import consumer
import datetime

def checkValidity(params):
	errors = {}
	for key, value in params.iteritems():
		if value == '' or value == None:
			errors[key] = 'Required'
	return errors

def getPid_for_Post():
	p_list = db.GqlQuery("select * from Blogpost")
	pid = 1
	for p in p_list:
		if p.post_id > pid:
			pid = p.post_id
	pid = pid +1
	return pid

def getCommentId():
	c_list = db.GqlQuery("select * from Comments")
	cid = 1
	for c in c_list:
		if c.commentid > cid:
			cid = c.commentid
	cid = cid + 1
	return cid

import buzz
class BuzzHandler:
	def __init__(self, user):
		self.user = user
		self.uid = user.user_id()
		avail = db.GqlQuery("select * from TokenStore where buzzuser = :1 and buzzuserid =:2 and tokentype = :3", self.user, self.uid, 'access_token')
		self.utdata = avail.get()
		self.client = None

	def is_user_authenticated(self):
		if self.utdata is None:
			return False
		tkey = self.utdata.tokenkey
		tsecret = self.utdata.tokensecret
		#Building and Authenticating the Client
		self.client = buzz.Client()
		self.client.build_oauth_consumer(consumer.CONSUMER_KEY, consumer.CONSUMER_KEY_SECRET)
		self.client.oauth_scopes.append(buzz.FULL_ACCESS_SCOPE)
		self.client.build_oauth_access_token(tkey, tsecret)
		return True

	def get_consumption_feed(self):
		result = self.client.posts(type_id='@consumption', max_results=10) #User Consumption feed
		result.data #Setting the data property of the result object
		return result._parse_posts(result._json) #returning the list of posts

	def get_user_followers(self):
		result = self.client.followers()
		result.data
		return result._parse_people(result._json)
	
	def create_buzz_post(self, mes):
		post = buzz.Post(content=mes)
		self.client.create_post(post)

""" This method clears all the request_tokens that are stored in the db resulting from incomplete oauth request"""
def clear_previous_request_tokens(user):
	uid = user.user_id()
	qkey = db.GqlQuery("select __key__ from TokenStore where buzzuserid = :1 and tokentype = :2", uid, 'request_token')
	for q in qkey:
		db.delete(q)

# Classes below handles Archive for posts
class BlogArchive:
	def __init__(self):
		self.a_years = [2010, 2011, 2012]
		self.cur_year = datetime.date.today().year
	
	def get_archive_year_list(self, year):
		ar_year_list = []
		for a_year in self.a_years:
			if a_year <= self.cur_year:
				if year == a_year:
					ar_year_list.append(ArchiveYear(a_year, cur_year=True))
				else:
					ar_year_list.append(ArchiveYear(a_year))
		return ar_year_list

class ArchiveYear:
	def __init__(self, a_year, cur_year=False):
		self.a_year = a_year
		self.cur_year = cur_year
		self.a_months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

	def get_archiveyear_url(self):
		return "/archive/%s/" % str(self.a_year)
	
	def archive_month_list(self):
		ar_month_list = []
		for a_month in self.a_months:
			if (self.a_year == datetime.date.today().year and self.a_months.index(a_month) + 1 > datetime.date.today().month) or (self.a_year == 2010 and self.a_months.index(a_month) + 1 < 7):
				pass
			else:
				ar_month_list.append(ArchiveMonth(self.a_year, a_month))
		return ar_month_list

	def is_current_year(self):
		return self.cur_year

class ArchiveMonth:
	def __init__(self, a_year, a_month):
		self.a_year = a_year
		self.a_month = a_month

	def get_archivemonth_url(self):
		return "/archive/%s/%s/" % (str(self.a_year), self.a_month)
