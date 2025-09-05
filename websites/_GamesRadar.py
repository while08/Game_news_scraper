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


class _GamesRadar:
    
    body_html_path = Path(__file__).parent.parent / 'database/GamesRadar/body.html'
    article_url_path = body_html_path.parent / 'article_url.jsonl'
    output_path = Path().home() / 'storage/shared/ArticleOutput/GamesRadar'
    
    body_html_path.parent.mkdir(parents = True, exist_ok = True)
    output_path.mkdir(parents = True, exist_ok = True)
    
    url = 'https://www.gamesradar.com/platforms/xbox/xbox-series-x/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}


    @classmethod
    def get_write_body(cls):
        print(C.YELLOW('[GR]Getting body html...'), end='', flush=True)
        
        response = requests.get(_GamesRadar.url, headers=_GamesRadar.headers)
        soup = BeautifulSoup(response.text, 'lxml').article
        body = soup.find('div', class_='listingResults')#type: ignore
        _GamesRadar.body_html_path.write_text(body.prettify())#type: ignore
        
        print(C.YELLOW(' Complete.'))


    @classmethod
    def get_article_url(cls):
        
        body_html = _GamesRadar.body_html_path.read_text(encoding='utf-8')
        soup = BeautifulSoup(body_html, 'lxml').div
        
        print(C.YELLOW('[GR]Writing article url...'), end='', flush=True)
        
        f = open(str(_GamesRadar.article_url_path), 'w', encoding='utf-8')
        divs_contain_url = soup.find_all(lambda tag:tag.name == 'div' and tag.a, recursive=False)#type: ignore
        for tag in divs_contain_url:
            url = tag.a['href']#type: ignore
            title = html.unescape(tag.a['aria-label']).strip()#type: ignore
            pub_date = tag.select_one('div time')['datetime'].strip()#type: ignore
            pub_date = re.sub(r'(\d{4}-)(\d\d)(-)(\d\d)(.*)', r'\2.\4', pub_date)#type: ignore
            
            json.dump({f'[{pub_date}] {title}': url}, f)
            f.write('\n')
        f.close()
        print(C.YELLOW(' Complete.'))


    @classmethod
    def cls_output_article(cls, title_url_dict: dict[str, str]):
        print(C.YELLOW('[GR]Getting reaponse and writing article...'), end='', flush=True)
        
        #get info
        url = next(iter(title_url_dict.values()))
        origin_title = next(iter(title_url_dict))
        title = re.sub(r'(\[.+?\] )(.+)', r'\2', origin_title)
        pub_date = re.sub(r'(\[)(.+?)(\].+)', r'\2', origin_title)
        title_prefix = title[:35]
        
        response = requests.get(url, headers=_GamesRadar.headers)
        soup = BeautifulSoup(response.text, 'lxml')
        
        #get article
        target_div = soup.body.find('div', id='article-body')#type: ignore
        tags_contain_article = target_div.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul'], recursive=False)#type: ignore
        
        article = title + '\n'
        for tag in tags_contain_article:
            if tag.name == 'ul':#type: ignore
                for li in tag.find_all(recursive=False):#type: ignore
                    article += f'-{li.text}\n'
                    continue
            article += tag.get_text(separator=' ', strip=True) + '\n'
        article += '\n——Published by GamesRadar'
        
        #write in article
        output_path =_GamesRadar.output_path / pub_date / f'{title_prefix}….txt'
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(article, encoding='utf-8')
            print(C.YELLOW('Complete, getting images...'))
        except Exception as e:
            print(C.RED(f'\n[!GR]') + f'Raise error while writing article: {e}')
            return False
        
        #get image urls
        img_path = output_path.parent / f'{title_prefix}'
        img_path.mkdir(exist_ok=True)
        img_url_list = []
        
        try:
            thumbnail_url = soup.body.find('section', class_='content-wrapper')#type: ignore
            thumbnail_url = thumbnail_url.find('div', recursive=False)#type: ignore
            thumbnail_url = thumbnail_url.img['src']#type: ignore
            img_url_list.append(thumbnail_url)
        except Exception as e: print(C.RED(f'\n[!GR]') + f'Thumb nail error: {e}')
        
        for tag in target_div.find_all('figure', recursive=False):#type: ignore
            try:
                img_url = tag.img['src']#type: ignore
                img_url_list.append(img_url)
            except Exception as e:
                print(C.RED(f'[!GR]') + f'Image error:{e}')
        
        #download images
        for i, img_url in enumerate(img_url_list):
            try:
                image_response = requests.get(img_url, headers=_GamesRadar.headers, stream=True)#type: ignore
                with open(str(img_path / f'[{i+1}]-{title_prefix}….png'), 'wb') as f:
                    for chunk in image_response.iter_content(2200): f.write(chunk)
                print(C.YELLOW(f'[GR]Picture {i+1} writen.'))
                
            except Exception as e:
                print(C.RED(f'[!GR]') + f'Failur to download {i+1}image: {e}')
                continue
        
        return article


if __name__ == '__main__':
    d = {"[9.02] Gears of War: Reloaded release time \u2013 here's when you can dive into the remastered 2006 shooter on PS5, PC, and Xbox Series X|S": "https://www.gamesradar.com/games/gears-of-war/gears-of-war-reloaded-release-time-heres-when-you-can-dive-into-the-remastered-2006-shooter-on-ps5-pc-and-xbox-series-x-s/"}

    _GamesRadar.cls_output_article(d)
    pass
