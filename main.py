#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import os
import webapp2
import cgi
import re
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir))


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile("^.{3,20}$")
EMAIL_RE = re.compile("^[\S]+@[\S]+\.[\S]+$")




class Handler(webapp2.RequestHandler):
  def write(self, *a, **kw):
    self.response.out.write(*a, **kw)

  def render_str(self, template, **kwargs):
    t = jinja_env.get_template(template)
    return t.render(**kwargs)

  def render(self, template, **kwargs):
    self.write(self.render_str(template, **kwargs))

class MainHandler(Handler):
  def get(self):
    self.render("mainpage.html")




###### Database considerations:

def blog_key(name = "default"):
  return db.Key.from_path('blogs', name)

class BlogPost(db.Model):
  subject = db.StringProperty(required=True)
  content = db.TextProperty(required=True)
  created = db.DateTimeProperty(auto_now_add=True)
  last_modified = db.DateTimeProperty(auto_now_add=True)

########

####### Blog Handlers

class BlogHandler(Handler):
  def get(self):
    posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 10") # Note: because class name is BlogPost
    self.render("mainpage.html", posts = posts)



class BlogPermalink(Handler):
  def get(self, post_id):
    key = db.Key.from_path('BlogPost', int(post_id))
    post_data = db.get(key)
    if not post_data:
      self.error(404)
    self.render("mainpage.html", posts = [post_data])





class NewPostHandler(Handler):
  def render_form(self, subject = "", content = "", error = ""):
    self.render("form.html", subject = subject, content = content, error = error)
  def get(self):
    self.render_form()

  def post(self):
    subject = self.request.get('subject')
    content = self.request.get('content')

    if subject and content:
      a = BlogPost(subject = subject, content = content)
      a.put()
      self.redirect("/blog/%s" % str(a.key().id()))
    else:
      self.render_form(subject = subject, content = content, error = "We need both a subject and some Content!")







app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/blog/?', BlogHandler),
    ('/blog/([0-9]+)', BlogPermalink),
    ('/blog/newpost', NewPostHandler)], debug=True)

### Spec:
# '/' => point to blog, display most recent entries
# '/newpost' => points to a form with subject, content--- sends back error unless both are filled out
# a successful submission creates a permalink page with that entry
