# -*- coding:utf-8 -*-
import time
import ConfigParser
import smtplib
from email.mime.text import MIMEText
from email.header import Header


class Reporter(object):

    def __init__(self):
        conf = ConfigParser.ConfigParser()
        conf.read("config.ini")
        self.sender = conf.get("EMAIL", "sender")
        self.receiver = conf.get("EMAIL", "receiver").split(',')
        self.username = conf.get("EMAIL", "username")
        self.password = conf.get("EMAIL", "password")
        self.smtp_server = conf.get("EMAIL", "smtpserver")

    def send_email(self, subject, detail):
        subject = subject
        now_time = time.strftime('%Y-%m-%d %H:%M:%S')
        msg = MIMEText('<html><h2>'+now_time+'</h2><h2>'+detail+'</h2></html>', 'html', 'utf-8')    # 中文需参数‘utf-8’，单字节字符不需要
        msg['Subject'] = Header(subject, 'utf-8')
        smtp = smtplib.SMTP()
        smtp.connect(self.smtp_server)
        smtp.login(self.username, self.password)
        smtp.sendmail(self.sender, self.receiver, msg.as_string())
        smtp.quit()


if __name__ == "__main__":
    reporter = Reporter()
    print(reporter.sender)
    print(reporter.username)
    print(reporter.password)
    print(reporter.receiver)
    reporter.send_email('python email test', 'hello world')