#Main file that handles all the requests

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from datamodels import *
from google.appengine.ext import db
from google.appengine.ext.webapp import template
import os
from utilities import *
import consumer

# Request Handlers for Admin Functionality

class HandleAdmin(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user == None:
			self.redirect(users.create_login_url(self.request.uri))
		if users.is_current_user_admin():
			self.redirect('/admin/manage/')

class AdminPage(webapp.RequestHandler):
	def get(self):
		if users.get_current_user():
			blog_list = db.GqlQuery("SELECT * FROM Blog")
			post_list = db.GqlQuery("SELECT * FROM Blogpost order by poston desc")
			url_link = users.create_logout_url('/')
			template_values = {
				'blog_list': blog_list,
				'post_list': post_list,
				'url_link': url_link,
				}
			path = os.path.join(os.path.dirname(__file__), 'templates/adminpage.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect(users.create_login_url('/'))

class AddBlog(webapp.RequestHandler):
	def get(self):
		if users.is_current_user_admin():
			url_link = users.create_logout_url('/')
			template_values = {'url_link': url_link, }
			path = os.path.join(os.path.dirname(__file__), 'templates/addblog.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')
	
	def post(self):
		if users.is_current_user_admin():
			params = {}
			params['blogname'] = self.request.get('blogname')
			params['blogtitle'] = self.request.get('blogtitle')
			params['hasperm'] = self.request.get('hasperm')
			url_link = users.create_logout_url('/')
			errors = checkValidity(params)
			if len(errors) > 0:
				template_values = {'url_link': url_link, 'errors': errors}
				path = os.path.join(os.path.dirname(__file__), 'templates/addblog.html')
				self.response.out.write(template.render(path, template_values))
			else:
				hp = False
				if params['hasperm'] == 'yes':
					hp = True
				blog = Blog(blogname=params['blogname'], blogtitle=params['blogtitle'], hasperm=hp)
				blog.put()
				self.redirect('/admin/manage/')
		else:
			self.redirect('/')

class AddPost(webapp.RequestHandler):
	def get(self):
		if users.is_current_user_admin():
			blog_list = db.GqlQuery("select * from Blog")
			url_link = users.create_logout_url('/')
			template_values = {'url_link': url_link, 'blog_list': blog_list}
			path = os.path.join(os.path.dirname(__file__), 'templates/addpost.html')
			self.response.out.write(template.render(path, template_values))
		else:
			self.redirect('/')

	def post(self):
		if users.is_current_user_admin():
			params = {}
			params['bname'] = self.request.get('bname')
			params['ptitle'] = self.request.get('ptitle')
			params['ptext'] = self.request.get('ptext')
			url_link = users.create_logout_url('/')
			errors = checkValidity(params)
			if len(errors) > 0:
				blog_list = db.GqlQuery("select * from Blog")
				template_values = {'url_link': url_link, 'errors': errors, 'blog_list': blog_list}
				path = os.path.join(os.path.dirname(__file__), 'templates/addpost.html')
				self.response.out.write(template.render(path, template_values))
			else:
				# Save the post
				pid = getPid_for_Post()
				blogs = db.GqlQuery("select * from Blog where blogname = :1", params['bname'])
				blog = blogs.get()
				bpost = Blogpost(blog=blog, post_id=pid, posttitle=params['ptitle'], posttext=params['ptext'])
				bpost.put()
				self.redirect('/admin/manage/')
		else:
			self.redirect('/')

# requestHandlers for the User Interfaces

class Homepage(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			url_link = users.create_logout_url('/')
			url_text = "logout"
		else:
			url_link = users.create_login_url(self.request.uri)
			url_text = "login"
		blog_list = db.GqlQuery("select * from Blog")
		post_list = db.GqlQuery("select * from Blogpost order by poston desc")
		#Getting Archives for the blog
		ba = BlogArchive()
		ar_year_list = ba.get_archive_year_list(datetime.date.today().year)
		template_values={
			'url_link': url_link,
			'url_text': url_text,
			'blog_list': blog_list,
			'post_list': post_list,
			'archive_list': ar_year_list,
			}
		if user:
			template_values['nick_name'] = user.nickname()
			#Clearing any earlier request_tokens resuting due to incomplete oauth requests(bug due to storing request_tokens in db)
			clear_previous_request_tokens(user)
			#Managing Buzz
			import buzz
			buzzhandle = BuzzHandler(user)
			if buzzhandle.is_user_authenticated():
				#Fetch BUZZ data for the user
				buzzposts = buzzhandle.get_consumption_feed()
				template_values['buzzposts'] = buzzposts
			else:
				template_values['gbuzz'] = 'ask_for'
		else:
			shtext = """Hi, there are a lot of things happening over here. Latest is the Google BUZZ integration with the application.
						You need to authenticate just once and you are ready to use all favourite BUZZ right here. Post, comment,
						update, delete and see all your friends updates. Login now with your Google Account"""
			template_values['shtext'] = shtext

		if users.is_current_user_admin():
			template_values['admin_link'] = '/admin/'
		path = os.path.join(os.path.dirname(__file__), 'templates/homepage.html')
		self.response.out.write(template.render(path, template_values))
	
	def post(self):
		mes = self.request.get('buzzpost', '')
		if mes == '' or mes is None:
			self.redirect('/')
		user = users.get_current_user()
		if user is not None:
			import buzz
			bh = BuzzHandler(user)
			if bh.is_user_authenticated():
				bh.create_buzz_post(mes)
				self.redirect('/')
		

#Request Handlers for User Interaction with the Application

class showcategory(webapp.RequestHandler):
	def get(self, bname):
		#print bname + "........."
		blogs = db.GqlQuery("select * from Blog where blogname = :1", bname)
		blog = blogs.get()
		post_list = blog.blogposts.order('-poston')
		blist = db.GqlQuery("select * from Blog")
		user = users.get_current_user()
		if user:
			url_link = users.create_logout_url('/')
			url_text = "logout"
		else:
			url_link = users.create_login_url(self.request.uri)
			url_text = "login"
		ba = BlogArchive()
		a_year = datetime.date.today().year
		archive_list = ba.get_archive_year_list(a_year)
		template_values = {
			'url_link': url_link,
			'url_text': url_text,
			'post_list': post_list,
			'category': blog,
			'blog_list': blist,
			'archive_list': archive_list,
			}
		if user:
			template_values['nick_name'] = user.nickname()
		path = os.path.join(os.path.dirname(__file__), 'templates/showcategory.html')
		self.response.out.write(template.render(path, template_values))

class showpost(webapp.RequestHandler):
	def get(self, pid):
		pid = int(pid)
		user = users.get_current_user()
		if user:
			url_link = users.create_logout_url('/')
			url_text = "logout"
		else:
			url_link = users.create_login_url(self.request.uri)
			url_text = "login"
		bposts = db.GqlQuery("select * from Blogpost where post_id = :1", pid)
		bpost = bposts.get()
		clist = bpost.comments.order('commenton')
		blog_list = db.GqlQuery("select * from Blog")
		ba = BlogArchive()
		a_year = datetime.date.today().year
		archive_list = ba.get_archive_year_list(a_year)
		template_values = {
			'url_link': url_link,
			'url_text': url_text,
			'bpost': bpost,
			'blog_list': blog_list,
			'comment_list': clist,
			'archive_list': archive_list,
			}
		if user:
			template_values['nick_name'] = user.nickname()
		path = os.path.join(os.path.dirname(__file__), 'templates/showpost.html')
		self.response.out.write(template.render(path, template_values))

#Handling Archive Calls
class HandleArchiveYear(webapp.RequestHandler):
	def get(self, a_year):
		a_year = int(a_year)
		from_date = datetime.datetime(a_year, 1, 1)
		to_date = datetime.datetime(a_year, 12, 31)
		post_list = db.GqlQuery("select * from Blogpost where poston >= :1 and poston <= :2", from_date, to_date)
		blog_list = db.GqlQuery("select * from Blog")
		user = users.get_current_user()
		if user:
			url_link = users.create_logout_url(self.request.uri)
			url_text = "logout"
		else:
			url_link = users.create_login_url(self.request.uri)
			url_text = "login"
		ba = BlogArchive()
		archive_list = ba.get_archive_year_list(a_year)
		template_values = {'url_link': url_link,
						'url_text': url_text,
						'post_list': post_list,
						'blog_list': blog_list,
						'archive_list': archive_list,
						'ar_year': a_year,
						}
		path = os.path.join(os.path.dirname(__file__), 'templates/yearwisearchive.html')
		self.response.out.write(template.render(path, template_values))

class HandleArchiveMonth(webapp.RequestHandler):
	def get(self, a_year, a_month):
		a_year = int(a_year)
		a_months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
		i_month = a_months.index(a_month)+1
		i_day = 30
		if i_month in [1, 3, 5, 7, 8, 10, 12]:
			i_day = 31
		if i_month == 2:
			i_day = 28
		from_date = datetime.datetime(a_year, i_month, 1)
		to_date = datetime.datetime(a_year, i_month, i_day)
		post_list = db.GqlQuery("select * from Blogpost where poston >= :1 and poston <= :2", from_date, to_date)
		blog_list = db.GqlQuery("select * from Blog")
		user = users.get_current_user()
		if user:
			url_link = users.create_logout_url(self.request.uri)
			url_text = "logout"
		else:
			url_link = users.create_login_url(self.request.uri)
			url_text = "login"
		ba = BlogArchive()
		archive_list = ba.get_archive_year_list(a_year)
		template_values = {'url_link': url_link,
						'url_text': url_text,
						'post_list': post_list,
						'blog_list': blog_list,
						'archive_list': archive_list,
						'ar_year': a_year,
						'ar_month': a_month,
						}
		path = os.path.join(os.path.dirname(__file__), 'templates/monthwisearchive.html')
		self.response.out.write(template.render(path, template_values))

class postcomment(webapp.RequestHandler):
	#request to this method comes via ajax
	def post(self):
		pid = self.request.get('pid')
		pid = int(pid)
		ctext = self.request.get('comtext')
		user = users.get_current_user()
		nusr = ""
		bposts = db.GqlQuery("select * from Blogpost where post_id = :1", pid)
		bpost = bposts.get()
		if user:
			cid = getCommentId()
			comment = Comments(blogpost=bpost, commentid=cid, commenttext=ctext)
			comment.put()
		else:
			nusr = "Please Login to post the Comment"
		restext = ""
		clist = bpost.comments.order('commenton')
		for c in clist:
			restext = restext + "<fieldset><legend style='font-size:20px'>" + c.commentby.nickname() + " said</legend>" + c.commenttext + "<div style='text-align:right'><i>Comment on " + str(c.commenton) + "</i></div></fieldset>"
		self.response.out.write(restext + nusr)

class aboutme(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			url_link = users.create_logout_url('/')
			url_text = "logout"
			nick_name = user.nickname()
		else:
			url_link = users.create_login_url(self.request.uri)
			url_text = "login"
		template_values = {
			'url_link': url_link,
			'url_text': url_text,
			}
		if users.is_current_user_admin():
			admin_link = '/admin/'
			template_values['admin_link'] = admin_link

		path = os.path.join(os.path.dirname(__file__), 'templates/aboutme.html')
		self.response.out.write(template.render(path, template_values))

# For Testing only
class deletecomments(webapp.RequestHandler):
	def get(self):
		if users.is_current_user_admin():
			comsk = db.GqlQuery("select __key__ from Comments")
			coms = comsk.fetch(10)
			for c in coms:
				db.delete(c)
			self.response.out.write("Comments Deleted")
		else:
			self.redirect('/')

#Handling BUZZ Authentication
class ConnectBUZZ(webapp.RequestHandler):
	def get(self):
		import buzz
		client = buzz.Client()
		client.build_oauth_consumer(consumer.CONSUMER_KEY, consumer.CONSUMER_KEY_SECRET)
		client.oauth_scopes.append(buzz.FULL_ACCESS_SCOPE)
		request_token = client.fetch_oauth_request_token('http://exceptionalcoder.appspot.com/buzzcallback/')
		#Saving the request token
		user = users.get_current_user()
		bid = user.user_id()
		tkey = request_token.key
		tsecret = request_token.secret
		token = TokenStore(buzzuser=user, buzzuserid=bid, tokenkey=tkey, tokensecret=tsecret, tokentype='request_token')
		token.put()
		#generate Authorization url
		auth_url = client.build_oauth_authorization_url()
		self.redirect(auth_url)

class BuzzCallback(webapp.RequestHandler):
	def get(self):
		import buzz
		verifier = self.request.get('oauth_verifier')
		user = users.get_current_user()
		uid = user.user_id()
		qtoken = db.GqlQuery("select * from TokenStore where buzzuserid = :1 and tokentype = :2", uid, 'request_token')
		token = qtoken.get()
		#print token
		client = buzz.Client()
		client.build_oauth_consumer(consumer.CONSUMER_KEY, consumer.CONSUMER_KEY_SECRET)
		client.oauth_scopes.append(buzz.FULL_ACCESS_SCOPE)
		client.build_oauth_request_token(token.tokenkey, token.tokensecret)		
		access_token = client.fetch_oauth_access_token(verifier)
		#saving the access_token
		token.tokenkey = access_token.key
		token.tokensecret = access_token.secret
		token.tokentype = 'access_token'
		token.put()
		#access_token saved redirecting to homepage
		self.redirect('/')

#Handling Buzz Operations

class BuzzOperation(webapp.RequestHandler):
	def get(self, reqtype):
		if reqtype == 'followers':
			#self.response.out.write("In requesttype" + reqtype)
			import buzz
			user = users.get_current_user()
			bh = BuzzHandler(user)
			if bh.is_user_authenticated():
				followers = bh.get_user_followers()
				restext = "<div style='width:99%;height:99%;text-align:right;color:green;background-image:url(/images/bgimg.jpg);overflow:auto'>"
				restext += "<b onclick='closeDiv()' style='cursor:pointer'>close</b>"
				restext += "<table cellspacing='1' cellpadding='2' width='100%'>"
				for p in followers:
					restext += "<tr><td width='40%'><img src='" + p.photo + "' alt='NA' width='50px' height='55px'></td><td><a href='" + p.uri +"'>" + p.name + "</a></td></tr>"
				restext += "</table></div>"
				self.response.out.write(restext)
			else:
				self.response.out.write("you are not authenticated")

# Creating the WSGI Application for this app

application = webapp.WSGIApplication([
									('/', Homepage),
									('/admin/', HandleAdmin),
									('/admin/manage/', AdminPage),
									('/admin/addblog/', AddBlog),
									('/admin/addpost/', AddPost),
									(r'^/category/([a-z]+)/$', showcategory),
									(r'^/post/(\d+)/$', showpost),
									('/comment/submit/', postcomment),
									('/comments/delete/', deletecomments),
									('/knowme/', aboutme),
									('/connect/googlebuzz/', ConnectBUZZ),
									('/buzzcallback/', BuzzCallback),
									(r'^/buzz/([a-z]+)/$', BuzzOperation),
									(r'^/archive/(\d+)/$', HandleArchiveYear),
									(r'^/archive/(\d+)/([a-zA-Z]+)/$', HandleArchiveMonth)],
									debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()