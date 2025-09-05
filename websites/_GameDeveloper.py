import requests
from bs4 import BeautifulSoup
from pathlib import Path
import re
import json


if __name__ != '__main__':
    from websites.C import C
else:
    from C import C


class _GameDeveloper:
    
    body_html_path = Path(__file__).parent.parent / 'database/GameDeveloper/body.json'
    article_url_path = body_html_path.parent / 'article_url.jsonl'
    output_path = Path().home() / 'storage/shared/ArticleOutput/GameDeveloper'
    
    body_html_path.parent.mkdir(parents = True, exist_ok = True)
    output_path.mkdir(parents = True, exist_ok = True)
    
    url = "https://www.gamedeveloper.com/api/dynamic-module"
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en-CN;q=0.8,en;q=0.7",
        "Referer": "https://www.gamedeveloper.com/",
        "Sec-Ch-Ua": '"Chromium";v="139", "Not;A=Brand";v="99"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Linux"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors", 
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
    }
    params = {
        "contentTypeUid": "module_latest_content",
        "uid": "blt786db145f8677f63",
        "location": "homepage"
    }


    @classmethod
    def get_write_body(cls):
        
        print(C.YELLOW('[Dev]Getting body html...'), end='', flush=True)
        
        try:#get response
            response = requests.get(_GameDeveloper.url, params=_GameDeveloper.params, headers=_GameDeveloper.headers)
            response.raise_for_status()
        except Exception as e:
            print(C.RED(f'\n[!Dev]') + f'Raise error while getting response: {e}')
            return False
        
        try:#get data
            list_contians_url: list = json.loads(response.text)['module']['data']['leftColumnData']['contents']
        except KeyError:
            print(C.RED('\n[!Dev]') + 'Invaild response format: {e}')
            return False
        
        #write data
        with open(str(_GameDeveloper.body_html_path), 'w', encoding='utf-8') as f:
            json.dump(list_contians_url, f, indent=True)
        print(C.YELLOW(' Complete.'))


    @classmethod
    def get_article_url(cls):
        with open(str(_GameDeveloper.body_html_path), 'r', encoding='utf-8') as f:
            list_contians_url = json.load(f)
        months = {
            'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
            'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
            'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12}
        
        result_list = []
        for ele in list_contians_url:
            if ele['type'] == 'ad': continue
            
            data_dict = ele['data']
            title = data_dict['articleName'].strip()
            url = 'https://www.gamedeveloper.com' + data_dict['articleUrl']
            pub_date = data_dict['date'].strip()
            month, day = re.match(r'([A-Za-z]+) (\d+),.*', pub_date).groups()#type: ignore
            pub_date = f'{months[month]}.{day if len(day) == 2 else '0' + day}'
            
            result_list.append({f'[{pub_date}] {title}': url})
            
            if len(result_list) >= 10: break
        
        
        #write in
        print(C.YELLOW('[Dev]Writing article url...'), end='', flush=True)
        f = open(str(_GameDeveloper.article_url_path), 'w', encoding='utf-8')
        for title_url_dict in result_list:
            json.dump(title_url_dict, f)
            f.write('\n')
        f.close()
        print(C.YELLOW(' Complete.'))


    @classmethod
    def cls_output_article(cls, title_url_dict: dict[str, str]):
        print(C.YELLOW('[Dev]Getting reaponse and writing article...'), end='', flush=True)
        
        #get info
        url = next(iter(title_url_dict.values()))
        origin_title = next(iter(title_url_dict))
        title = re.sub(r'(\[.+?\] )(.+)', r'\2', origin_title)
        pub_date = re.sub(r'(\[)(.+?)(\].+)', r'\2', origin_title)
        title_prefix = title[:35]
        
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        #get tags contain article
        article = title +'\n'
        
        tag_contains_article = soup.body.main.find('div', class_='ContentModule-Wrapper')#type: ignore
        para_tags = tag_contains_article.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'], recursive=False)#type: ignore
        
        #delete useless tags
        for tag in para_tags:
            try:
                if 'RelatedArticle' in tag.get('class', []): tag.extract()#type: ignore
            except Exception: pass
        para_tags = tag_contains_article.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p'], recursive=False)#type: ignore
        
        #get article
        for tag in para_tags:
            article += (tag.get_text(separator=' ', strip=True) + '\n')
        article += '\n——Published by GameDeveloper'
        
        #write in article
        output_path = _GameDeveloper.output_path / pub_date / f'{title_prefix}….txt'
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(article, encoding='utf-8')
            print(C.YELLOW('Complete, getting images...'))
        except Exception as e:
            print(C.RED(f'\n[!Dev]Raise error while writing article: {e}'))
            return False
        
        #get image urls
        img_path = output_path.parent / f'{title_prefix}'
        img_path.mkdir(exist_ok=True)
        img_url_list = []
        
        try:
            thumbnail_url = soup.head.find('meta', {'property': 'og:image'})['content']#type: ignore
            img_url_list.append(thumbnail_url)
        except Exception as e: print(C.RED('[!Dev]') + f'Thumb nail error: {e}')
        
        #download images
        for i, img_url in enumerate(img_url_list):
            try:
                image_response = requests.get(img_url, headers=_GameDeveloper.headers, stream=True)#type: ignore
                with open(str(img_path / f'[{i+1}]-{title_prefix}….png'), 'wb') as f:
                    for chunk in image_response.iter_content(2200): f.write(chunk)
                print(C.YELLOW(f'[Dev]Picture {i+1} writen.'))
                
            except Exception as e:
                print(C.RED(f'[!Dev]Failur to download {i+1}image: {e}'))
                continue
        
        return article



if __name__ == '__main__':
    d = {"8 games have pushed publishing dates in response to Silksong": "https://www.gamedeveloper.com/business/7-games-have-pushed-publishing-dates-in-response-to-silksong"}
    _GameDeveloper.cls_output_article(d)
    pass
