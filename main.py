from pathlib import Path
import json


#local utils
from websites.C import C
from websites.WindowsCentral import WindowsCentral
from websites.AlineaAnalytics import AlineaAnalytics
from websites.Mp1st import Mp1st
from websites.VGC import VGC
from websites.GameStop import GameStop

#type hints
from abc import ABC
from typing import ClassVar, Protocol



class WebSiteAbc(ABC):#abc for websiteOperate class
    
    #show_articles()
    article_url_path: ClassVar[Path]
    show_amount: ClassVar[int]



class ClassProtocol(Protocol):#solve cross-parent class dependency problem

    #show_articles()
    get_article_url: ClassVar
    article_url_path: ClassVar
    show_amount: ClassVar

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
            print(C.RED(f'[!{cls}]Raise error while reading article url: {e}'))
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
            target_url = Basic.current_article_list[idx - 1]
        except IndexError:
            print(C.RED('[!]Index not found.'))
            return False
        
        #process and write article to local
        cls.cls_output_article(target_url)



class WinCentOp(WebSiteAbc, WindowsCentral, Basic):
    show_amount = 10

class AAOp(WebSiteAbc, AlineaAnalytics, Basic):
    show_amount = 5

class Mp1Op(WebSiteAbc, Mp1st, Basic):
    show_amount = 10

class VGCOp(WebSiteAbc, VGC, Basic):
    show_amount = 7

class GSOp(WebSiteAbc, GameStop, Basic):
    show_amount = 10
    



class CommandLineInterface(Basic):
    pass

if __name__ == '__main__':
    pass



