# -*- coding: utf-8 -*-
"""
nested_template是使用nested数据结构的template
flat_template是使用扁平化数据结构的template
"""

import requests
import json

nodes_nested_template = {
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


nodes_flat_template = {
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


class EsTemplate(object):

    def make_nodes_template(self, es_url, data_structure):
        if data_structure == 'flat':
            template = nodes_flat_template
        else:
            template = nodes_nested_template
        url = "http://{0}:9200/_template/{1}".format(es_url, template['template'])
        r = requests.get(url)
        if r.status_code == 404:
            r = requests.put(url, data=json.dumps(template), headers={'content-type': 'application/json'})
            print(r.text)
            if r.status_code == 200:
                print('put template %s success!' % template['template'])
            else:
                print('put template %s failed!' % template['template'])
        elif r.status_code == 200:
            print('template %s exists!' % template['template'])
        else:
            print('get template %s error!' % template['template'])

    def make_indices_template(self, es_url):
        pass
