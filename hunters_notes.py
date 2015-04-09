#!/usr/bin/python
# -*- coding: utf-8 -*-

import config
import datetime
import json
import logging
import random
import string
import sys
import time
from twython import Twython, TwythonError

def connectTwitter():
     return Twython(config.twitter_key, config.twitter_secret,
                    config.access_token, config.access_secret)

def initJSON():
    with open("bloodborne.json") as json_file:
        return json.load(json_file)

def capitalizeFirst(sentence):
	# capitalize the first letter (stupidly complex)
	hasQuotes = sentence.count('\"')
	sentence = sentence.replace('\"', '')
	words = string.split(sentence, ' ', 1)
	words[0] = words[0].capitalize()
	if hasQuotes:
		return '\"' + string.join(words) + '\"'
	else:
		return string.join(words)

def getClause(data, capital=False):
	# get a random clause
	t = random.choice(data['templates'])
	if capital and not t.startswith('%s'):
		t = capitalizeFirst(t)
	if t.count('%s') > 0:
		w = random.choice(data['words'])
		if capital and t.startswith('%s'):
			w = capitalizeFirst(w)
		return t % w
	else:
		return t

def getSentence(data):
	# assemble clauses into a sentence
	sentence = getClause(data, True)
	if random.random() < 0.75:
		sentence += random.choice(data['conjunctions']) + getClause(data)
	if not sentence.endswith(('.', '!', '?')):
		sentence += "."
	return sentence

def postTweet(twitter, to_tweet):
    # post the given tweet
    print "Posting tweet: " + to_tweet.encode('ascii', 'ignore')
    twitter.update_status(status=to_tweet)

def waitToTweet():
    # tweet every 4 hours, offset by 1 hours
    now = datetime.datetime.now()
    wait = 60 - now.second
    wait += (59 - now.minute) * 60
    wait += (3 - ((now.hour + 1) % 4)) * 3600
    print "Wait " + str(wait) + " seconds for next tweet"
    time.sleep(wait)

if __name__ == "__main__":
	data = initJSON()
	twitter = connectTwitter()
	to_tweet = None
	
	# main loop
	while True:
		try:
			if not to_tweet:
				waitToTweet()
			to_tweet = getSentence(data)
			postTweet(twitter, to_tweet)
			to_tweet = None # success!
		except TwythonError as e:
			# might be a random error, try again?
			logging.exception(e)
		except:
			# actual error, don't try again
			logging.exception(sys.exc_info()[0])
			to_tweet = None
		time.sleep(60)