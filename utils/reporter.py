# -*- coding:utf-8 -*-
import time
import ConfigParser
import smtplib
from email.mime.text import MIMEText
from email.header import Header


conf = ConfigParser.ConfigParser()
conf.read("config.ini")
sender = conf.get("EMAIL", "sender")
receiver = conf.get("EMAIL", "receiver").split(',')
username = conf.get("EMAIL", "username")
password = conf.get("EMAIL", "password")
smtp_server = conf.get("EMAIL", "smtpserver")


def send_email(subject, detail):
    subject = subject
    now_time = time.strftime('%Y-%m-%d %H:%M:%S')
    msg = MIMEText('<html><h2>'+now_time+'</h2><h2>'+detail+'</h2></html>', 'html', 'utf-8')    # 中文需参数‘utf-8’，单字节字符不需要
    msg['Subject'] = Header(subject, 'utf-8')
    smtp = smtplib.SMTP()
    smtp.connect(smtp_server)
    smtp.login(username, password)
    smtp.sendmail(sender, receiver, msg.as_string())
    smtp.quit()


if __name__ == "__main__":
    print(sender)
    print(username)
    print(password)
    print(receiver)
    send_email('python email test', 'hello world')
