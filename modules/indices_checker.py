# -*- coding:utf-8 -*-
import time
import pycurl
import StringIO
import ConfigParser
from elasticsearch import Elasticsearch
from elasticsearch import helpers

from utils.reporter import Reporter
from parsers.indices_parser import IndicesParser


class IndicesChecker(object):

    def __init__(self):
        conf = ConfigParser.ConfigParser()
        conf.read('config.ini')
        self.es_url = conf.get("ES", "es_url")
        self.esindex_prefix = conf.get("ES", "esindex_prefix")
        self.data_type = conf.get("indices_module", "data_type")
        self.sampling_speed = int(conf.get("indices_module", "sampling_speed"))
        self.store_size_unit = conf.get("indices_module", "store_size_unit")

        self.indices_parser = IndicesParser()
        self.reporter = Reporter()

    def start_indices_task(self):
        es = Elasticsearch(self.es_url)
        if_send_email = True
        while True:
            try:
                indices_data = self.get_indices_status(self.es_url)
                time.sleep(self.sampling_speed)
                values = self.make_indices_data(indices_data)
                self.send_data(es, values)
                if_send_email = True
            except pycurl.error:
                if if_send_email:
                    email_title = u'上海ES集群告警'
                    email_detail = u'以下节点或整个集群出现异常,请进行检查:' + self.es_url
                    self.reporter.send_email(email_title, email_detail)
                    if_send_email = False

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
    indices_checker = IndicesChecker()
    indices_checker.start_indices_task()
