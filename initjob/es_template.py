# -*- coding: utf-8 -*-
"""
nested_template是使用nested数据结构的template
flat_template是使用扁平化数据结构的template
"""

import requests
import json

template_name = 'cc-monitor-template'

nodes_nested_template = {
    "order": 1,
    "template": "cc-monitor-*",
    "settings": {
        "index": {
            "refresh_interval": "10s",
            "number_of_shards": 5,
            "number_of_replicas": 0,
            "routing.allocation.total_shards_per_node": 1
        }
    },
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
    "order": 1,
    "template": "cc-monitor-*",
    "settings": {
        "index": {
            "refresh_interval": "10s",
            "number_of_shards": 5,
            "number_of_replicas": 0,
            "routing.allocation.total_shards_per_node": 1
        }
    },
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
        url = "http://{0}:9200/_template/{1}".format(es_url, template_name)
        r = requests.get(url)
        if r.status_code == 404:
            r = requests.put(url, data=json.dumps(template), headers={'content-type': 'application/json'})
            print(r.text)
            if r.status_code == 200:
                print('put template %s success!' % template_name)
            else:
                print('put template %s failed!' % template_name)
        elif r.status_code == 200:
            print('template %s exists!' % template_name)
        else:
            print('get template %s error!' % template_name)

    def make_indices_template(self, es_url):
        pass
