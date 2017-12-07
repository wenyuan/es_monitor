# -*- coding:utf-8 -*-
"""
各节点的数据结构采用nested形式
"""
import time


def parse_data(nodes_data, latest_nodes_data, es_config_info):
    esindex_prefix = es_config_info['esindex_prefix']
    data_type = es_config_info['data_type']
    values = []
    storage_nodes = []
    for node in nodes_data.keys():
        data = nodes_data[node]
        latest_data = latest_nodes_data[node]

        timestamp = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
        final_data = {'@timestamp': timestamp, 'appname': 'monitor', 'type': 'nodes_status',    # normal data
                      'nodes_status': {'data_nodes': storage_nodes}
                      }

        node_ip = latest_data['ip'].split(':')[0]                                                   # optional data
        host = latest_data['host']
        single_data_node_status = {'node_id': node, 'node_ip': node_ip, 'host': host,
                                   'indices': {'search': {}},
                                   'os': {},
                                   'jvm': {}
                                   }
        query_total = data['indices']['search']['query_total']
        query_time_in_millis = data['indices']['search']['query_time_in_millis']
        latest_query_total = latest_data['indices']['search']['query_total']
        latest_query_time_in_millis = latest_data['indices']['search']['query_time_in_millis']

        single_data_node_status['indices']['search']['query_total'] = latest_query_total - query_total
        single_data_node_status['indices']['search']['query_time_in_millis'] = (latest_query_time_in_millis - query_time_in_millis)

        if 'timestamp' in latest_data['os'].keys():    # remove reduplicated data
            latest_data['os'].pop('timestamp')
        if 'timestamp' in latest_data['jvm'].keys():
            latest_data['jvm'].pop('timestamp')
        single_data_node_status['os'] = latest_data['os']
        single_data_node_status['jvm'] = latest_data['jvm']

        storage_nodes.append(single_data_node_status)

        esindex = "%s-%s" % (esindex_prefix, time.strftime('%Y.%m.%d'))
        print(esindex)
        values.append({
            "_index": esindex,
            "_type": data_type,
            "_source": final_data
        })
    return values
