#coding:utf-8
import requests
from pyquery import PyQuery as pq
import time
import json
import re
import pytesseract
from PIL import Image
import logging
import threading
import datetime
from qrcodeHelper import QrcHelper

class Kouzhao(threading.Thread):
    """docstring for Kouzhao"""
    def __init__(self, phone, id_card, realname):
        super(Kouzhao, self).__init__()
        self.phone = phone
        self.id_card = id_card
        self.realname = realname
        self.cookie = ''
        self.token = ''
        self.qr_path = './qr.png'
        self.qrcode = ''

    def run(self):
        self.get_token_and_cookie()
        rt = '验证码错误'
        while rt=='验证码错误':
            self.get_qrcode()
            rt = self.do_yuyue()

        
    def get_token_and_cookie(self):
        while True:
            url = 'http://lerentang.yihecm.com/?m=yuyuelist&id=1'
            r = requests.get(url)
            if r.status_code==200:
                m = re.search(r"var token='(.+)'", r.text)
                if m:
                    self.token =  m.group(1)
                _cookie = r.headers['Set-Cookie']
                _cookie = _cookie.split(';')
                self.cookie = _cookie[0]

                logging.error('token：{0}'.format(self.token))
                logging.error('cookie：{0}'.format(self.cookie))
                break

    def get_qrcode(self):
        self.qrcode = ''
        while len(self.qrcode)!=4:
            self.get_qrcode_img()
            qh = QrcHelper(qr_path='./qr.png', is_with_api=True)
            self.qrcode = qh.fuck_qrcode_img()
        return self.qrcode

    def get_qrcode_img(self):
        headers = {
            'Cookie':self.cookie,
        }
        while True:
            url = 'http://lerentang.yihecm.com/core/common/yzm.php?{0}'.format(time)
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                with open(self.qr_path , 'wb') as f:
                    f.write(r.content)
                logging.warning("验证码图片：{0}".format(self.qr_path))
                break

    def do_yuyue(self):
        url = 'http://lerentang.yihecm.com/?m=save'

        headers = {
            'Cookie':self.cookie,
        }
        
        today = datetime.date.today() #获得今天的日期
        tomorrow = today + datetime.timedelta(days=1)
        pickdate = tomorrow.strftime('%Y-%m-%d')

        data = {
            'realname': self.realname,
            'phone': self.phone,
            'shenfenzheng': self.id_card,
            'area': '15',
            'shop': '48',
            'pickdate': pickdate,
            'picktime': '13:00-15:00',
            'shuliang': '5',
            'pid': '1',
            'yzm': self.qrcode,
            'token': self.token,
        }

        while True:
            r = requests.post(url, data=data, headers=headers)
            if r.status_code==200:
                with open('预约结果.txt', 'a') as f:
                    f.write('\n{0}'.format(r.text))
                    j = json.loads(r.text)
                    if j[0]==1:
                        f.write("\n{0}，{1}，预约成功".format(self.realname, self.id_card))
                logging.warning("预约结果：{0}".format(j[1]))
                return j[1]


if __name__ == '__main__':
    k = Kouzhao(
        phone='18712151501', 
        id_card='130102199303073476', 
        realname='秦帅'
        )
    k.start()
