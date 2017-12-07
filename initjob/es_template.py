# -*- coding: utf-8 -*-
"""
body是使用nested数据结构的template
body_V1是使用扁平化数据结构的template
"""

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


body_V1 = {
    "order": 0,
    "template": "cc-monitor-*",
    "mappings": {
        "nodes_status": {
            "properties": {
                "nodes_status": {
                    "properties": {
                        "node_ip": {
                            "type": "ip"
                        }
                    }
                }
            }
        }
    },
    "aliases": {}
}


def make_template(es_url):
    url = "http://{0}:9200/_template/{1}".format(es_url, body_V1['template'])
    r = requests.get(url)
    if r.status_code == 404:
        r = requests.put(url, data=json.dumps(body_V1), headers={'content-type': 'application/json'})
        print(r.text)
        if r.status_code == 200:
            print('put template %s success!' % body_V1['template'])
        else:
            print('put template %s failed!' % body_V1['template'])
    elif r.status_code == 200:
        print('template %s exists!' % body_V1['template'])
    else:
        print('get template %s error!' % body_V1['template'])
