#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import threading
from time import ctime
import logging.config

from modules.nodes_checker import NodesChecker
from modules.indices_checker import IndicesChecker
from config.logging_config import LOGGING

logging.config.dictConfig(LOGGING)
logger = logging.getLogger('monitor')


class Monitor(object):

    def __init__(self):
        self.nodes_checker = NodesChecker()
        self.indices_checker = IndicesChecker()

    def nodes_task(self, func):
        logger.info("%s %s" % (func, time.strftime('%Y-%m-%d %H:%M:%S')))
        self.nodes_checker.start_nodes_task()

    def indices_task(self, func):
        logger.info("%s %s" % (func, time.strftime('%Y-%m-%d %H:%M:%S')))
        self.indices_checker.start_indices_task()

    def main_task(self):
        threads = []
        t1 = threading.Thread(target=self.nodes_task, args=('开始运行采集节点信息的脚本',))
        threads.append(t1)
        t2 = threading.Thread(target=self.indices_task, args=('开始运行采集索引信息的脚本',))
        threads.append(t2)

        for thread in threads:
            thread.setDaemon(True)
            thread.start()
        while True:
            alive = False
            for thread in threads:
                alive = alive or thread.isAlive()
            if not alive:
                break
            time.sleep(3)
        logger.info("all tasks over %s" % ctime())


if __name__ == "__main__":
    monitor = Monitor()
    monitor.main_task()
