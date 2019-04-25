#!python
# -*- coding:utf-8 -*-
"""
邮件公用函数(发邮件用)
Created on 2015/1/15
Updated on 2019/4/3
@author: Holemar

本模块专门供发邮件用,支持html内容
"""
import os
import logging
import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

from email.utils import COMMASPACE, formatdate
from email import encoders
# python 2.3.*: email.Utils email.Encoders

import str_util

__all__ = ("send_mail",)
logger = logging.getLogger('libs_my.email_util')


def send_mail(host, user, password, to_list, **kwargs):
    """
    发邮件
    :param {string} host: 连接smtp服务器
    :param {string} user: 登陆账号
    :param {string} password: 登陆密码
    :param {list} to_list: 收信人列表, 如： ["收件人1 <to1@qq.com>", "to2@qq.com"]
    :param {string} From: 收到信时显示的发信人设置，如："测试邮件<daillo@163.com>"
    :param {string} Cc: 抄送人, 多人用英文逗号分开, 如："cc1@163.com, cc2@163.com"
    :param {string} BCc: 暗抄邮箱(有抄送效果,但抄送人列表不展示), 多人用英文逗号分开, 如："bcc1@163.com, bcc2@163.com"
    :param {string} Subject: 邮件主题
    :param {string} html: HTML 格式的邮件正文内容
    :param {string} text: 纯文本 格式的邮件正文内容(html格式的及纯文本格式的，只能传其中一个，以html参数优先)
    :param {list} files: 附件列表,需填入附件路径,如：["d:\\123.txt"]
    :return {bool}: 发信成功则返回 True,否则返回 False
    """
    # 添加邮件内容
    msg = MIMEMultipart()
    msg['Date'] = formatdate(localtime=True)

    # 发信人
    from_address = str_util.to_unicode(kwargs.get('From'))
    msg['From'] = from_address

    # 邮件主题
    Subject = kwargs.get('Subject')
    if Subject:
        msg['Subject'] = str_util.to_unicode(Subject) # 转编码,以免客户端看起来是乱码的

    # 邮件正文内容
    html = kwargs.get('html')
    text = kwargs.get('text')
    # HTML 格式的邮件正文内容
    if html:
        html = str_util.to_str(html)
        msg.attach(MIMEText(html, _subtype='html', _charset='utf-8'))
    # 纯文本 格式的邮件正文内容
    elif text:
        text = str_util.to_str(text)
        msg.attach(MIMEText(text, _subtype='plain', _charset='utf-8'))

    # 收信人列表
    if isinstance(to_list, basestring):
        to_list = [to_list]
    assert type(to_list) == list
    to_address = [str_util.to_str(to) for to in to_list]
    msg['To'] = COMMASPACE.join(to_address) # COMMASPACE==', '  # 收件人邮箱, 多人逗号分开

    # 抄送人, 多人用英文逗号分开
    cc_address = kwargs.get('Cc')
    if cc_address:
        msg['Cc'] = str_util.to_str(cc_address)
    # 暗抄邮箱, 多人用英文逗号分开
    bcc_address = kwargs.get('BCc')
    if bcc_address:
        msg['BCc'] = str_util.to_str(bcc_address)

    # 添加附件
    if 'files' in kwargs:
        files = kwargs.get('files') or []
        for file_path in files:
            # 文件路径
            file_path = str_util.to_unicode(file_path)
            # 文件名(不包含路径)
            file_name = os.path.basename(file_path)
            disposition = str_util.to_str(u'attachment; filename="%s"') % str_util.to_str(file_name)
            #disposition = str_util.to_str(disposition)
            # 取文件后缀
            suffix = file_path.split('.')[-1]
            suffix = suffix.lower()
            file_content = open(file_path, 'rb').read()
            # 处理图片附件
            if suffix in ('jpg', 'jpeg', 'bmp', 'png', 'gif',):
                image = MIMEImage(file_content)
                image.add_header('Content-ID', '<image1>')
                image.add_header('Content-Disposition', disposition)
                msg.attach(image)
            # 传送 txt 文件
            elif suffix == 'txt':
                att1 = MIMEText(file_content, _subtype='base64', _charset='utf-8')
                att1["Content-Type"] = 'application/octet-stream'
                att1["Content-Disposition"] = disposition
                msg.attach(att1)
            # 其它附件
            else:
                part = MIMEBase('application', 'octet-stream') #'octet-stream': binary data
                part.set_payload(file_content)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', disposition)
                msg.attach(part)

    # 发送邮件
    try:
        smtp = smtplib.SMTP()
        smtp.connect(host)  # 连接smtp服务器
        smtp.login(user, password)  # 登陆服务器
        smtp.sendmail(from_address, to_address, msg.as_string())  # 发送邮件
        smtp.close()
        return True
    except Exception, e:
        logger.error(u'发邮件错误:%s', e, exc_info=True)
        return False


if __name__ == '__main__':
    #错误信息邮件通知配置
    host = "smtp.163.com"
    user = "daillo@163.com"
    password = "01A0519163!@"
    text = """这是测试内容,见到请忽略...<br/>
    html代码测试：<font color='red'>红色字体</font>
    """
    params = {
        'From': u"测试邮件<daillo@163.com>" , # 这里可以任意设置，收到信后，将按照设置显示收件人
        'Subject': u"测试邮件。。。",
        #'Cc': '415372820@qq.com', # 抄送人
        'html': text, # 邮件内容
        'files': [ # 附近列表
            __file__,
            u'C:\\workspace\\备忘.txt', # 中文名称的文件名，会导致显示乱码，暂时无法解决
            'C:\\WebDisk2\\_同步\\picture_同步\\桌面\\1(3).jpg',
        ],
    }
    mail_to_list = ["292598441@qq.com", '收信 <daillo@qq.com>'] # 收信人,发多个人需要用列表,只用字符串则只发第一个
    res = send_mail(host, user, password, mail_to_list, **params)
    if res:
        print "发送成功"
    else:
        print "发送失败"

