#!usr/bin/env python
# coding:utf-8

import pytesseract
from PIL import Image
import numpy as np
import re
import logging
import os
import base64
import requests

class QrcHelper(object):
    """docstring for QrcHelper"""
    def __init__(self, qr_path='./qr.png', is_with_api=False):
        super(QrcHelper, self).__init__()
        self.qr_path = qr_path
        self.is_with_api = is_with_api
        

    def fuck_qrcode_img(self):
        image = Image.open(self.qr_path)
        #code = pytesseract.image_to_string(image) #图片进行识别
        #logging.warning('原图：{0}'.format(code))

        #0. 灰度
        w, h = image.size
        image = image.convert('L')  #转化为灰度图

        #1. 二值化
        threshold = 180             #设定的二值化阈值
        #遍历所有像素，大于阈值的为黑色
        pixdata = image.load()
        for y in range(h):
            for x in range(w):
                if pixdata[x, y] < threshold:
                    pixdata[x, y] = 0
                else:
                    pixdata[x, y] = 255
        image.save('./qr2.png')
        #code = pytesseract.image_to_string(image) #图片进行识别
        #logging.warning('二值：{0}'.format(code))

        #2. 去燥
        pixdata = image.load()
        for y in range(0, h-1):
            for x in range(0 ,w-1):
                count = 0
                if pixdata[x,y-1] > 245:#上
                    count = count + 1
                if pixdata[x,y+1] > 245:#下
                    count = count + 1
                if pixdata[x-1,y] > 245:#左
                    count = count + 1
                if pixdata[x+1,y] > 245:#右
                    count = count + 1
                if pixdata[x-1,y-1] > 245:#左上
                    count = count + 1
                if pixdata[x-1,y+1] > 245:#左下
                    count = count + 1
                if pixdata[x+1,y-1] > 245:#右上
                    count = count + 1
                if pixdata[x+1,y+1] > 245:#右下
                    count = count + 1
                if count > 7:
                    pixdata[x,y] = 255
        image.save('./qr3.png')

        txtqr = pytesseract.image_to_string(image) #对去噪后的图片进行识别
        if self.is_with_api:
            txtqr = self.fuck_with_api(qr_path='./qr3.png')

        m = re.findall(r'[a-zA-Z\d]', txtqr) #只要数字及字母
        code = ''.join(m) #合并成字符串
        result = code.upper() #转换为大写

        logging.warning('识别验证码：{0}'.format(result))

        return result


    def fuck_with_api(self, qr_path):
        result = ''
        request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/general_basic"
        # 二进制方式打开图片文件
        f = open(qr_path, 'rb')
        img = base64.b64encode(f.read())

        params = {"image":img}
        access_token = '24.d00887283c602fb6a6e702b8000c5f94.2592000.1587467701.282335-19004215'
        request_url = request_url + "?access_token=" + access_token
        headers = {'content-type': 'application/x-www-form-urlencoded'}
        response = requests.post(request_url, data=params, headers=headers)
        if response:
            j = response.json()
            if j['words_result_num']>0:
                result = j['words_result'][0]['words']
        logging.warning('接口识别：{0}'.format(result))
        return result


if __name__ == '__main__':
    q = QrcHelper(is_with_api=True)
    q.fuck_qrcode_img()

