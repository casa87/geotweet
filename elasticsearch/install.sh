#!/bin/bash

echo "Creating index"
curl -XPUT 'http://localhost:9200/twitter/' -d '{
    "settings" : {
        "index" : {
            "number_of_shards" : 3,
            "number_of_replicas" : 2
        }
    }
}'

echo "Creating mapping"
curl -XPUT 'http://localhost:9200/twitter/_mapping/tweet' -d @mapping.json
