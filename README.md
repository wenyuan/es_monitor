# es_monitor
脚本介绍
用于监控Elasticsearch集群的性能,实时发现和通知集群出现的问题
采集和存储服务器节点的信息(内存、cpu、gc等)、索引信息(健康状态、文档数和磁盘空间)
对采集到的信息,按天保存,结合kibana的可视化或三清云系统能够进行有效的历史数据分析

支持版本
Elasticsearch version:5.X
(6.X 版本舍弃了type的设定,如需兼容,需要做一些结构上的调整)

运行步骤
1.配置文件
vim config.ini
参数说明
ES下,分别是Elasticsearch服务器的ip、用于存储数据的索引名
nodes_module下,定义各采集模块的信息。data_structure是最后生成的数据结构,有nested和flat两种可以选择：
nested结构优点:节省生成的文档数,多节点的集群环境下具有一定的性能优化;缺点:不支持kibana可视化
flat结构优点:扁平化的结构是kiabna所支持的;缺点:会产生较多的docs,每个节点一个doc
所有数据结构都能被三清云所支持

2.安装所需包
sudo pip install -r requirements.txt

3.运行
python monitor.py

