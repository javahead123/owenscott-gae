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


class BlogPost(db.Model):
  title = db.StringProperty(required=True)
  content = db.TextProperty(required=True)
  created = db.DateTimeProperty(auto_now_add=True)


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
    posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC LIMIT 10") # Note: because class name is BlogPost
    self.render("mainpage.html", posts = posts)

class NewPostHandler(Handler):
  def render_form(self, title = "", content = "", error = ""):
    self.render("form.html", title = title, content = content, error = error)
  def get(self):
    self.render_form()

  def post(self):
    title = self.request.get('title')
    content = self.request.get('content')

    if title and content:
      a = BlogPost(title = title, content = content)
      a.put()
      self.redirect("/")

    else:
      self.render_form(title = title, content = content, error = "We need both a Title and some Content!")

class PostHandler(Handler):
  def get(self):
    self.request
    self.render("mainpage.html")


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/post/(.*)', PostHandler),
    ('/newpost', NewPostHandler)], debug=True)

### Spec:
# '/' => point to blog, display most recent entries
# '/newpost' => points to a form with title, content--- sends back error unless both are filled out
# a successful submission creates a permalink page with that entry
