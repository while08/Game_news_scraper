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

class _Mp1st:

    body_html_path = Path(__file__).parent.parent / 'database/Mp1st/body.html'
    article_url_path = body_html_path.parent / 'article_url.jsonl'
    output_path = Path().home() / 'storage/shared/ArticleOutput/Mp1st'
    
    body_html_path.parent.mkdir(parents = True, exist_ok = True)
    output_path.mkdir(parents = True, exist_ok = True)
    
    api_url = 'https://mp1st.com/wp-admin/admin-ajax.php'
    headers = {
        "accept": "*/*",
        "accept-language": "zh-CN,zh;q=0.9,en-CN;q=0.8,en;q=0.7",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "sec-ch-ua": "\"Chromium\";v=\"139\", \"Not;A=Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": "\"Android\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-requested-with": "XMLHttpRequest",
        "referer": "https://mp1st.com/news"}
    data = {"action": "category_ajax","page_id": "1","category_name": "news"}


    @classmethod
    def get_write_body(cls):
        
        print(C.YELLOW('[Mp1]Getting body html...'), end='', flush=True)
        
        response = requests.post(_Mp1st.api_url, headers=_Mp1st.headers, data=_Mp1st.data)
        soup = BeautifulSoup(response.text, 'html.parser')#type: ignore
        
        _Mp1st.body_html_path.write_text(soup.prettify(), encoding = 'utf-8')#type: ignore
        print(C.YELLOW(' Complete.'))


    @classmethod
    def get_article_url(cls):
        #get target <h3> tags that contains article url
        body_html = _Mp1st.body_html_path.read_text(encoding = 'utf-8')
        body = BeautifulSoup(body_html, 'html.parser')
        tags_contain_url = body.find_all(lambda tag: tag.name == 'article' and tag.find('h3'))#type: ignore
        
        f = open(str(_Mp1st.article_url_path), 'w', encoding='utf-8')
        
        #write into local 
        print(C.YELLOW('[Mp1]Writing article url...'), end='', flush=True)
        for tag in tags_contain_url:
            h3_tag = tag.find('h3')#type: ignore
            try:
                title = h3_tag.get_text(strip=True)#type: ignore
                url = h3_tag.a['href']#type: ignore
                date = tag.select_one('article div.codevidia-meta-date').get_text(strip=True)#type: ignore
                number, token = re.match(r'(\d+) (hours*|days*).*', date).groups()#type: ignore
                if token.startswith('hour'): delta = timedelta(hours=int(number))
                elif token.startswith('day'): delta = timedelta(days=int(number))
                else: delta = timedelta(hours=0)
                pub_date = (datetime.today() - delta).strftime('%m.%d')
                
                json.dump({f'[{pub_date}] {title}': url}, f)
                f.write('\n')
            except Exception as e:
                print(C.RED(f'\n[!Mp1]') + f'Raise error: {e}')
                continue
        f.close()
        print(C.YELLOW(' Complete.'))


    @classmethod
    def cls_output_article(cls, title_url_dict: dict[str, str]):
        print(C.YELLOW('[Mp1]Getting reaponse and writing article...'), end='', flush=True)
        
        #get info
        url = next(iter(title_url_dict.values()))
        origin_title = next(iter(title_url_dict))
        title = re.sub(r'(\[.+?\] )(.+)', r'\2', origin_title)
        pub_date = re.sub(r'(\[)(.+?)(\].+)', r'\2', origin_title)
        title_prefix = title[:35]
        
        response = requests.get(url, headers=_Mp1st.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        article_tag = soup.find('article')
        for useless_tag in article_tag.find_all(class_='related-post'):#type: ignore
            useless_tag.extract()
        
        #process and get article, write to local
        single_content_tag = article_tag.find('div', class_=re.compile(r'.*?single-content'))#type: ignore
        result_article = title + '\n' + single_content_tag.get_text(separator='\n', strip=True)#type: ignore
        result_article = result_article + '\n\n---Published by Mp1st'
        
        output_path = _Mp1st.output_path / pub_date / f'{title_prefix}.txt'
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(result_article, encoding='utf-8')
            print(C.YELLOW('Complete, getting images...'))
        except Exception as e:
            print(C.RED(f'\n[!Mp1]') + f'Raise error while writing article: {e}')
            return False
        
        #download images to local
        img_path = output_path.parent / f'{title_prefix}'
        img_path.mkdir(exist_ok=True)
        img_url_list = []
        
        try:
            thumbnail_tag = article_tag.find('div', class_='post-thumbnail')#type: ignore
            img_url_list.append(thumbnail_tag.img['src'])#type: ignore
        except Exception as e:
            print(C.RED('[!]') + f'Thumb nail error: {e}')
        
        for img_tag in single_content_tag.find_all('img'):#type: ignore
            img_url_list.append(img_tag['src'])#type: ignore
        
        headers = _Mp1st.headers
        for i, img_url in enumerate(img_url_list):
            try:
                image_response =requests.get(img_url, headers=headers, stream=True)#type: ignore
                with open(str(img_path / f'[{i+1}]-{title_prefix}….png'), 'wb') as f:
                    for chunk in image_response.iter_content(2200): f.write(chunk)
                print(C.YELLOW(f'[Mp1]Picture {i+1} writen.'))
                
            except Exception as e:
                print(C.RED(f'[!Mp1]') + f'Failur to download {i+1}image: {e}')
                continue
        
        return result_article


if __name__ == '__main__':
    title_url_dict = {"[08.11] Battlefield 2042 Gets New Update Version 1.74/1.000.077 That Adds New Content, Just in Time as BF6 Beta Ends": "https://mp1st.com/news/battlefield-2042-new-update-1-74-1-000-077-new-content"}

    _Mp1st.cls_output_article(title_url_dict)
