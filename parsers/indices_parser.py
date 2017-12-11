# -*- coding:utf-8 -*-
import time
import copy

from utils.reporter import Reporter


class IndicesParser(object):

    def __init__(self):
        self.reporter = Reporter()

    def parse_data(self, indices_data, latest_indices_data, es_config_info):
        esindex_prefix = es_config_info['esindex_prefix']
        data_type = es_config_info['data_type']
        store_size_unit = es_config_info['store_size_unit']
        values = []
        timestamp = time.strftime('%Y-%m-%dT%H:%M:%S+08:00')
        store_size = 'store_size_in_' + store_size_unit
        pri_store_size = 'pri_store_size_in_' + store_size_unit
        final_data_template = {'@timestamp': timestamp, 'appname': 'monitor', 'type': data_type,
                               'indices_status': {'health': {}, 'status': {}, 'index_name': {}, 'uuid': {},
                                                  'pri': {}, 'rep': {}, 'docs_count': {}, 'docs_deleted': {},
                                                  store_size: {}, pri_store_size: {},
                                                  'added_docs_count': {}              # optional attr
                                                  }
                               }

        temp_container = {}                                                             # uuid:docs_count
        for index_data in indices_data:
            index_attr = index_data.strip().split()
            if not index_attr or len(index_attr) != 10:
                continue
            temp_container[index_attr[3]] = index_attr[6]

        for i, latest_index_data in enumerate(latest_indices_data):
            latest_index_attr = latest_index_data.strip().split()
            if not latest_index_attr or len(latest_index_attr) != 10:
                continue
            final_data = copy.deepcopy(final_data_template)
            final_data['indices_status']['health'] = latest_index_attr[0]
            final_data['indices_status']['status'] = latest_index_attr[1]
            final_data['indices_status']['index_name'] = latest_index_attr[2]
            final_data['indices_status']['uuid'] = latest_index_attr[3]
            final_data['indices_status']['pri'] = latest_index_attr[4]
            final_data['indices_status']['rep'] = latest_index_attr[5]
            final_data['indices_status']['docs_count'] = int(latest_index_attr[6])
            final_data['indices_status']['docs_deleted'] = int(latest_index_attr[7])

            store_size_value = self.store_size_unit_transition(store_size_unit, latest_index_attr[8], latest_index_attr[2])
            pri_store_size_value = self.store_size_unit_transition(store_size_unit, latest_index_attr[9], latest_index_attr[2])
            if store_size_value == -1 or pri_store_size_value == -1:
                continue
            final_data['indices_status'][store_size] = store_size_value
            final_data['indices_status'][pri_store_size] = pri_store_size_value

            if len(latest_indices_data) != len(indices_data):    # extra defined field
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

    # unit transition(只考虑bytes到gb,单索引存储太多的数据是一种ugly design)
    # todo...从时间复杂度上考虑,有没有更巧妙的算法来实现这个逻辑?
    def store_size_unit_transition(self, store_size_unit, store_size_value, index_name):
        if 'tb' in store_size_value:
            email_title = u'上海ES集群告警'
            email_detail = u'以下索引占用磁盘空间已经达到tb级别,请调整相关设置,该索引现在开始将不进行数据统计：' + index_name
            self.reporter.send_email(email_title, email_detail)
            return -1
        if store_size_unit == 'bytes':
            if store_size_value.endswith('gb'):
                store_size_value = float(store_size_value.strip('gb')) * 1024 * 1024 * 1024
            elif store_size_value.endswith('mb'):
                store_size_value = float(store_size_value.strip('mb')) * 1024 * 1024
            elif store_size_value.endswith('kb'):
                store_size_value = float(store_size_value.strip('kb')) * 1024
            else:
                store_size_value = float(store_size_value.strip('b'))
            return store_size_value
        elif store_size_unit == 'kb':
            if store_size_value.endswith('gb'):
                store_size_value = float(store_size_value.strip('gb')) * 1024 * 1024
            elif store_size_value.endswith('mb'):
                store_size_value = float(store_size_value.strip('mb')) * 1024
            elif store_size_value.endswith('kb'):
                store_size_value = float(store_size_value.strip('kb'))
            else:
                store_size_value = float(store_size_value.strip('b')) / 1024
            return store_size_value
        elif store_size_unit == 'mb':
            if store_size_value.endswith('gb'):
                store_size_value = float(store_size_value.strip('gb')) * 1024
            elif store_size_value.endswith('mb'):
                store_size_value = float(store_size_value.strip('mb'))
            elif store_size_value.endswith('kb'):
                store_size_value = float(store_size_value.strip('kb')) / 1024
            else:
                store_size_value = float(store_size_value.strip('b')) / 1024 / 1024
            return store_size_value
        else:
            if store_size_value.endswith('gb'):
                store_size_value = float(store_size_value.strip('gb'))
            elif store_size_value.endswith('mb'):
                store_size_value = float(store_size_value.strip('mb')) / 1024
            elif store_size_value.endswith('kb'):
                store_size_value = float(store_size_value.strip('kb')) / 1024 / 1024
            else:
                store_size_value = float(store_size_value.strip('b')) / 1024 / 1024 / 1024
            return store_size_value
