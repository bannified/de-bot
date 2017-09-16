import json
import logging
import urllib
import urllib2
from secrets import TOKEN, WEBHOOK_URL, MAIN_ANDROID_ID

# standard app engine imports
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
import webapp2

BASE_URL = 'http://api.tofusms.com/devices/send/' + MAIN_ANDROID_ID

JSON_HEADER = {'Content-Type': 'application/json;charset=utf-8',
                "Authorization": "Token " + TOKEN}
# ================================

class User(ndb.Model):
    contact = ndb.StringProperty()
    currentMode = ndb.StringProperty(default="new")
    rating = ndb.IntegerProperty(default=0)


# ================================

def make_payload(message, contact):
    payload = json.dumps({
        'message': message,
        'contact': contact
        })
    return payload

def send_message(data):
    urlfetch.fetch(url=BASE_URL, payload = data, method = urlfetch.POST,
                    headers = JSON_HEADER)

def get_user_by_contact(contact):
    q = User.query(User.contact == str(contact)).fetch()
    if len(q) != 0:
        user = q[0]
        return user
    else:
        newuser = User(contact = contact)
        newuser.put()
        return newuser


# ================================

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write("LULULULULUL")

class ReceiveHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write("Receive page")
    def post(self):
        data = json.loads(self.request.body) #deserializing json in POST request body
        logging.debug(self.request.body) # prints debug message

        msg = data["message"]
        contact = data["contact"]

        user = get_user_by_contact(contact)
        new_msg = ""
        # if (msg == "start"):
        #     user.currentMode = "new"
        if (msg == "new"):
            user.currentMode = "new"
        if (user.currentMode == "new"):
            if (msg == "start"):
                new_msg = "You are about to start a new demo. At any point if you feel like restarting the " + \
                        "demo, type in 'new'!"
                send_message(make_payload(new_msg, contact))
                new_msg = "Hi! I am De-Bot.\nYour package #059123754 has arrived in Singapore! " + \
                "It will be be delivered to you @ 6 College Avenue East, University Town " + \
                "on 24th September 2017, 1:00PM - 3:00PM. \n \n" + \
                "Please reply '0' if you are not able to collect at the stated time. " + \
                "No action is required if you are okay with this arrangement."
                user.currentMode = "start"
                user.put()
                if (user.rating > 0):
                    new_msg += "\n\nAlso... You seem familiar... you were the human who " + \
                    "rated me " + str(user.rating) + " right? Bots like me have good memory!"
            else:
                new_msg = "Hello! It seems like you are a new user. I am De-Bot, nice to meet you! \n \n" + \
                            "Please enter 'start' to begin trying me out!"
                if (user.rating >= 0):
                    new_msg += "\n\n Also... You seem familiar... you were the human who " + \
                    "rated me " + str(user.rating) + " right? Bots like me have good memory!" + \
                    " I'll see if I can do better this time!"
            send_message(make_payload(new_msg, contact))
        elif (user.currentMode == "start"):
            if (msg == "next"):
                new_msg = "Hi! I am De-Bot.\n" + \
                "Your package will be be delivered to you TOMORROW at 1:00PM - 3:00PM. \n \n " + \
                "Please reply '0' if you are not able to collect at the stated time. " + \
                "No action is required if you are okay with this arrangement."
                user.currentMode = "demo1"
                user.put()
            elif (msg == "0"):
                new_msg = "Hi! I have noticed that you are not able to collect " + \
                "your package today. \n " + \
                "Thank you for informing us!\n\n " + \
                "Your package will not be delivered today and is being " + \
                "rescheduled for delivery on another day."
                user.currentMode = "new"
                user.put()
            else:
                new_msg += "Sorry, I did not understand what you just said.\n"
                new_msg += "[DEMO MODE]\n"
                new_msg += "You are currently in start mode\n"
                new_msg += "Type 'next' to go to the next step of the demo."
            send_message(make_payload(new_msg, contact))
        elif (user.currentMode == "demo1"):
            if (msg == "next"):
                new_msg = "Hi! I am De-Bot.\n" + \
                "Your package will be be delivered to you TODAY at 1:00PM - 3:00PM. \n \n " + \
                "Please reply '0' if you are not able to collect at the stated time. " + \
                "No action is required if you are okay with this arrangement."
                user.currentMode = "demo2"
                user.put()
            elif (msg == "0"):
                new_msg = "Hi! I have noticed that you are not able to collect " + \
                "your package today. \n " + \
                "Thank you for informing us!\n\n " + \
                "Your package will not be delivered today and is being " + \
                "rescheduled for delivery on another day."
                user.currentMode = "new"
                user.put()
            else:
                new_msg += "Sorry, I did not understand what you just said.\n"
                new_msg += "[DEMO MODE]\n"
                new_msg += "You are currently in demo1 mode\n"
                new_msg += "Type 'next' to go to the next step of the demo."
            send_message(make_payload(new_msg, contact))
        elif (user.currentMode == "demo2"):
            if (msg == "next"):
                new_msg = "Your package has successfully been delivered! \n\n" + \
                "Thank you for using De-Bot! \n " + \
                "If you want to, give me a rating from '1' to '5' just by typing " + \
                "the number in! \n\n" + \
                "Also, you can find my source code and leave a feedback for a " + \
                "friendly bot like me to my developers Sharan, De Long " + \
                "and Dominic at https://github.com/bannified !"
                send_message(make_payload(new_msg,contact))
                new_msg = "--- END OF DEMO --- \n" + \
                "Type in 'new' to try again"
            elif (msg == "0"):
                new_msg = "Hi! I have noticed that you are not able to collect " + \
                "your package today. \n" + \
                "Thank you for informing us!\n\n " + \
                "Your package will not be delivered today and is being " + \
                "rescheduled for delivery on another day."
                user.currentMode = "new"
                user.put()
            elif (msg == "1"):
                new_msg = "That means that I still have much to improve on! \n" + \
                "Thank you for the feedback, kind human!"
                user.rating = 1
                user.currentMode = "new"
                user.put()
            elif (msg == "2"):
                new_msg = "I'll try harder the next time we meet! \n" + \
                "Thank you for the feedback, kind human!"
                user.rating = 2
                user.currentMode = "new"
                user.put()
            elif (msg == "3"):
                new_msg = "Nice! That's kind of you. I'll become better in the future! \n" + \
                "Thank you for the feedback, kind human!"
                user.rating = 3
                user.currentMode = "new"
                user.put()
            elif (msg == "4"):
                new_msg = "Wow! I've never been praised so highly before. \n" + \
                "Thank you for the feedback, kind human!"
                user.rating = 4
                user.currentMode = "new"
                user.put()
            elif (msg == "5"):
                new_msg = "Does this make me the best bot in the world?  \n" + \
                "Thank you for the feedback, kind human!"
                user.rating = 5
                user.currentMode = "new"
                user.put()
            else:
                new_msg = "Sorry, I did not understand what you just said.\n"
                new_msg += "[DEMO MODE]\n"
                new_msg += "You are currently in demo2 mode\n"
                new_msg += "Type 'next' to go to the next step of the demo."
            send_message(make_payload(new_msg, contact))
        self.response.write(self.request)

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/receive', ReceiveHandler),
], debug=True)
