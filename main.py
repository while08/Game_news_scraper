from pathlib import Path
import json
import requests

#translate()
from hashlib import md5
import random

#local utils
from websites.C import C
from websites.WindowsCentral import WindowsCentral
from websites.AlineaAnalytics import AlineaAnalytics
from websites.Mp1st import Mp1st
from websites.VGC import VGC
from websites.GameStop import GameStop
from websites.TheVerge import TheVerge

#type hints
from abc import ABC
from typing import ClassVar, Protocol



class WebSiteAbc(ABC):#abc for websiteOperate class
    
    #show_articles()
    article_url_path: ClassVar[Path]
    show_amount: ClassVar[int]
    alias: ClassVar[str]



class ClassProtocol(Protocol):#solve cross-parent class dependency problem

    #show_articles()
    get_article_url: ClassVar
    article_url_path: ClassVar
    show_amount: ClassVar
    alias: ClassVar

    #output_article()
    get_write_body: ClassVar
    cls_output_article: ClassVar


"""
Text
    Structure
        wensite.py: Single_website_scraper_method_class
        websites: All websites' scraper script
        database: Contain body_html file and arricle_url.jsonl from scrapers
        main.py: Create websiteOperate class that inherits from a Basic class

    methods of Basic class
        show_articles: 
        output_article:
"""



class Basic(ClassProtocol):
    
    current_article_list = []


    @classmethod
    def show_articles(cls, update=False, show_all=False, show=True):
        """    Require class attribute
        cls.article_url_path: Path | Point to project database direction.
        cls.show_amount: int | Decide show amount of artiles
    Result
        Pass particular website's article_url to 'current_article_list', for future selection operates."""
        
        if update == True:
            cls.get_write_body()
            print('\n')
            cls.get_article_url()
            print('\n')
        
        try:
            with open(str(cls.article_url_path), 'r', encoding='utf-8') as f:
                title_url_list: list = []
                for line in f:
                    dict = json.loads(line.strip())
                    dict['class'] = cls
                    title_url_list.append(dict)
        except Exception as e:
            print(C.RED(f'[!{cls.alias}]Raise error while reading article url: {e}'))
            return
            
        #cut and write title_hrep_list to Basic attribute
        if show_all == False: title_url_list = title_url_list[:cls.show_amount]
        Basic.current_article_list = title_url_list
        
        #print titles
        if show == True:
            for i, x in enumerate(title_url_list, 1):
                print(C.GREEN(f'[{i}] ') + next(iter(x)))
            print('\n')


    @classmethod
    def output_article(cls, idx: int):
        """write artucle to local direction: ~/storage/shared/ArticleOutput/website_name/datetime/...
        download picture to ArticleOutput/website_name/datetime/article_title/..."""
        
        try:    #get target article url
            target_url = Basic.current_article_list[idx-1]
        except IndexError:
            print(C.RED('[!]Index not found.'))
            return False
        
        #process and write article to local
        cls.cls_output_article(target_url)



    @classmethod
    def translate(cls, idx: int):
        
        trans_api = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
        appid = '20250822002436409'
        try:
            q = next(iter(Basic.current_article_list[idx-1]))
        except IndexError:
            print(C.RED('[!]Index not found.'))
            return False
        salt = random.randint(32768, 65536)
        key = 'Gef7sZTzRNdAnxMkhfso'
        sign_str = appid + q + str(salt) + key
        sign = md5(sign_str.encode(encoding='utf-8')).hexdigest()
        params = {'q': q, 'from': 'en', 'to': 'zh', 'appid': appid, 'salt': salt, 'sign': sign, 'needIntervene': 1}
        
        print(C.YELLOW('[log]Getting translate response...'))
        trans_response = requests.get(trans_api, params=params)
        response_json = json.loads(trans_response.text)
        
        try:
            dst = response_json['trans_result'][0]['dst']
            print(C.GREEN(f'[{idx}-Trans]') + dst)
        except (KeyError, IndexError):
            err_code = response_json['error_code']
            err_msg = response_json['error_msg']
            print(C.RED(f'[!Trans]Error code: {err_code}, error message: {err_msg}'))
        



class WinCentOp(WebSiteAbc, WindowsCentral, Basic):
    alias = 'Win'
    show_amount = 10

class AAOp(WebSiteAbc, AlineaAnalytics, Basic):
    alias = 'AA'
    show_amount = 5

class Mp1Op(WebSiteAbc, Mp1st, Basic):
    alias = 'Mp1'
    show_amount = 10

class VGCOp(WebSiteAbc, VGC, Basic):
    alias = 'VGC'
    show_amount = 7

class GSOp(WebSiteAbc, GameStop, Basic):
    alias = 'GS'
    show_amount = 10

class VergOp(WebSiteAbc, TheVerge, Basic):
    alias = 'Veg'
    show_amount = 7
    



class CommandLineInterface(Basic):
    pass

if __name__ == '__main__':
    VergOp.show_articles()
    VergOp.translate(2)
    VergOp.output_article(4)
    VergOp.output_article(7)
    pass



