import requests
from bs4 import BeautifulSoup
from pathlib import Path
import re
import json

import html


if __name__ != '__main__':
    from websites.C import C
else:
    from C import C

class _EuroGamer:
    
    body_html_path = Path(__file__).parent.parent / 'database/EuroGamer/body.html'
    article_url_path = body_html_path.parent / 'article_url.jsonl'
    output_path = Path().home() / 'storage/shared/ArticleOutput/EuroGamer'
    
    body_html_path.parent.mkdir(parents = True, exist_ok = True)
    output_path.mkdir(parents = True, exist_ok = True)
    
    url = 'https://www.eurogamer.net/xbox'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}



    @classmethod
    def get_write_body(cls):
        print(C.YELLOW('[Ero]Getting body html...'), end='', flush=True)
        
        response = requests.get(_EuroGamer.url, headers=_EuroGamer.headers)
        soup = BeautifulSoup(response.text, 'html.parser').body
        body = soup.select_one('body main div.archive__items')#type: ignore
        
        _EuroGamer.body_html_path.write_text(body.prettify())#type: ignore
        
        print(C.YELLOW(' Complete.'))


    @classmethod
    def get_article_url(cls):
        
        body_html =_EuroGamer.body_html_path.read_text(encoding='utf-8')
        body = BeautifulSoup(body_html, 'html.parser').div
        
        #get article url
        result_list = []
        for article_tag in body.select('div > article'):#type: ignore
            try:
                if article_tag.select_one('article div.archive__type').get_text(strip=True) != 'News':#type: ignore
                    continue
                a_tag = article_tag.select_one('article h2 a')
                
                title = a_tag.get_text(strip=True)#type: ignore
                url = a_tag['href']#type: ignore
                pub_date = article_tag.select_one('article time')['datetime']#type: ignore
                pub_date = re.sub(r'(\d{4}-)(\d\d)(-)(\d\d)(.*)', r'\2.\4', pub_date)#type: ignore
                
                result_list.append({f'[{pub_date}] {title}': url})
                if len(result_list) >= 20: break
            except Exception: continue
        
        #write in
        print(C.YELLOW('[Ero]Writing article url...'), end='', flush=True)
        f = open(str(_EuroGamer.article_url_path), 'w', encoding='utf-8')
        for title_url_dict in result_list:
            json.dump(title_url_dict, f)
            f.write('\n')
        f.close()
        print(C.YELLOW(' Complete.'))


    @classmethod
    def cls_output_article(cls, title_url_dict: dict[str, str]):
        print(C.YELLOW('[Ero]Getting reaponse and writing article...'), end='', flush=True)
        
        #get info
        url = next(iter(title_url_dict.values()))
        origin_title = next(iter(title_url_dict))
        title = re.sub(r'(\[.+?\] )(.+)', r'\2', origin_title)
        pub_date = re.sub(r'(\[)(.+?)(\].+)', r'\2', origin_title)
        title_prefix = title[:35]
        
        try:#get article response
            json_response = requests.get((url + '?ajax=1'), headers=_EuroGamer.headers)
            json_response.raise_for_status()
            
            data: dict = json.loads(json_response.text)
            body_html = data['html']
            soup = BeautifulSoup(body_html, 'html.parser')
        
        except (json.JSONDecodeError, requests.exceptions.HTTPError) as e:
            print(C.RED('\n[!]') + f'Raise error while getting article response: {e}')
            return None
        
        target_div = soup.select_one('div > article div.article_body_content.article-styling')
        search_tags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul']
        tags_contain_article = target_div.find_all(search_tags, recursive=False)#type: ignore
        
        article = title + '\n'
        for tag in tags_contain_article:
            if tag.name == 'ul':#type: ignore
                for li in tag.select('ul > li'):#type: ignore
                    article += f'-{li.get_text(separator=" ", strip=True)}\n'
                continue
            
            article += tag.get_text(separator=' ', strip=True) + '\n'
        article += '\n——Published by EuroGamer'
        
        #write in article
        output_path =_EuroGamer.output_path / pub_date / f'{title_prefix}….txt'
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(article, encoding='utf-8')
            print(C.YELLOW('Complete, getting images...'))
        except Exception as e:
            print(C.RED(f'\n[!Ero]Raise error while writing article: {e}'))
            return False
        
        #get img urls
        img_path = output_path.parent / f'{title_prefix}'
        img_path.mkdir(exist_ok=True)
        img_url_list = []
        
        _response = requests.get(url, headers=_EuroGamer.headers)
        soup = BeautifulSoup(_response.text, 'html.parser')
    
        try:#thumb nail
            thumbnail_url = soup.head.select_one('meta[property="og:image"]')['content']#type: ignore
            img_url_list.append(thumbnail_url)
        except Exception as e:
            print(C.RED('[!Ran]') + f'Thumb nail error: {e}')
        
        #download images
        for i, img_url in enumerate(img_url_list):
            try:
                image_response = requests.get(img_url, headers=_EuroGamer.headers, stream=True)#type: ignore
                with open(str(img_path / f'[{i+1}]-{title_prefix}….png'), 'wb') as f:
                    for chunk in image_response.iter_content(2200): f.write(chunk)
                print(C.YELLOW(f'[Ero]Picture {i+1} writen.'))
                
            except Exception as e:
                print(C.RED(f'[!Ero]') + f'Failur to download {i+1}image: {e}')
                continue
        
        return article



if __name__ == '__main__':
    d = {"[08.29]Hollow Knight: Silksong's release date causes delays for more games than you might think": "https://www.eurogamer.net/hollow-knight-silksongs-release-date-causes-delays-for-more-games-than-you-might-think"}
    _EuroGamer.cls_output_article(d)
    pass
