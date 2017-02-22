from flask import Flask, request, abort, redirect

import errno
import os
import sys
import tempfile
import random
import wikipedia

from markovchain import run
from nGram import nRun, nUpdate, join

from werkzeug.contrib.cache import SimpleCache

from argparse import ArgumentParser

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser, SourceGroup, SourceRoom,
    TemplateSendMessage, ConfirmTemplate, MessageTemplateAction,
    ButtonsTemplate, URITemplateAction, PostbackTemplateAction,
    CarouselTemplate, CarouselColumn, PostbackEvent,
    StickerMessage, StickerSendMessage, LocationMessage, LocationSendMessage,
    ImageMessage, VideoMessage, AudioMessage,
    UnfollowEvent, FollowEvent, JoinEvent, LeaveEvent, BeaconEvent
)

app = Flask(__name__)

cSecret = 'Insert channel secret'
cAccessToken = 'Insert channel access token'

line_bot_api = LineBotApi(cAccessToken)
handler = WebhookHandler(cSecret)
cache = SimpleCache(6000, 0)
cache.set("nGramDict", nUpdate())

@app.route("/callback", methods = ["POST"])
def callback():
    f = open("/var/www/FlaskApp/FlaskApp/log.txt", 'a')
    body = request.get_data(as_text=True)
    signature = request.headers['X-Line-Signature']
    f.write(str(body))
    f.write("\n")
    f.close()
    handler.handle(body, signature)
    return("hi")

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    f = open("/var/www/FlaskApp/FlaskApp/textlog.txt", 'a')
    if "@rb" not in event.message.text.split() and "@randombot" not in event.message.text.split():
        f.write("`" + event.message.text + '`' + "\n")
    f.close()
    result = textParser(event.message.text, event)
    if result == False:
        return False
    else:
        line_bot_api.reply_message(event.reply_token, result)
    return "ok"

@handler.default()
def default(event):
    f = open("/var/www/FlaskApp/FlaskApp/log2.txt", 'a')
    f.write(str(event))
    f.write("default")
    f.close()
    #textParser("Greed", event)
    return "ok"

def textParser(message, event):
    splitMessage = message.split()
    if "@rb" in splitMessage[0] or "@randombot" in splitMessage[0]:
        if "spin" in splitMessage[1]:
            return TextSendMessage(text=spin())
        if "dice" in splitMessage[1]:
            if len(splitMessage) > 2:
                return TextSendMessage(text=dice(int(splitMessage[2])))
            return TextSendMessage(text=dice())
        if "rps" in splitMessage[1]:
            return TextMessage(text=rps())
        if "8ball" in splitMessage[1] or "eightball" in splitMessage[1]:
            return TextMessage(text=eightball())
        if "chain" in splitMessage[1]:
            return TextMessage(text=mChain())
        if "wiki" in splitMessage[1] or "wikipedia" in splitMessage[1]:
            return TextMessage(text=wikiSearch(splitMessage[2:]))
        if "ngram" in splitMessage[1]:
            if len(splitMessage) > 2:
                return TextMessage(text=join(cache.get("nGramDict"), splitMessage[2]))
            else:
                return TextMessage(text=join(cache.get("nGramDict")))
	if "nUpdate" in splitMessage[1]:
	    cache.set("nGramDict", nUpdate())
	    return TextMessage(text="Updating nodes" + str(len(cache.get("nGramDict"))))
	if "debug" in splitMessage[1]:
	    try:
	         if splitMessage[2] == "nlen":
		    return TextMessage(text="uhh")
	    except Exception, e:
		return TextMessage(text="Debug error " + str(e))
    return False

def getUserId(id):
    f = open("/var/www/FlaskApp/FlaskApp/test.txt", 'w')
    f.write(id)
    x = int(id)
    result = line_bot_api.get_message_content(x)
    f.write(result)
    f.close
    return True


def spin():
    symbols = [u'\U0001F34B', u'\U0001F352', u'\U0001F4B0']
    first = random.sample(symbols, 1)[0]
    second = random.sample(symbols, 1)[0]
    third = random.sample(symbols, 1)[0]

    if first == second and second == third:
        return(first + ' ' + second + ' ' + third + '\n' + 'You win!')
    else:
        return(first + ' ' + second + ' ' + third) 

def dice(k = 6):
    randomDiceNumber = random.randint(1,k)
    return str(randomDiceNumber)

def rps():
    rps = ['rock', 'paper', 'scissors']
    return(str(random.sample(rps, 1)[0]))

def eightball():
    answers = ['It is certain', 'It is decidedly so', 'Without a doubt', 'Yes, definitely', 'You may rely on it', 'As I see it, yes', 'Most likely','Outlook good', 'Yes', 'Signs point to yes', 'Reply hazy try again', 'Ask again later', 'Better not tell you now', 'Cannot predict now', 'Concentrate and ask again', 'Do not count on it', 'My reply is no', 'My sources say no', 'Outlook not so good', 'Very doubtful']
    return(str(random.sample(answers, 1)[0]))

def mChain():
    result = run()
    return result

def wikiSearch(query):
    query = ' '.join(query)
    returnQuery = wikipedia.search(query)

    if returnQuery:
        page = wikipedia.page(returnQuery[0])
        summary = wikipedia.summary(query, sentences=1)
        msg = page.title + "\n" + page.url + "\n"
        msg += summary
        return msg
    else:
        return "Nothing Found"

@app.route("/")
def hello():
     return "hello world"
    #return redirect("https://leosun.us/test", code=302)

@app.route("/test")
def hello2():
    return "placeholder"
    #return join(cache.get("nGramDict"))

@app.route("/test2")
def pay():
    return "x&#772"

@app.route("/test3")
def hello3():
    return "placeholder"
    #return str(cache.get("nGramDict"))

@app.route("/nupdate")
def ngramupdate():
    cache.set("nGramDict", nUpdate())
    return "updated"
    #return str(cache.get("nGramDict"))

if __name__ == "__main__":
    app.run()
