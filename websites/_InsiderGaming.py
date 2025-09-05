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

class _InsiderGaming:
    
    body_html_path = Path(__file__).parent.parent / 'database/InsiderGaming/body.html'
    article_url_path = body_html_path.parent / 'article_url.jsonl'
    output_path = Path().home() / 'storage/shared/ArticleOutput/InsiderGaming'
    
    body_html_path.parent.mkdir(parents = True, exist_ok = True)
    output_path.mkdir(parents = True, exist_ok = True)
    
    url = 'https://insider-gaming.com/news-sitemap.xml'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}



    @classmethod
    def get_write_body(cls):
        print(C.YELLOW('[InG]Getting body html...'), end='', flush=True)
        
        headers = _InsiderGaming.headers
        headers['Referer'] = 'https://insider-gaming.com/sitemap_index.xml'
        
        try: response = requests.get(_InsiderGaming.url, headers=headers)
        except Exception as e:
            print(C.RED(f'\n[!InG]Aborted: {e}'))
            return False
        response.encoding = 'utf-8'
        _InsiderGaming.body_html_path.write_text(response.text)
        
        print(C.YELLOW(' Complete.'))


    @classmethod
    def get_article_url(cls):
        
        body_html = _InsiderGaming.body_html_path.read_text(encoding='utf-8')
        body = BeautifulSoup(body_html, 'xml')
        
        #write into local 
        f = open(str(_InsiderGaming.article_url_path), 'w', encoding='utf-8')
        print(C.YELLOW('[InG]Writing article url...'), end='', flush=True)
        
        url_tags = body.find_all('url')
        for tag in url_tags[:25]:
            url = tag.find('loc').text#type: ignore
            title = html.unescape(tag.find('news:title').text)#type: ignore
            pub_date = tag.find('news:publication_date').get_text(strip=True)#type: ignore
            pub_date = re.sub(r'(\d{4}-)(\d\d)(-)(\d\d)(.*)', r'\2.\4', pub_date)#type: ignore
            
            json.dump({f'[{pub_date}] {title}': url}, f)
            f.write('\n')
        f.close()
        print(C.YELLOW(' Complete.'))


    @classmethod
    def cls_output_article(cls, title_url_dict: dict[str, str]):
        print(C.YELLOW('[InG]Getting reaponse and writing article...'), end='', flush=True)
        
        #get info
        url = next(iter(title_url_dict.values()))
        origin_title = next(iter(title_url_dict))
        title = re.sub(r'(\[.+?\] )(.+)', r'\2', origin_title)
        pub_date = re.sub(r'(\[)(.+?)(\].+)', r'\2', origin_title)
        title_prefix = title[:35]
        
        response = requests.get(url, headers=_InsiderGaming.headers)
        article_tag = BeautifulSoup(response.text, 'html.parser').article
        
        #get article
        article = title + '\n'
        div_contains_article = article_tag.find('div', class_='entry-content')#type: ignore
        for useless_tag in div_contains_article.find_all(['div', 'hr', 'style'], recursive=False):#type: ignore
            useless_tag.extract()
        
        for tag in div_contains_article.find_all(recursive=False):#type: ignore
            if tag.name == 'ul':#type: ignore
                for li in tag.find_all('li', recursive=False):#type: ignore
                    article = article + '-' + li.get_text(separator=' ', strip=True) + '\n'
            
            article = article + tag.get_text(separator=' ', strip=True) + '\n'
        article = article + '\n---Published by Insider Gaming'
        
        #write in article
        output_path = _InsiderGaming.output_path / pub_date / f'{title_prefix}….txt'
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(article, encoding='utf-8')
            print(C.YELLOW('Complete, getting images...'))
        except Exception as e:
            print(C.RED(f'\n[!InG]Raise error while writing article: {e}'))
            return False
        
        #get image urls
        img_path = output_path.parent / f'{title_prefix}'
        img_path.mkdir(exist_ok=True)
        img_url_list = []
        
        try:
            thumbnail_url = article_tag.select_one('[class*="post-thumbnail"]')['style']#type: ignore
            thumbnail_url = re.search(r'(https:.*\.(?:png|jpg|webp))', str(thumbnail_url))#type: ignore
            img_url_list.append(thumbnail_url.group(1))#type: ignore
        except Exception as e: print(C.RED(f'[!InG]Thumb nail error: {e}'))
        
        figure_tags = div_contains_article.find_all(lambda tag: tag.name == 'figure' and tag.find('img'), recursive=False)#type: ignore
        for tag in figure_tags:
            try: img_url = tag.img['src']#type: ignore
            except Exception as e:
                print(C.RED(f'[!InG]Figure error: {e}'))
                continue
            img_url_list.append(img_url)
        
        #download images
        for i, img_url in enumerate(img_url_list):
            try:
                image_response = requests.get(img_url, headers=_InsiderGaming.headers, stream=True)#type: ignore
                with open(str(img_path / f'[{i+1}]-{title_prefix}….png'), 'wb') as f:
                    for chunk in image_response.iter_content(2200): f.write(chunk)
                print(C.YELLOW(f'[InG]Picture {i+1} writen.'))
                
            except Exception as e:
                print(C.RED(f'[!InG]Failur to download {i+1}image: {e}'))
                continue
        
        return article


if __name__ == '__main__':
    d1 = {"[9.02] Gamescom 2026 Dates, Location, and Ticket Sales\u2014When is Gamescom 2026 Happening?": "https://insider-gaming.com/gamescom-2026-dates-location-and-ticket-sales-when-is-gamescom/"}
    a = _InsiderGaming.cls_output_article(d1)
    pass
