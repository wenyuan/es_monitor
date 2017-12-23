# -*- coding:utf-8 -*-
import time
import pycurl
import StringIO
import ConfigParser
import logging.config
from elasticsearch import Elasticsearch
from elasticsearch import helpers

from utils.reporter import Reporter
from parsers.indices_parser import IndicesParser
from config.logging_config import CONFIG_PATH, LOGGING

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('indices_checker')


class IndicesChecker(object):

    def __init__(self):
        conf = ConfigParser.ConfigParser()
        conf.read(CONFIG_PATH)
        self.es_url = conf.get("ES", "es_url")
        self.esindex_prefix = conf.get("ES", "esindex_prefix")
        self.data_type = conf.get("indices_module", "data_type")
        self.sampling_speed = int(conf.get("indices_module", "sampling_speed"))
        self.store_size_unit = conf.get("indices_module", "store_size_unit")

        self.indices_parser = IndicesParser()
        self.reporter = Reporter()

    def start_indices_task(self):
        if_send_email = True
        while True:
            logger.info('Start indices_checker')
            try:
                es = Elasticsearch(self.es_url)
                indices_data = self.get_indices_status(self.es_url)
                time.sleep(self.sampling_speed)
                values = self.make_indices_data(indices_data)
                self.send_data(es, values)
                if_send_email = True
                for conn in es.transport.connection_pool.connections:
                    conn.pool.close()
                logger.info('Indices_checker is running normally')
            except pycurl.error:
                if if_send_email:
                    email_title = u'上海ES集群告警'
                    email_detail = u'以下节点或整个集群出现异常,请进行检查:' + self.es_url
                    self.reporter.send_email(email_title, email_detail)
                    if_send_email = False
                    logger.warn('Indices_checker fails to connect to es, we will send an alert e-mail')
                else:
                    logger.warn('Indices_checker fails to connect to es, we have already sent an alert e-mail')
            except Exception as e:
                logger.error('Some exception happened to indices_checker, details are as follows:')
                logger.error(e)
            finally:
                logger.info('Finish indices_checker\n')

    def get_indices_status(self, es_url):
        b = StringIO.StringIO()
        c = pycurl.Curl()
        c.setopt(pycurl.URL, 'http://'+es_url+':9200/_cat/indices')
        c.setopt(pycurl.WRITEFUNCTION, b.write)
        c.perform()
        body = b.getvalue()
        c.close()
        return body.split('\n')

    def make_indices_data(self, indices_data):
        latest_indices_data = self.get_indices_status(self.es_url)
        es_config_info = {'esindex_prefix': self.esindex_prefix, 'data_type': self.data_type, 'store_size_unit': self.store_size_unit}
        return self.indices_parser.parse_data(indices_data, latest_indices_data, es_config_info)

    def send_data(self, es, values):
        helpers.bulk(es, values)


if __name__ == "__main__":
    #indices_checker = IndicesChecker()
    #indices_checker.start_indices_task()
    es = Elasticsearch("192.168.10.50")
    print(es.cluster.health())
    for conn in es.transport.connection_pool.connections:    # 这里是手写的关闭连接,Will McGinnis已经更新close接口到源码,坐等pip库更新
        conn.pool.close()
    print(es.cluster.health())
