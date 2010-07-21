# General utilities for the application

def checkValidity(params):
	errors = {}
	for key, value in params.iteritems():
		if value == '' or value == None:
			errors[key] = 'yes'
	return errors

def getPid_for_Post():
	from google.appengine.ext import db
	p_list = db.GqlQuery("select * from Blogpost")
	pid = 1
	for p in p_list:
		if p.post_id > pid:
			pid = p.post_id
	pid = pid +1
	return pid

def getCommentId():
	from google.appengine.ext import db
	c_list = db.GqlQuery("select * from Comments")
	cid = 1
	for c in c_list:
		if c.commentid > cid:
			cid = c.commentid
	cid = cid + 1
	return cid