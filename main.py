from pathlib import Path
import json
import requests
import re

#translate()
from hashlib import md5
import random

#exceptions
import traceback
import sys

#local utils
from websites.C import C
from deepseek_api import DeepSeek

from websites._WindowsCentral import _WindowsCentral
from websites._AlineaAnalytics import _AlineaAnalytics
from websites._Mp1st import _Mp1st
from websites._VGC import _VGC
from websites._GameSpot import _GameSpot
from websites._TheVerge import _TheVerge
from websites._InsiderGaming import _InsiderGaming
from websites._GamesRadar import _GamesRadar
from websites._GameDeveloper import _GameDeveloper
from websites._PureXbox import _PureXbox
from websites._GameRant import _GameRant
from websites._EuroGamer import _EuroGamer

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




class Basic(ClassProtocol):
    
    current_article_list = []

    cache_path = Path(__file__).parent / 'database/DeepSeek_prompts/cache.json'
    if not cache_path.exists():
        with open(str(cache_path), 'w', encoding='utf-8') as f:
            json.dump([], f)
    
    with open(str(cache_path), 'r', encoding='utf-8') as f:
        cache = set(json.load(f))

    @staticmethod
    def write_cache():
        with open(str(Basic.cache_path), 'w', encoding='utf-8') as f:
            json.dump(list(Basic.cache)[:30], f)




    @classmethod
    def show_articles(cls, update=False, read=True, append=False, show_all=False, show=True):
        """    Require class attribute
        cls.article_url_path: Path | Point to project database direction.
        cls.show_amount: int | Decide show amount of artiles
    Result
        Pass particular website's article_url to 'current_article_list', for future selection operates."""
        
        if update:
            cls.get_write_body()
            cls.get_article_url()
            print('\n')
        
        if read:
            try:
                with open(str(cls.article_url_path), 'r', encoding='utf-8') as f:
                    title_url_list: list = []
                    for line in f:
                        _dict = json.loads(line.strip())
                        _dict['class'] = cls
                        title_url_list.append(_dict)
            except Exception as e:
                print(C.RED(f'[!{cls.alias}]Raise error while reading article url: {e}'))
                return
        
            #cut and write title_hrep_list to Basic attribute
            if not show_all:
                title_url_list = title_url_list[:cls.show_amount]
            if append:
                Basic.current_article_list += title_url_list
            else:
                Basic.current_article_list = title_url_list
        
        #print titles
        if show == True:
            current_name = ''
            for i, title_url_dict in enumerate(Basic.current_article_list):
                if title_url_dict['class'].__name__ != current_name:
                    current_name = title_url_dict['class'].__name__
                    print(C.YELLOW('\n[Publisher] ') + current_name)
                
                _url = next(iter(title_url_dict.values()))
                if _url in cls.cache: head = C.BLUE(f'[{i + 1}]')
                else: head = C.GREEN(f'[{i + 1}]')
                
                print(head + next(iter(title_url_dict)))
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
        return target_url['class'].cls_output_article(target_url)



    @classmethod
    def translate(cls, idx: int):
        
        trans_api = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
        appid = '20250822002436409'
        try:
            q = next(iter(Basic.current_article_list[idx-1]))
        except IndexError:
            print(C.RED('[!]') + 'Index not found.')
            return False
        salt = random.randint(32768, 65536)
        key = '<your key here>'
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



class WindowsCentral(WebSiteAbc, _WindowsCentral, Basic):
    alias = 'Win'
    show_amount = 10

class AlineaAnalytics(WebSiteAbc, _AlineaAnalytics, Basic):
    alias = 'AA'
    show_amount = 5

class Mp1st(WebSiteAbc, _Mp1st, Basic):
    alias = 'Mp1'
    show_amount = 10

class VGC(WebSiteAbc, _VGC, Basic):
    alias = 'VGC'
    show_amount = 7

class GameSpot(WebSiteAbc, _GameSpot, Basic):
    alias = 'GS'
    show_amount = 10

class TheVerge(WebSiteAbc, _TheVerge, Basic):
    alias = 'Veg'
    show_amount = 7

class InsiderGaming(WebSiteAbc, _InsiderGaming, Basic):
    alias = 'InG'
    show_amount = 12

class GamesRadar(WebSiteAbc, _GamesRadar, Basic):
    alias = 'GR'
    show_amount = 12

class GameDeveloper(WebSiteAbc, _GameDeveloper, Basic):
    alias = 'Dev'
    show_amount = 7

class PureXbox(WebSiteAbc, _PureXbox, Basic):
    alias = 'PX'
    show_amount = 12

class GameRant(WebSiteAbc, _GameRant, Basic):
    alias = 'Ran'
    show_amount = 12

class EuroGamer(WebSiteAbc, _EuroGamer, Basic):
    alias = 'Ero'
    show_amount = 12



