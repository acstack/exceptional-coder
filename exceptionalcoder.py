from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from datamodels import *
from google.appengine.ext import db
from google.appengine.ext.webapp import template
import os
from utilities import *

#template.register_template_library('templatetags.blogtags')
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
			self.url_link = users.create_logout_url('/')
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
			self.url_link = users.create_logout_url('/')
			errors = checkValidity(params)
			if len(errors) > 0:
				templat_values = {'url_link': url_link, 'errors': errors}
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

#Request Handlers for User Interaction with the Application



# requestHandlers for the User Interfaces

class Homepage(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()
		if user:
			url_link = users.create_logout_url('/')
			url_text = "logout"
			#Will  have functionality to display user profile on google
		else:
			url_link = users.create_login_url(self.request.uri)
			url_text = "login"
		blog_list = db.GqlQuery("select * from Blog")
		post_list = db.GqlQuery("select * from Blogpost order by poston desc")
		template_values={
			'url_link': url_link,
			'url_text': url_text,
			'blog_list': blog_list,
			'post_list': post_list,
			}
		if user:
			template_values['nick_name'] = user.nickname()
		if users.is_current_user_admin():
			template_values['admin_link'] = '/admin/'
		path = os.path.join(os.path.dirname(__file__), 'templates/homepage.html')
		self.response.out.write(template.render(path, template_values))

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
		template_values = {
			'url_link': url_link,
			'url_text': url_text,
			'post_list': post_list,
			'category': blog,
			'blog_list': blist,
			}
		if user:
			template_values['nick_name'] = user.nickname()
		path = os.path.join(os.path.dirname(__file__), 'templates/showcategory.html')
		self.response.out.write(template.render(path, template_values))

class showpost(webapp.RequestHandler):
	def get(self, pid):
		#print pid + "........"
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
		#print bpost.posttitle
		blog_list = db.GqlQuery("select * from Blog")
		template_values = {
			'url_link': url_link,
			'url_text': url_text,
			'bpost': bpost,
			'blog_list': blog_list,
			}
		if user:
			template_values['nick_name'] = user.nickname()
		path = os.path.join(os.path.dirname(__file__), 'templates/showpost.html')
		self.response.out.write(template.render(path, template_values))

class postcomment(webapp.RequestHandler):
	def post(self):
		pid = self.request.get('pid')
		pid = int(pid)
		ctext = self.request.get('comtext')
		bposts = db.GqlQuery("select * from Blogpost where post_id = :1", pid)
		bpost = bposts.get()
		cid = getCommentId()
		comment = Comments(blogpost=bpost, commentid=cid, commenttext=ctext)
		comment.put()
		restext = ""
		clist = bpost.comments
		for c in clist:
			restext = restext + "<fieldset><legend style='font-size:20px'>" + c.commentby.nickname() + " said</legend>" + str(c.commenton) + "<br>" + c.commenttext + "</fieldset>"
		self.response.out.write(restext)

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
									('/knowme/', aboutme)],
									debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()