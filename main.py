from flask import Flask
app = Flask(__name__)
app.config['DEBUG'] = True

# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.


import os

import re
import logging
import jinja2
import webapp2

template_dir = os.path.join(os.path.dirname(__file__),'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                                autoescape = True)

# Validation Functions:
def doPasswordsMatch(password, verify):
    return password == verify
USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return USER_RE.match(username)
PASS_RE = re.compile(r"^.{3,20}$")
def valid_password(password):
    return PASS_RE.match(password)
EMAIL_RE = re.compile(r"^[\S]+@[\S]+.[\S]+$")
def valid_email(email):
    # Email is optional
    if email:
        return EMAIL_RE.match(email)
    else:
        return True


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)
    def render_str(self, template, **params):
        t= jinja_env.get_template(template)
        return t.render(params)
    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainHandler(Handler):
    def get(self):
        self.render("base.html", passwordsMatch = True, validUsername = True, 
                        validPassword = True, validEmail = True)
    def post(self):
        # Get user inputs and assign to variables
        username = self.request.get("username")
        password = self.request.get("password")
        verify = self.request.get("verify")
        email = self.request.get("email")

        # Assign results of verifications to variables
        passwordsMatch = doPasswordsMatch(password, verify)
        validUsername = valid_username(username)
        validPassword = valid_password(password)
        validEmail = valid_email(email)
        # If no error pops, render welcome.html, otherwise render base and send error variables to it
        if (passwordsMatch and validUsername and validPassword and validEmail): 
            #self.render("welcome.html", username = username)
            self.redirect('/welcome?username='+username)
        else:
            self.render("base.html", passwordsMatch = passwordsMatch, validUsername = validUsername, 
                        validPassword = validPassword, validEmail = validEmail, username = username, email = email)
class Welcome(Handler):
    def get(self):
        username = self.request.get("username")
        self.render("welcome.html", username = username)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/welcome', Welcome) 
], debug=True)