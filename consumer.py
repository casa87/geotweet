#!/usr/bin/python
# -*- coding: UTF-8 -*-

import sys
import ujson
import elasticsearch
from pprint import pprint
from unicodedata import normalize
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

access_token = ""
access_token_secret = ""
consumer_key = ""
consumer_secret = ""

# SF Bay Area boundaries
boundaries = [-122.6624, 36.7378,
              -121.4044, 38.1486]

# USA
boundaries = [-126.02, 26.23,
              -65.04, 49.33]
# Boundaries World
boundaries2 = [-180, -90,
               180, 90]

es = elasticsearch.Elasticsearch('http://localhost:9200')


class ESExporter(StreamListener):
    """ A listener handles tweets that are received from the stream.
    """

    def on_data(self, tweet):
        """
        Receive a tweet from the stream and insert it into ES
        :param tweet: tweet object
        :return:
        """
        data = ujson.loads(tweet)
        try:
            # Check for a geolocation.
            if not data['geo']:
                return

            # Build the data to export to ES.
            content = {'user': {},
                       'coordinates': {}}

            # Inser data from the tweet in the payload.
            content['@timestamp'] = data['created_at']
            coord = data['coordinates']['coordinates']
            content['coordinates']['coordinates'] = {"lon": coord[0],
                                                     "lat": coord[1]}
            content['user']['name'] = data['user']['screen_name']
            content['text'] = normalize('NFKD', data['text']).encode('ascii', 'ignore')

            # Check for an hashtags.
            hashtags = data['entities'].get('hashtags', [])
            if hashtags:
                content['entities'] = {'hashtags': []}
                for hashtag in data['entities'].get('hashtags', []):
                    content['entities']['hashtags'].append(hashtag)

            es.index(index='twitter', doc_type='tweet', body=content)
        except:
            print "FAIL"
            pprint(data)

    def on_error(self, status):
        """
        IHandlers for error
        :param status:  status of the error
        :return:
        """
        print(status)


if __name__ == '__main__':
    l = ESExporter()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    stream = Stream(auth, l)
    stream.filter(locations=boundaries)
