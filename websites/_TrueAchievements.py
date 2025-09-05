from bs4.element import NavigableString
import requests
from bs4 import BeautifulSoup
from pathlib import Path
import re
import json
from datetime import datetime, timedelta


if __name__ != '__main__':
    from websites.C import C
else:
    from C import C


class _TrueAchievements:
    
    body_html_path = Path(__file__).parent.parent / 'database/TrueAchievements/body.html'
    article_url_path = body_html_path.parent / 'article_url.jsonl'
    output_path = Path().home() / 'storage/shared/ArticleOutput/TrueAchievements'
    
    body_html_path.parent.mkdir(parents = True, exist_ok = True)
    output_path.mkdir(parents = True, exist_ok = True)
    
    url = 'https://www.trueachievements.com/news'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}


    @classmethod
    def get_write_body(cls):
        
        print(C.YELLOW('[TA]Getting body html...'), end='', flush=True)
        
        response = requests.get(_TrueAchievements.url, headers=_TrueAchievements.headers)
        soup = BeautifulSoup(response.text, 'html.parser').body
        body = soup.select_one('body > form main div.news-section.list')#type: ignore
        if not body:
            print(C.RED('[!]') + 'Aborted')
            return False
        
        _TrueAchievements.body_html_path.write_text(body.prettify())#type: ignore
        
        print(C.YELLOW(' Complete.'))


    @classmethod
    def get_article_url(cls):
        print(C.YELLOW('[TA]Writing article url...'), end='', flush=True)
        body_html = _TrueAchievements.body_html_path.read_text(encoding='utf-8')
        body = BeautifulSoup(body_html, 'html.parser').div
        
        #get article urls
        gener_filt = {'List', 'Community news', 'Quick Games', 'Site news', 'Targets'}
        head = 'https://www.trueachievements.com'
        result_list = []
        
        for section in body.select('div > section'):#type: ignore
            gener = section.select_one('section > div.image > a').get_text(strip=True)#type: ignore
            if gener in gener_filt: continue
            
            a = section.select_one('section > article a')
            url = head + a['href']#type: ignore
            title = a.get_text(strip=True)#type: ignore
            
            date = section.select_one('section > article p.author span').get_text(strip=True)#type: ignore
            try:
                number, token = re.match(r'Posted (\d+) (hours*|days*).*', date).groups()#type: ignore
                if token.startswith('day'): delta = timedelta(days=int(number))
                elif token.startswith('hour'): delta = timedelta(hours=int(number))
            except AttributeError: delta = timedelta(days=0)
            pub_date = (datetime.today() - delta).strftime('%m.%d')#type: ignore
            
            result_list.append({f'[{pub_date}]{gener}: {title}': url})
            if len(result_list) >= 20: break
        
        #write into local 
        f = open(str(_TrueAchievements.article_url_path), 'w', encoding='utf-8')
        for title_url_dict in result_list:
            json.dump(title_url_dict, f)
            f.write('\n')
        f.close()
        print(C.YELLOW(' Complete.'))


    @classmethod
    def cls_output_article(cls, title_url_dict: dict[str, str]):
        print(C.YELLOW('[TA]Getting reaponse and writing article...'), end='', flush=True)
        
        #get info
        url = next(iter(title_url_dict.values()))
        origin_title = next(iter(title_url_dict))
        title = re.sub(r'(\[.+?\])(.+)', r'\2', origin_title)
        title_prefix = title[:35]
        pub_date = re.sub(r'(\[)(.+?)(\].+)', r'\2', origin_title)
        
        response = requests.get(url, headers=_TrueAchievements.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        #iterate over a copy list
        tag_contains_article = soup.select_one('body > form article > section')
        children = []
        for child in tag_contains_article.contents:#type: ignore
            if child.name == 'div' and 'quote' in child.get('class'):#type: ignore
                for _child in child.contents:#type: ignore
                    children.append(_child)
                continue
            children.append(child)
        
        #get article
        article = title + '\n\n'
        for child in children:
            if isinstance(child, NavigableString):
                article += child.strip()
                continue
            
            if child.name == 'br':
                article += '\n'
            
            elif child.name == 'ul':
                article += '\n'
                for li in child.select('ul li'):
                    article += f'  -{li.get_text(separator=' ', strip=True)}\n'
            
            elif child.name == 'div' :
                if not 'tab-w' in child.get('class'): continue
                
                article += '\n'
                for tr in child.select('table tr'):
                    row_list = []
                    for td in tr.find_all(['td', 'th']):
                        row_list.append(td.get_text(separator=' ', strip=True))
                    article += ' | '.join(row_list) + '\n'
            
            else:
                article += child.get_text(separator=' ', strip=True)
        article += '\n——Published by TrueAchievements'
        
        #write in article
        output_path = _TrueAchievements.output_path / pub_date / f'{title_prefix}….txt'
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(article, encoding='utf-8')
            print(C.YELLOW('Complete, getting images...'))
        except Exception as e:
            print(C.RED('\n[!TA]' + f'Raise error while writing article: {e}'))
            return False
        
        #get image urls
        img_path = output_path.parent / f'{title_prefix}'
        img_path.mkdir(exist_ok=True)
        img_url_list = []
        
        try:#thumb nail
            thumbnail_url = soup.head.select_one('meta[property="og:image"]')['content']#type: ignore
            img_url_list.append(thumbnail_url)
        except Exception as e:
            print(C.RED('[!TA]') + f'Thumb nail error: {e}')
        
        #article images
        head = 'https://www.trueachievements.com'
        for div in tag_contains_article.select('section > div.iih'):#type: ignore
            try:
                img_url = head + div.select_one('div img')['src']#type: ignore
                img_url_list.append(img_url)
            except Exception as e:
                print(C.RED('[!TA]') + f'Image error: {e}')
        
        #download images
        for i, img_url in enumerate(img_url_list):
            try:
                image_response = requests.get(img_url, headers=_TrueAchievements.headers, stream=True)#type: ignore
                with open(str(img_path / f'[{i+1}]-{title_prefix}….png'), 'wb') as f:
                    for chunk in image_response.iter_content(2200): f.write(chunk)
                print(C.YELLOW(f'[TA]Picture {i+1} writen.'))
                
            except Exception as e:
                print(C.RED(f'[!TA]') + f'Failur to download {i+1}image: {e}')
                continue
        
        return article




if __name__ == '__main__':
    d = {"[09.04]Series X: Space Marine 2's free Anniversary Update kickstarts Year 2 roadmap": "https://www.trueachievements.com/news/warhammer-40000-space-marine-2-year-2-roadmap"}
    _TrueAchievements.cls_output_article(d)
    pass
