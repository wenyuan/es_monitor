# es_monitor
a script to monitor nodes status </br>
support elasticsearch version:5.X (es6.X has deprecated type in index, need a little change)

###运行步骤
1.配置文件
vim config.ini

2.确认最终所需数据的数据结构</br> 
**需要nested结构的数据** 

    main.py中开头导的包为 from parsers.data_parser import parse_data

    修改 initjob.es_template.py中,使用body
**需要扁平化结构的数据**

    main.py中开头导的包为 from parsers.data_parser_V1 import parse_data

    修改initjob.es_template.py中,使用 body_V1

3.安装所需包
sudo pip install -r requirements.txt

4.运行
python main.py