class CommandLineInterface(Basic):

    def __init__(self):
        self.operates = {
                'help': CommandLineInterface.help,
                'ls': CommandLineInterface.ls,
                'show': CommandLineInterface.show,
                'up': CommandLineInterface.up,
                'trans': CommandLineInterface.trans,
                'gene': CommandLineInterface.gene,
                'out': CommandLineInterface.out
                }
        self.group = {
                'h': [GameSpot, InsiderGaming, GamesRadar, PureXbox, GameRant],
                'm': [VGC, TheVerge, GameDeveloper, WindowsCentral, Mp1st, EuroGamer],
                'l': [AlineaAnalytics]
                }
        self.websites_list = self.group['h'] + self.group['m'] + self.group['l']
        self.prompts = {'pro': 'pro', 'rel': 'relaxe_pro', 'sho': 'short'}



    def handle_input(self, user_input: str):
        command = user_input.split(' ')[0]
        params = user_input.split(' ')[1:]
        if command not in self.operates:
            print(C.RED('[!]') + 'Command not found.')
            return False
        
        return self.operates[command](self, params)



    #COMMANDS
    def help(self):
        return


    def ls(self, params:list):
        #optional 1 param
        try: group = params[0]
        except IndexError: group = None
        
        with open(str(Basic.cache_path), 'w', encoding='utf-8') as f:
            json.dump(list(self.__class__.cache)[:20], f)
        
        #-group
        if group:
            try: websites = self.group[group]
            except KeyError:
                print(C.RED('[!]') + 'Please insert one of h/m/l.\n')
                return False
        else:
            websites = self.websites_list
        
        for website in websites:
            i = self.websites_list.index(website)
            print(C.GREEN(f'[{i+1}][{website.alias}]{' '*(4-len(website.alias))}') + website.__name__)
        print('\n')


    def show(self, params:list):
        #only 1 param
        if not params:
            print(C.RED('[!]') + ('Please insert one of index/group/a(all)\n'))
            return False
        flag = params[0]
        
        #-index
        if re.fullmatch(r'\d+', flag):
            if not 0 < int(flag) <= len(self.websites_list):
                return print(C.RED('[!]') + 'Index out of range.\n')
            return self.websites_list[int(flag) - 1].show_articles()
        
        #-group
        elif flag in self.group:
            Basic.write_cache()
            
            Basic.current_article_list = []
            for website in self.group[flag]:
                website.show_articles(show=False, append=True)
            return Basic.show_articles(read=False)
        
        #-a
        elif flag == 'a':
            Basic.write_cache()
            
            Basic.current_article_list = []
            for website in self.websites_list:
                website.show_articles(show=False, append=True)
            return Basic.show_articles(read=False)
        
        else:
            print(C.RED('[!]') + ('Please insert one of: index/group/a(all)\n'))
            return False


    def up(self, params:list):
        
        #optional 1 param, update then call self.show👆
        if not params:#-a
            Basic.write_cache()
            for website in self.websites_list:
                website.show_articles(update=True, read=False, show=False)
            return self.show(['a'])
        
        else:
            flag = params[0]
            
            #-index
            if re.fullmatch(r'\d+', flag):
                self.websites_list[int(flag) - 1].show_articles(update=True, read=False, show=False)
                return self.show([flag])
            
            #-group
            elif flag in self.group:
                Basic.write_cache()
                for website in self.group[flag]:
                    website.show_articles(update=True, read=False, show=False)
                return self.show([flag])
            
            #invalid
            else:
                print(C.RED('[!]') + 'Please insert one of: index/group/None(all)')
                return False



    def trans(self, params:list):
        #1 index param
        if not params:
            print(C.RED('[!]') + 'Please insert index.')
            return False
        
        flag = params[0]
        #-index
        if re.fullmatch(r'\d+', flag):
            return Basic.translate(int(flag))
        
        #invalid
        else:
            print(C.RED('[!]') + 'Please insert correct index.')
            return False


    def gene(self, params:list):
        #1 index param
        if not params:
            print(C.RED('[!]') + 'Please insert index.')
            return False
        
        try:
            prompt = self.prompts[params[0]]#-prompt
            flag = params[1]
        except (KeyError, IndexError):
            print(C.RED('[!]') + 'Correct format: gene+prompt(pro/rel/sho)+index')
            return False
        
        #-index
        if re.fullmatch(r'\d+', flag):
            cache_url = next(iter(Basic.current_article_list[int(flag) - 1].values()))
            Basic.cache.add(cache_url)
            Basic.write_cache()
            
            article: str = Basic.output_article(int(flag))#type: ignore
            return DeepSeek.output(prompt, article)
        
        #invalid
        else:
            print(C.RED('[!]') + 'Correct format: gene+prompt(pro/rel/sho)+index')
            return False



    def out(self, params:list):
        return



    def run(self):
        while True:
            try: 
                user_input = input(C.GREEN('❯ '))
            except EOFError:
                Basic.write_cache()
                print('Program ends.\n')
                break
            user_input = re.sub('  * ', ' ', user_input).strip()
            
            if not user_input.strip():
                continue
            
            if user_input == 'q':
                Basic.write_cache()
                print('Program ends.\n')
                break
            
            try:
                self.handle_input(user_input)
            
            except InterruptedError:
                print(C.RED('[!]') + 'Interruped.')
                continue
            except requests.exceptions.ConnectionError as e:
                print(C.RED('[!]') + f'Connection error: {e}\n')
                continue
            except Exception:
                exc_type, exc_value, exc_tb = sys.exc_info()
                
                last_tb = exc_tb
                while last_tb.tb_next: last_tb = last_tb.tb_next#type: ignore
                frame = last_tb.tb_frame#type: ignore
                
                file_name = frame.f_code.co_filename
                line_number = last_tb.tb_lineno#type: ignore
                function_name = frame.f_code.co_name
                
                print(C.RED('[!]') + 'Raise unexcepted error!')
                print(f'Error type: {exc_type.__name__}({exc_value})')#type: ignore
                print(f"Error path: '{file_name}', line number: {line_number}")
                print(f'Function name: {function_name}')
                
                _input = input('Insert n/any to continue/quit ' + C.RED('❯'))
                if _input.strip() == 'n': continue
                break


if __name__ == '__main__':
    CLI = CommandLineInterface()
    CLI.run()
    pass
