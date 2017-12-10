# -*- coding:utf-8 -*-
import time
import json
import pycurl
import StringIO
import ConfigParser
from elasticsearch import Elasticsearch
from elasticsearch import helpers

from utils.reporter import Reporter
from parsers.nodes_parser import NodesParser
from initjob.es_template import EsTemplate


class NodesChecker(object):

    def __init__(self):
        conf = ConfigParser.ConfigParser()
        conf.read('config.ini')
        self.es_url = conf.get("ES", "es_url")
        self.esindex_prefix = conf.get("ES", "esindex_prefix")
        self.data_type = conf.get("nodes_module", "data_type")
        self.sampling_speed = int(conf.get("nodes_module", "sampling_speed"))
        self.data_structure = conf.get("nodes_module", "data_structure")
        self.nodes_total_count = conf.get("nodes_module", "nodes_total_count")

        self.nodes_parser = NodesParser()
        self.es_template = EsTemplate()
        self.reporter = Reporter()

    def start_nodes_task(self):
        es = Elasticsearch(self.es_url)
        self.es_template.make_nodes_template(self.es_url, self.data_structure)
        if_send_email = True
        latest_check_time = time.strftime('%Y-%m-%dT%H时')
        while True:
            try:
                nodes_count, nodes_data = self.get_nodes_status(self.es_url)
                if nodes_count < int(self.nodes_total_count) and time.strftime('%Y-%m-%dT%H时') != latest_check_time:
                    email_title = u'上海ES集群告警'
                    email_detail = u'该集群共有' + str(self.nodes_total_count) + u'个节点,目前只有' + str(nodes_count) + u'个处于正常状态,请检查!'
                    self.reporter.send_email(email_title, email_detail)
                    latest_check_time = time.strftime('%Y-%m-%dT%H时')
                time.sleep(self.sampling_speed)
                values = self.make_nodes_data(nodes_count, nodes_data)
                self.send_data(es, values)
                if_send_email = True
            except pycurl.error:
                if if_send_email:
                    email_title = u'上海ES集群告警'
                    email_detail = u'以下节点或整个集群出现异常,请进行检查:' + self.es_url
                    self.reporter.send_email(email_title, email_detail)
                    if_send_email = False

    def get_nodes_status(self, es_url):
        b = StringIO.StringIO()
        c = pycurl.Curl()
        c.setopt(pycurl.URL, 'http://'+es_url+':9200/_nodes/stats/indices,os,process,jvm/search')
        c.setopt(pycurl.WRITEFUNCTION, b.write)
        c.perform()
        body = b.getvalue()
        c.close()
        data = json.loads(body)
        nodes_data = data['nodes']
        nodes_count = len(nodes_data.keys())
        return nodes_count, nodes_data

    def make_nodes_data(self, nodes_count, nodes_data):
        latest_nodes_count, latest_nodes_data = self.get_nodes_status(self.es_url)
        if latest_nodes_count < nodes_count:
            node_ip_list = [nodes_data[node]['ip'].split(':')[0] for node in nodes_data.keys()]
            latest_node_ip_list = [latest_nodes_data[node]['ip'].split(':')[0] for node in latest_nodes_data.keys()]
            lost_node_ip = [node_ip for node_ip in node_ip_list if node_ip not in latest_node_ip_list]
            email_title = u'上海ES集群告警'
            email_detail = u'以下节点的ES从原集群中脱离了,请进行检查:' + str(lost_node_ip)
            self.reporter.send_email(email_title, email_detail)
            return []
        elif latest_nodes_count > nodes_count:
            node_ip_list = [nodes_data[node]['ip'].split(':')[0] for node in nodes_data.keys()]
            latest_node_ip_list = [latest_nodes_data[node]['ip'].split(':')[0] for node in latest_nodes_data.keys()]
            added_node_ip = [latest_node_ip for latest_node_ip in latest_node_ip_list if latest_node_ip not in node_ip_list]
            email_title = u'上海ES集群告警'
            email_detail = u'新加入了以下节点,请确认:' + str(added_node_ip)
            self.reporter.send_email(email_title, email_detail)
            return []
        else:
            es_config_info = {'esindex_prefix': self.esindex_prefix, 'data_type': self.data_type}
            if self.data_structure == 'flat':
                return self.nodes_parser.parse2flat_data(nodes_data, latest_nodes_data, es_config_info)
            else:
                return self.nodes_parser.parse2nested_data(nodes_data, latest_nodes_data, es_config_info)

    def send_data(self, es, values):
        helpers.bulk(es, values)

if __name__ == "__main__":
    nodes_parser = NodesChecker()
    nodes_parser.start_nodes_task()
