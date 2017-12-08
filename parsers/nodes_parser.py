# -*- coding:utf-8 -*-
"""
nested形式
    优点:节省docs数,性能上有一定好处
    缺点:不支持kibana的可视化
扁平化形式
    优点:支持kibana的可视化
    缺点:nodes较多的情况下,分出的docs数较多(每次插入数据中,几个nodes就有几个docs)
"""
import time
import copy


class NodesParser(object):

    def parse2nested_data(self, nodes_data, latest_nodes_data, es_config_info):
        esindex_prefix = es_config_info['esindex_prefix']
        data_type = es_config_info['data_type']
        values = []
        storage_nodes = []    # nested field: to store status_info of each es_node
        timestamp = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
        final_data = {'@timestamp': timestamp, 'appname': 'monitor', 'type': data_type,  # normal data
                      'nodes_status': {'data_nodes': storage_nodes}
                      }
        for node in nodes_data.keys():
            data = nodes_data[node]
            latest_data = latest_nodes_data[node]

            node_ip = latest_data['ip'].split(':')[0]                                                   # optional data
            host = latest_data['host']
            single_data_node_status = {'node_id': node, 'node_ip': node_ip, 'host': host,
                                       'indices': {'search': {}},
                                       'os': {},
                                       'jvm': {}
                                       }
            query_total = data['indices']['search']['query_total']                                   # search_info,is history data in default
            query_time_in_millis = data['indices']['search']['query_time_in_millis']
            latest_query_total = latest_data['indices']['search']['query_total']
            latest_query_time_in_millis = latest_data['indices']['search']['query_time_in_millis']
            young_gc_count = data['jvm']['gc']['collectors']['young']['collection_count']          # gc_info,is history data in default
            young_gc_time_in_millis = data['jvm']['gc']['collectors']['young']['collection_time_in_millis']
            latest_young_gc_count = latest_data['jvm']['gc']['collectors']['young']['collection_count']
            latest_young_gc_time_in_millis = latest_data['jvm']['gc']['collectors']['young']['collection_time_in_millis']
            old_gc_count = data['jvm']['gc']['collectors']['old']['collection_count']
            old_gc_time_in_millis = data['jvm']['gc']['collectors']['old']['collection_time_in_millis']
            latest_old_gc_count = latest_data['jvm']['gc']['collectors']['old']['collection_count']
            latest_old_gc_time_in_millis = latest_data['jvm']['gc']['collectors']['old']['collection_time_in_millis']

            single_data_node_status['indices']['search']['query_total'] = latest_query_total - query_total
            single_data_node_status['indices']['search']['query_time_in_millis'] = \
                latest_query_time_in_millis - query_time_in_millis

            if 'timestamp' in latest_data['os'].keys():    # remove reduplicated data
                latest_data['os'].pop('timestamp')
            if 'timestamp' in latest_data['jvm'].keys():
                latest_data['jvm'].pop('timestamp')
            single_data_node_status['os'] = latest_data['os']
            single_data_node_status['jvm'] = latest_data['jvm']
            single_data_node_status['jvm']['gc']['collectors']['young']['current_collection_count'] = \
                latest_young_gc_count - young_gc_count
            single_data_node_status['jvm']['gc']['collectors']['young']['current_collection_time_in_millis'] = \
                latest_young_gc_time_in_millis - young_gc_time_in_millis
            single_data_node_status['jvm']['gc']['collectors']['old']['current_collection_count'] = \
                latest_old_gc_count - old_gc_count
            single_data_node_status['jvm']['gc']['collectors']['old']['current_collection_time_in_millis'] = \
                latest_old_gc_time_in_millis - old_gc_time_in_millis

            storage_nodes.append(single_data_node_status)

        esindex = "%s-%s" % (esindex_prefix, time.strftime('%Y.%m.%d'))
        print(esindex)
        values.append({
            "_index": esindex,
            "_type": data_type,
            "_source": final_data
        })
        return values

    def parse2flat_data(self, node_data, latest_node_data, es_config_info):
        esindex_prefix = es_config_info['esindex_prefix']
        data_type = es_config_info['data_type']
        values = []
        timestamp = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
        final_data_template = {'@timestamp': timestamp, 'appname': 'monitor', 'type': data_type,    # normal data
                               'nodes_status': {'indices': {'search': {}}, 'os': {}, 'jvm': {}}
                               }
        for node in node_data.keys():
            data = node_data[node]
            latest_data = latest_node_data[node]

            node_ip = latest_data['ip'].split(':')[0]                                                       # optional data
            final_data = copy.deepcopy(final_data_template)
            final_data['nodes_status']['node_ip'] = node_ip

            query_total = data['indices']['search']['query_total']    # search_info,is history data in default
            query_time_in_millis = data['indices']['search']['query_time_in_millis']
            latest_query_total = latest_data['indices']['search']['query_total']
            latest_query_time_in_millis = latest_data['indices']['search']['query_time_in_millis']
            young_gc_count = data['jvm']['gc']['collectors']['young']['collection_count']    # gc_info,is history data in default
            young_gc_time_in_millis = data['jvm']['gc']['collectors']['young']['collection_time_in_millis']
            latest_young_gc_count = latest_data['jvm']['gc']['collectors']['young']['collection_count']
            latest_young_gc_time_in_millis = latest_data['jvm']['gc']['collectors']['young']['collection_time_in_millis']
            old_gc_count = data['jvm']['gc']['collectors']['old']['collection_count']
            old_gc_time_in_millis = data['jvm']['gc']['collectors']['old']['collection_time_in_millis']
            latest_old_gc_count = latest_data['jvm']['gc']['collectors']['old']['collection_count']
            latest_old_gc_time_in_millis = latest_data['jvm']['gc']['collectors']['old']['collection_time_in_millis']

            final_data['nodes_status']['indices']['search']['query_total'] = latest_query_total - query_total
            final_data['nodes_status']['indices']['search']['query_time_in_millis'] = \
                latest_query_time_in_millis - query_time_in_millis

            if 'timestamp' in latest_data['os'].keys():    # remove reduplicated data
                latest_data['os'].pop('timestamp')
            if 'timestamp' in latest_data['jvm'].keys():
                latest_data['jvm'].pop('timestamp')
            final_data['nodes_status']['os'] = latest_data['os']
            final_data['nodes_status']['jvm'] = latest_data['jvm']
            final_data['nodes_status']['jvm']['gc']['collectors']['young']['current_collection_count'] = \
                latest_young_gc_count - young_gc_count
            final_data['nodes_status']['jvm']['gc']['collectors']['young']['current_collection_time_in_millis'] = \
                latest_young_gc_time_in_millis - young_gc_time_in_millis
            final_data['nodes_status']['jvm']['gc']['collectors']['old']['current_collection_count'] = \
                latest_old_gc_count - old_gc_count
            final_data['nodes_status']['jvm']['gc']['collectors']['old']['current_collection_time_in_millis'] = \
                latest_old_gc_time_in_millis - old_gc_time_in_millis

            esindex = "%s-%s" % (esindex_prefix, time.strftime('%Y.%m.%d'))
            print(esindex)
            values.append({
                "_index": esindex,
                "_type": data_type,
                "_source": final_data
            })
        return values