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

import webapp2
import cgi
import re
import jinja2.environment


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASSWORD_RE = re.compile("^.{3,20}$")
EMAIL_RE = re.compile("^[\S]+@[\S]+\.[\S]+$")

form="""
<form action="/testform">
  <select name="q">
    <option>One</option>
    <option>Two</option>
    <option>Thr</option>
  </select>
  <br/>
  <input type="submit">
</form>
"""



class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers["Content-type"] = "text/html"
        self.response.write(form)

class TestHandler(webapp2.RequestHandler):
    def get(self):
        self.response.headers["Content-type"] = "text/plain"
        self.response.write(self.request)

class Rot13Handler(webapp2.RequestHandler):
    def get_template(self, input = ""):
      template = """
<form method="POST">
<textarea name="text">
%(INPUT)s
</textarea>
<input type="submit">
</form>
    """
      return template % {'INPUT': input}
    def get(self):
        self.response.write(self.get_template())

    def post(self):
      input_raw = self.request.get("text")

      letters = "abcdefghijklmnopqrstuvwxyz"
      LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

      i1 = ""
      for ch in input_raw:
        i1 += letters[(letters.find(ch) + 13) % 26] if letters.find(ch) > -1 else ch
      i2 = ""
      for ch in i1:
        i2 += LETTERS[(LETTERS.find(ch) + 13) % 26] if LETTERS.find(ch) > -1 else ch

      input_escaped = cgi.escape(i2)
      self.response.write(self.get_template(input_escaped))


class SignupHandler(webapp2.RequestHandler):
  def signup_template(self, username = "", password = "", verify = "", email = "",
                      erm_username = "", erm_password = "", erm_verify = "", erm_email=""):
    template = """
<h1>Signup</h1>
<form method="POST">
<label>
  Username
  <input name="username" value="%(username)s">
  <span>%(erm_username)s</span>
</label></br>
<label>
  Password
  <input name="password" type="password" value="%(password)s">
  <span>%(erm_password)s</span>
</label></br>
<label>
  Verify password
  <input name="verify" type="password" value="%(verify)s">
  <span>%(erm_verify)s</span>
</label></br>
<label>
  Email (optional)
  <input name="email" type="email" value="%(email)s">
  <span>%(erm_email)s</span>
</label></br>
<input type="submit">
</form>
    """
    rendered_template = template % {'username': username,
                                    'password': password,
                                    'verify': verify,
                                    'email': email,
                                    'erm_username': erm_username,
                                    'erm_password': erm_password,
                                    'erm_verify': erm_verify,
                                    'erm_email': erm_email}
    return rendered_template

  def get(self):
    self.response.write(self.signup_template())

  def post(self):
    username = self.request.get("username")
    password = self.request.get("password")
    verify = self.request.get('verify')
    email = self.request.get('email')

    vu = USER_RE.match(username)
    vp = PASSWORD_RE.match(password)
    vv = (password == verify)
    if not email == "":
      ve = EMAIL_RE.match(email)
    else:
      ve = True
    erm_username, erm_password, erm_verify, erm_email = "", "", "", ""

    if vu and vp and vv and ve:
      self.redirect('/welcome?username=%s' % username)
    if not vu:
      erm_username = "That's not a valid username"
    if not vp:
      erm_password = "That's not a valid password"
    if not vv:
      erm_verify = "Passwords do not match"
    if not ve:
      erm_email = "That's not a valid email address"

    self.response.write(self.signup_template(username, password, verify, email,
                                             erm_username, erm_password, erm_verify, erm_email))


class WelcomeHandler(webapp2.RequestHandler):
  def get(self):
    username = self.request.get("username")
    self.response.write("Welcome %s!" % username)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/testform', TestHandler),
    ('/unit2/signup', SignupHandler),
    ('/unit2/rot13', Rot13Handler),
    ('/welcome', WelcomeHandler)

], debug=True)
