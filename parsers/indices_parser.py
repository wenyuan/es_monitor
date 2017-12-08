# -*- coding:utf-8 -*-

import time
import copy


class IndicesParser(object):

    def parse_data(self, indices_data, latest_indices_data, es_config_info):
        esindex_prefix = es_config_info['esindex_prefix']
        data_type = es_config_info['data_type']
        values = []
        timestamp = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
        final_data_template = {'@timestamp': timestamp, 'appname': 'monitor', 'type': data_type,
                               'indices_status': {'health': {}, 'status': {}, 'index_name': {}, 'uuid': {},
                                                  'pri': {}, 'rep': {}, 'docs_count': {}, 'docs_deleted': {},
                                                  'store_size': {}, 'pri_store_size': {},
                                                  'added_docs_count': {}              # optional attr
                                                  }
                               }

        temp_container = {}                                                             # uuid:docs_count
        for index_data in indices_data:
            index_attr = index_data.strip().split()
            if not index_attr:
                break
            temp_container[index_attr[3]] = index_attr[6]

        for i, latest_index_data in enumerate(latest_indices_data):
            latest_index_attr = latest_index_data.strip().split()
            if not latest_index_attr:
                break
            final_data = copy.deepcopy(final_data_template)
            final_data['indices_status']['health'] = latest_index_attr[0]
            final_data['indices_status']['status'] = latest_index_attr[1]
            final_data['indices_status']['index_name'] = latest_index_attr[2]
            final_data['indices_status']['uuid'] = latest_index_attr[3]
            final_data['indices_status']['pri'] = latest_index_attr[4]
            final_data['indices_status']['rep'] = latest_index_attr[5]
            final_data['indices_status']['docs_count'] = int(latest_index_attr[6])
            final_data['indices_status']['docs_deleted'] = int(latest_index_attr[7])
            final_data['indices_status']['store_size'] = latest_index_attr[8]
            final_data['indices_status']['pri_store_size'] = latest_index_attr[9]

            if len(latest_indices_data) != len(indices_data):
                final_data['indices_status']['added_docs_count'] = 0
            elif final_data['indices_status']['uuid'] not in temp_container:
                final_data['indices_status']['added_docs_count'] = 0
            else:
                docs_count = temp_container[final_data['indices_status']['uuid']]
                added_docs_count = int(latest_index_attr[6]) - int(docs_count)
                final_data['indices_status']['added_docs_count'] = added_docs_count

            esindex = "%s-%s" % (esindex_prefix, time.strftime('%Y.%m.%d'))

            values.append({
                "_index": esindex,
                "_type": data_type,
                "_source": final_data
            })
        return values