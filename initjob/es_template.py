# -*- coding: utf-8 -*-

import requests
import json


body = {
    "order": 0,
    "template": "cc-monitor-*",
    "mappings": {
        "nodes_status": {
            "properties": {
                "nodes_status": {
                    "properties": {
                        "data_nodes": {
                            "type": "nested",
                            "properties": {
                                "node_ip": {
                                    "type": "ip"
                                }
                            }
                        }
                    }
                }
            }
        }
    },
    "aliases": {}
}


def make_template(es_url):
    url = "http://{0}:9200/_template/{1}".format(es_url, body['template'])
    r = requests.get(url)
    if r.status_code == 404:
        r = requests.put(url, data=json.dumps(body), headers={'content-type': 'application/json'})
        print(r.text)
        if r.status_code == 200:
            print('put template %s success!' % body['template'])
        else:
            print('put template %s failed!' % body['template'])
    elif r.status_code == 200:
        print('template %s exists!' % body['template'])
    else:
        print('get template %s error!' % body['template'])
