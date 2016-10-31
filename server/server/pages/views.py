#! /usr/bin/env python

from pprint import pprint
from elasticsearch import Elasticsearch
from django.views.generic import TemplateView


class HomeView(TemplateView):
    template_name = 'home.html'
    es = Elasticsearch()

    def get(self, request, *args, **kwargs):
        context = {}

        # Get parameters
        lat = request.GET.get('lat', None)
        if lat:
            try:
                lat = float(lat)
            except:
                lat = None
        long = request.GET.get('long', None)
        if long:
            try:
                long = float(long)
            except:
                long = None
        radius = request.GET.get('radius', '5km')
        if radius not in ('1km', '5km', '50km', '200km'):
            radius = '5km'

        if lat and long:
            # Build the query
            query = {
                "bool": {
                    "filter": {
                        "geo_distance": {
                            "distance": radius,
                            "coordinates.coordinates": {
                                "lat": lat,
                                "lon": long
                            }
                        }
                    },
                }
            }

            # Hashtags : Add hashtags to the query
            hashtags = request.GET.get('hashtags', '')
            if hashtags:
                query['bool']['must'] = []
                for hashtag in hashtags.split(' '):
                    if len(hashtag) > 1:
                        query['bool']['must'].append({"match": {"entities.hashtags.text": hashtag}})

            # Query
            res = HomeView.es.search(index="twitter", body={"query": query,
                                                            "sort": {"@timestamp": {"order": "desc"}},
                                                            "size": 200})
            tweets = []
            for tweet in res['hits']['hits']:
                tweets.append(tweet['_source'])
            if tweets:
                context['tweets'] = tweets
            context['lat'] = lat
            context['long'] = long
            context['hashtags'] = hashtags

        print
        return self.render_to_response(context)
