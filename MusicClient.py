#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from urllib import parse
import base64
import json
import os
import random
import string
import time
import tkinter
import tkinter.filedialog
import tkinter.messagebox
import webbrowser

from Crypto.Cipher import AES
import binascii
import requests


class MusicAPI:
    def __init__(self, csrf, cookie):
        self.csrf = csrf
        self.cookie = cookie

    def getRandom(self):
        randomStr = ''.join(random.sample(
            string.ascii_letters + string.digits, 16))
        return randomStr

    def changeLength(self, text):
        pad = 16 - len(text) % 16
        text = text + pad * chr(pad)
        text = text.encode('utf-8')
        return text

    def aes(self, text, key):
        iv = b'0102030405060708'
        text = self.changeLength(text)
        cipher = AES.new(key.encode(), AES.MODE_CBC, iv)
        encrypted = cipher.encrypt(text)
        encrypt = base64.b64encode(encrypted).decode()
        return encrypt

    def jsFuncB(self, text, string):
        first = self.aes(text, '0CoJUm6Qyw8W8jud')
        second = self.aes(first, string)
        return second

    def jsFuncC(self, text):
        jsVarE = '010001'
        jsVarF = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
        text = text[::-1]
        result = pow(int(binascii.hexlify(text.encode()), 16),
                     int(jsVarE, 16), int(jsVarF, 16))
        return format(result, 'x').zfill(131)

    def getParam(self, text, string):
        params = self.jsFuncB(text, string)
        encSecKey = self.jsFuncC(string)
        return {'params': params, 'encSecKey': encSecKey}

    def getList(self, params, encSecKey):
        url = 'https://music.163.com/weapi/cloudsearch/get/web?csrf_token=' + self.csrf
        payload = 'params=' + \
            parse.quote(params) + '&encSecKey=' + parse.quote(encSecKey)
        headers = {
            'authority': 'music.163.com',
            'user-agent': 'Mozilla/5.0 (X11; Linux armv7l) AppleWebKit/537.36 (KHTML, like Gecko) Raspbian Chromium/78.0.3904.108 Chrome/78.0.3904.108 Safari/537.36',
            'content-type': 'application/x-www-form-urlencoded',
            'accept': '*/*',
            'origin': 'https://music.163.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://music.163.com/search/',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cookie': self.cookie}
        response = requests.request('POST', url, headers=headers, data=payload)
        return response.text

    def getUrl(self, params, encSecKey):
        url = 'https://music.163.com/weapi/song/enhance/player/url/v1?csrf_token=' + self.csrf
        payload = 'params=' + \
            parse.quote(params) + '&encSecKey=' + parse.quote(encSecKey)
        headers = {
            'authority': 'music.163.com',
            'user-agent': 'Mozilla/5.0 (X11; Linux armv7l) AppleWebKit/537.36 (KHTML, like Gecko) Raspbian Chromium/78.0.3904.108 Chrome/78.0.3904.108 Safari/537.36',
            'content-type': 'application/x-www-form-urlencoded',
            'accept': '*/*',
            'origin': 'https://music.163.com',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'referer': 'https://music.163.com/',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cookie': self.cookie}
        response = requests.request('POST', url, headers=headers, data=payload)
        return response.text

    def parseUrl(self, songId, randomParam):
        jsVarD = {
            'ids': '[' + str(songId) + ']',
            'level': 'standard',
            'encodeType': '',
            'csrf_token': self.csrf}
        jsVarD = json.dumps(jsVarD)
        param = self.getParam(jsVarD, randomParam)
        songResult = self.getUrl(param['params'], param['encSecKey'])
        if len(songResult) > 0:
            songResult = json.loads(songResult)
            try:
                songUrl = json.dumps(
                    songResult['data'][0]['url'], ensure_ascii='False')
            except IndexError:
                return None
            return songUrl
        else:
            return None

    def getSong(self, name):
        jsVarD = {
            'hlpretag': "<span class='s-fc7'>",
            'hlposttag': '</span>',
            's': name,
            'type': '1',
            'offset': '0',
            'total': 'true',
            'limit': '30',
            'csrf_token': self.csrf}
        jsVarD = json.dumps(jsVarD)
        randomParam = self.getRandom()
        param = self.getParam(jsVarD, randomParam)
        resultList = self.getList(param['params'], param['encSecKey'])
        returnList = []
        if len(resultList) > 0:
            try:
                resultList = json.loads(resultList)['result']['songs']
            except KeyError:
                return None
            for i, item in enumerate(resultList):
                item = json.dumps(item)
                name = json.loads(str(item))['name']
                author = json.loads(str(item))['ar']
                temp = []
                for i in author:
                    temp.append(i['name'])
                author = temp
                songUrl = self.parseUrl(
                    str(json.loads(str(item))['id']), randomParam)
                if songUrl is not None:
                    returnList.append(
                        {'name': name, 'author': author, 'url': songUrl})
                else:
                    pass
            return returnList
        else:
            return returnList


class MusicApp:
    def __init__(self, window):
        window.title('登录')
        self.frame = tkinter.Frame(window)
        self.frame.pack()
        if os.path.isfile(
            os.getcwd() +
            os.sep +
            'config' +
            os.sep +
                'config.json'):
            with open('config/config.json', 'r') as f:
                config = f.read()
            config = json.loads(config)
            self.csrf = config['csrf']
            self.cookie = config['cookie']
            self.hasConfig = True
            self.login()
        else:
            self.hasConfig = False
            self.labelCsrf = tkinter.Label(self.frame, text='输入你的csrf：')
            self.labelCsrf.grid(row=0, column=0, sticky=tkinter.W)
            self.entryCsrf = tkinter.Entry(self.frame, show='*')
            self.entryCsrf.grid(row=0, column=1, sticky=tkinter.W)
            self.labelCookie = tkinter.Label(self.frame, text='输入你的cookie：')
            self.labelCookie.grid(row=1, column=0, sticky=tkinter.W)
            self.entryCookie = tkinter.Entry(self.frame, show='*')
            self.entryCookie.grid(row=1, column=1, sticky=tkinter.W)
            self.buttonLogin = tkinter.Button(
                self.frame, text='登录', command=self.login)
            self.buttonLogin.grid(row=2, column=1, sticky=tkinter.W)

    def login(self):
        if not self.hasConfig:
            self.csrf = self.entryCsrf.get()
            self.cookie = self.entryCookie.get()
            self.labelCsrf.grid_forget()
            self.entryCsrf.grid_forget()
            self.labelCookie.grid_forget()
            self.entryCookie.grid_forget()
            self.buttonLogin.grid_forget()
            if not os.path.lexists(os.getcwd() + os.sep + 'config' + os.sep):
                os.mkdir('config')
            with open('config/config.json', 'w') as f:
                writeDict = {'csrf': self.csrf, 'cookie': self.cookie}
                json.dump(writeDict, f)
        else:
            pass
        self.API = MusicAPI(self.csrf, self.cookie)
        window.title('客户端')
        self.varMode = tkinter.IntVar()
        self.varMode.set(1)
        self.modeList = [('通过歌名搜索', 1), ('通过歌曲ID获取下载链接', 2)]
        for text, num in self.modeList:
            self.buttonMode = tkinter.Radiobutton(
                self.frame, text=text, variable=self.varMode, value=num)
            self.buttonMode.grid(row=num - 1, column=0, sticky=tkinter.W)
        self.searchLabel = tkinter.Label(self.frame, text='输入目标（ID或歌名）：')
        self.searchLabel.grid(row=2, column=0, sticky=tkinter.W)
        self.searchEntry = tkinter.Entry(self.frame)
        self.searchEntry.grid(row=3, column=0, sticky=tkinter.W)
        self.searchButton = tkinter.Button(
            self.frame, text='查询', command=self.search)
        self.searchButton.grid(row=3, column=0, sticky=tkinter.E)
        self.resultText = tkinter.Text(
            self.frame, width=50, height=20, state=tkinter.DISABLED)
        self.resultText.grid(row=5, column=0, sticky=tkinter.W)
        self.clearButton = tkinter.Button(
            self.frame, text='清空', command=self.clear)
        self.clearButton.grid(row=6, column=0, sticky=tkinter.E)

    def search(self):
        if self.varMode.get() == 1:
            resultList = self.API.getSong(self.searchEntry.get())
            self.clear()
            self.resultText.config(state=tkinter.NORMAL)
            if resultList is None:
                self.resultText.insert(tkinter.INSERT, '出现错误！')
            else:
                for i in resultList:
                    self.resultText.insert(
                        tkinter.INSERT, '歌名：' + i['name'] + '，歌手：' + str(i['author']) + '，下载链接：')
                    self.resultText.window_create(
                        tkinter.INSERT,
                        window=tkinter.Button(
                            self.resultText,
                            text='点我打开',
                            command=lambda i=i: webbrowser.open(
                                i['url'].strip('"'),
                                new=0)))
                    self.resultText.window_create(
                        tkinter.INSERT,
                        window=tkinter.Button(
                            self.resultText,
                            text='点我保存',
                            command=lambda i=i: self.save(
                                i['url'].strip('"'))))
                    self.resultText.insert(tkinter.INSERT, '\n')
            self.resultText.config(state=tkinter.DISABLED)
        elif self.varMode.get() == 2:
            resultStr = self.API.parseUrl(
                self.searchEntry.get(), self.API.getRandom())
            self.clear()
            self.resultText.config(state=tkinter.NORMAL)
            if resultStr is None:
                self.resultText.insert(tkinter.INSERT, '出现错误！')
            else:
                self.resultText.insert(tkinter.INSERT, '下载链接：')
                self.resultText.window_create(
                    tkinter.INSERT,
                    window=tkinter.Button(
                        self.resultText,
                        text='点我打开',
                        command=lambda resultStr=resultStr: webbrowser.open(
                            resultStr.strip('"'),
                            new=0)))
                self.resultText.window_create(
                    tkinter.INSERT,
                    window=tkinter.Button(
                        self.resultText,
                        text='点我保存',
                        command=lambda resultStr=resultStr: self.save(
                            resultStr.strip('"'))))
            self.resultText.config(state=tkinter.DISABLED)
        else:
            self.clear()
            self.resultText.config(state=tkinter.NORMAL)
            self.resultText.insert(tkinter.INSERT, '出现错误！')
            self.resultText.config(state=tkinter.DISABLED)

    def clear(self):
        self.resultText.config(state=tkinter.NORMAL)
        self.resultText.delete(1.0, tkinter.END)
        self.resultText.config(state=tkinter.DISABLED)
        self.searchEntry.delete(0, tkinter.END)

    def save(self, url):
        if url.endswith('.m4a'):
            fileFormat = '.m4a'
        elif url.endswith('.mp3'):
            fileFormat = '.mp3'
        else:
            return tkinter.messagebox.showerror('错误', '出错了！')
        filePath = tkinter.filedialog.asksaveasfilename(
            defaultextension=fileFormat, filetypes=[
                ('音乐文件', fileFormat)], title='选择保存位置')
        response = requests.get(url)
        with open(filePath, 'wb') as f:
            f.write(response.content)


if __name__ == '__main__':
    window = tkinter.Tk()
    app = MusicApp(window)
    window.mainloop()
