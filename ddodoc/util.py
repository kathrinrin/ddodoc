import json
import urllib2
import datetime 


url = "http://api.opencultuurdata.nl/v0/search"
now = datetime.datetime.now()

def get_candidates():
    
    candidates = []
    
    for x in range(0, 3000):
        
        data = '{"query": "-dirtyhack","filters": {"date": {"from": "%d-%d-%d","to": "%d-%d-%d"}, "media_content_type": {"terms": ["image/jpeg"]}}}' % (x, now.month, now.day, x, now.month, now.day)
        headers = { "Accept" : "application/json", "Conthent-Type": "application/json"}
        req = urllib2.Request(url, data, headers)
        response = urllib2.urlopen(req)
        the_page = response.read()
        json_object = json.loads(the_page) 
        
        if len(json_object['hits']['hits']) > 0:
            print str(x) + ': ' + str(len(json_object['hits']['hits'])) + ' hits'
            
            for item in json_object['hits']['hits']:
                if item['_source'].has_key('title'):
                    if (len(item['_source']['title']) <= 93 and (item['_source']['date_granularity'] >= 8)): 
                        candidates.append(item)
    return (candidates)
