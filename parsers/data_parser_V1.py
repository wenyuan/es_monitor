# -*- coding:utf-8 -*-
"""
各节点的数据结构扁平化处理,每个节点的每个时间一个doc
优点:支持kibana的可视化
缺点:nodes较多的情况下,分出的docs数较多(同一时间几个nodes就有几个docs)
"""
import time
import copy


def parse_data(node_data, latest_node_data, es_config_info):
    esindex_prefix = es_config_info['esindex_prefix']
    data_type = es_config_info['data_type']
    values = []
    timestamp = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
    final_data_template = {'@timestamp': timestamp, 'appname': 'monitor', 'type': 'nodes_status',
                           'nodes_status': {'indices': {'search': {}}, 'os': {}, 'jvm': {}}
                           }
    for node in node_data.keys():
        data = node_data[node]
        latest_data = latest_node_data[node]

        node_ip = latest_data['ip'].split(':')[0]                                               # optional data
        final_data = copy.deepcopy(final_data_template)
        final_data['nodes_status']['node_ip'] = node_ip

        query_total = data['indices']['search']['query_total']
        query_time_in_millis = data['indices']['search']['query_time_in_millis']
        latest_query_total = latest_data['indices']['search']['query_total']
        latest_query_time_in_millis = latest_data['indices']['search']['query_time_in_millis']

        final_data['nodes_status']['indices']['search']['query_total'] = latest_query_total - query_total
        final_data['nodes_status']['indices']['search']['query_time_in_millis'] = (latest_query_time_in_millis - query_time_in_millis)

        if 'timestamp' in latest_data['os'].keys():    # remove reduplicated data
            latest_data['os'].pop('timestamp')
        if 'timestamp' in latest_data['jvm'].keys():
            latest_data['jvm'].pop('timestamp')
        final_data['nodes_status']['os'] = latest_data['os']
        final_data['nodes_status']['jvm'] = latest_data['jvm']

        esindex = "%s-%s" % (esindex_prefix, time.strftime('%Y.%m.%d'))
        print(esindex)
        values.append({
            "_index": esindex,
            "_type": data_type,
            "_source": final_data
        })
    return values
