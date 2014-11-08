#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-


import json
import urllib
import util
import random
import datetime
import bitly_api
from twython import Twython
import os.path
import re 


BITLY_API_USER = ''
BITLY_API_KEY = ''
BITLY_ACCESS_TOKEN = ''

TWITTER_APP_KEY = ''
TWITTER_APP_SECRET = ''
TWITTER_OAUTH_TOKEN = ''
TWITTER_OAUTH_TOKEN_SECRET = ''


now = datetime.datetime.now()
jsonFileName = '../json/' + str(now.year) + '-' + str(now.month) + '-' + str(now.day) + '.json'


twitter = Twython(TWITTER_APP_KEY, TWITTER_APP_SECRET, TWITTER_OAUTH_TOKEN, TWITTER_OAUTH_TOKEN_SECRET)

# Always get fresh trendset 
trendset = set()
trends = twitter.get_available_trends()
for trend in trends:
     
    if trend['country'] == 'Netherlands': 
        print trend
        woeid = trend['woeid']
           
        results = twitter.get_place_trends(id=woeid)
        for result in results: 
            for resulttrend in result['trends']: 
                resulttrendname = resulttrend['name']
                if not ((trend['name'] in resulttrendname) or ('Den Haag' in resulttrendname) or ('Amsterdam' in resulttrendname) or ('Rotterdam' in resulttrendname) or ('Utrecht' in resulttrendname) or ('Nederland' in resulttrendname) or ('The Hague' in resulttrendname)):  
                    trendset.add(re.sub('^[^a-zA-z]*|[^a-zA-Z]*$', '', resulttrendname))
print trendset 
print len(trendset)

# trendset = set([u'pauw', u'Wiebes', u'TVOH', u'Tweede Kamer', u'Waarom', u'Goedemorgen', u'Thanxx', u'Welkom', u'Zwarte Piet', u'WhatsApp', u'ajabar', u'FEYrij', u'CollegeTour', u'Weet', u'Zwarte Pieten', u'LIVCHE', u'FOURleaked', u'Ziggo', u'AJAbar', u'Succes', u'Pauw', u'CDAcongres', u'Van Rijn', u'anouk', u'Halloween', u'Westen', u'asksamuel', u'Trijntje', u'ziggo', u'Youp'])


# check whether candidates are already available, get them from OCD API otherwise 
if os.path.isfile(jsonFileName): 
    json_data = open(jsonFileName)
    candidates = json.load(json_data)
    print str(len(candidates)) + ' candidates'
    print

else: 
    # good time to clean up 
    jsonFolder = '../json/'
    for json_file in os.listdir(jsonFolder):
        json_path = os.path.join(jsonFolder, json_file)
        os.unlink(json_path)
        
    imageFolder = '../images/'
    for image_file in os.listdir(imageFolder):
        image_path = os.path.join(imageFolder, image_file)
        os.unlink(image_path)

    candidates = util.get_candidates()
    with open(jsonFileName, 'wb') as fp:
        json.dump(candidates, fp)
    print str(len(candidates)) + ' candidates'
    print
    

# try to tweet random item 
success = False 

while success == False: 
    
    try: 
        
        title = ''
        authors = ''
        originalurl = ''
        date = ''
        
        item = ''
        founditem = False 
        
        for candidate in candidates: 
            title = candidate['_source']['title']
            if any(trend in title for trend in trendset):
                print title 
                founditem = True
                item = candidate
                print 'chosen by match: ' + str(item)
                break  
        
        if (founditem == False):  
            item = random.choice(candidates)
            print 'chosen randomly: ' + str(item)
            
        
        print
        print 'id: ' + item['_id']
        print
    
# if item['_source'].has_key('description'):
#     print 'description: ' + item['_source']['description']
#     print

        if item['_source'].has_key('title'):
            title = item['_source']['title']
            print 'title: ' + title
            print
            
        if item['_source'].has_key('date_granularity'):
            print 'date_granularity: ' + str(item['_source']['date_granularity'])

        if item['_source']['meta'].has_key('original_object_urls'):
            originalurl = item['_source']['meta']['original_object_urls']['html']
            print 'original_object_urls html: ' + originalurl
            print

        if item['_source']['meta'].has_key('collection'):
            print 'collection: ' + str(item['_source']['meta']['collection'])
            print

        if item['_source'].has_key('media_urls'):
            for url in item['_source']['media_urls']:
                media_url = url['url']
                print 'media_url: ' + media_url
                print 'content_type: ' + url['content_type']
                print 'width: ' + str(url.get("width", None))
                print 'height: ' + str(url.get("height", None))
                print

        if item['_source'].has_key('authors'):
            for author in item['_source']['authors']:
                if authors == '': 
                    authors = authors + author.encode('utf-8')
                else: 
                    authors = authors + ', ' + author.encode('utf-8')
                print 'authors: ' + authors
                print

        if item['_source'].has_key('date'):
            year = item['_source']['date'][0:4]
            date = item['_source']['date'][0:10]
            print 'year: ' + year
            print 


        # shorten url 
        conn_btly = bitly_api.Connection(access_token=BITLY_ACCESS_TOKEN)
        shorturl = conn_btly.shorten(originalurl, BITLY_API_USER, BITLY_API_KEY)
        # print shorturl['url']


        # assemble tweet 
        difference = now.year - int(year)
        tweet = "Today, " + str(difference) + " years ago: '" + title + "' by " + authors + " - " + shorturl['url']

        if len(tweet) > 140: 
            tweet = "Today, " + str(difference) + " years ago: '" + title + "' - " + shorturl['url']

        print tweet
        print str(len(tweet)) + ' characters'
        print 

        if len(tweet) <= 140: 
            imageFileName = '../images/' + item['_id'] + '.jpg' 
            if (not os.path.isfile(imageFileName)):
                urllib.urlretrieve(media_url, imageFileName)
            
            print 'Size of image: ' + str(os.path.getsize(imageFileName))
            print 
        
            photo = open(imageFileName)
        
            twitter.update_status_with_media(status=tweet, media=photo)
            success = True 
            print 'success!' 
    
            # delete tweeted item from candidates -> prevents double tweets 
            for i in xrange(len(candidates)):
                if candidates[i]['_id'] == item['_id']: 
                    candidates.pop(i)
                    with open(jsonFileName, 'wb') as fp:
                        json.dump(candidates, fp)
                        break

    except Exception as e:
        print e
        print 
        print 
            
