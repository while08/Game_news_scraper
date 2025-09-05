import requests
from bs4 import BeautifulSoup
from pathlib import Path
import re
import json


if __name__ != '__main__':
    from websites.C import C
else:
    from C import C



class _AlineaAnalytics:
    
    body_html_path = Path(__file__).parent.parent / 'database/AlineaAnalytics/body.html'
    article_url_path = body_html_path.parent / 'article_url.jsonl'
    output_path = Path().home() / 'storage/shared/ArticleOutput/AlineaAnalytics'
    
    body_html_path.parent.mkdir(parents = True, exist_ok = True)
    output_path.mkdir(parents = True, exist_ok = True)
    
    url = 'https://alineaanalytics.com/blog/'
    headers = {'User-Agent': "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36"}
    


    @classmethod
    def get_write_body(cls):
        
        print(C.YELLOW('[AA]Getting body html...'), end='', flush=True)
        
        response = requests.get(_AlineaAnalytics.url, headers=_AlineaAnalytics.headers)
        response.encoding = 'utf-8'
        body = BeautifulSoup(response.text, 'html.parser').body

        _AlineaAnalytics.body_html_path.write_text(body.prettify(), encoding='utf-8')#type: ignore
        print(C.YELLOW(' Complete.'))


    @classmethod
    def get_article_url(cls):
        
        #get target <section> that contains article url
        body_html = _AlineaAnalytics.body_html_path.read_text(encoding='utf-8')
        body = BeautifulSoup(body_html, 'html.parser')
        target_section = body.find('main')
        target_section = target_section.find('section', class_='site-blog', recursive=False)#type: ignore
        
        #generate dict{title: url} then write into jsonl
        divs_contain_url = target_section.find_all('div', class_='site-blog-post-content')#type: ignore
        
        f = open(_AlineaAnalytics.article_url_path, 'w', encoding='utf-8')
        
        print(C.YELLOW('[AA]Writing article url...'), end='',flush=True)
        _s = ' '
        for div in divs_contain_url[:7]:
            try:
                pub_date = div.span.text.strip()#type: ignore
                pub_date = re.sub(r'([a-zA-Z]+)(.*?)(\d+)(.*)', r'\1.\3', pub_date)
                
                url = div.h3.a['href']#type: ignore
                title = f'[{pub_date}]' + div.h3.a.get_text(strip=True)#type: ignore
                title_url_dict = {title: url}
                
                json.dump(title_url_dict, f)
                f.write('\n')
            except Exception as e:
                print(C.RED(f'\n[!AA]Raise error: {e}'))
                _s = '[AA]'
        f.close()
        print(C.YELLOW(f'{_s}Complete.'))


    @classmethod
    def cls_output_article(cls, title_url_dict: dict[str, str]):
        print(C.YELLOW('[AA]Getting reaponse and writing article...'), end='', flush=True)
        
        url = next(iter(title_url_dict.values()))
        original_title = next(iter(title_url_dict.keys()))
        pub_date = re.sub(r'(\[)(.*)(\].*)', r'\2', original_title)
        title = re.sub(r'(\[.*\])(.*)', r'\2', original_title)
        title_prefix = title[:35]
        
        #get publish date and tags that contain article text
        headers = _AlineaAnalytics.headers
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        article_tag = soup.find('article')
        
        #get and write article to local
        tags_contain_article = article_tag.find_all(recursive=False)#type: ignore
        result_article = ''
        for tag in tags_contain_article[:-1]:
            result_article = result_article + tag.text + '\n'
        result_article = re.sub(r'\n\n+\n', r'\n\n', result_article)
        result_article = result_article + '\n---Published by Alinea Analytics'
        
        output_path = _AlineaAnalytics.output_path / pub_date / f'{title_prefix}….txt'
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(result_article, encoding='utf-8')
            print(C.YELLOW('Complete, getting images...'))
        except Exception as e:
            print(C.RED(f'\n[!AA]Raise error while writing article: {e}'))
            return False
        
        
        #get and download images to local
        img_path = output_path.parent / f'{title_prefix}'
        img_path.mkdir(exist_ok=True)
        
        img_tags = article_tag.find_all('img')#type: ignore
        headers['Referer'] = url
        for i, img_tag in enumerate(img_tags):
            try:
                
                img_url = img_tag['src']#type: ignore
                image_response =requests.get(img_url, headers=headers, stream=True)#type: ignore
                with open(str(img_path / f'[{i+1}]-{title_prefix}….png'), 'wb') as f:
                    for chunk in image_response.iter_content(2200): f.write(chunk)
                print(C.YELLOW(f'[AA]Picture {i+1} writen.'))
                
            except Exception as e:
                print(C.RED(f'[!AA]Failur to download {i+1}image: {e}'))
                continue
        
        return result_article




if __name__ == '__main__':

    title_url_dict = {"[July.15]Steam\u2019s top games by copies sold (week 28) \u2013 Indies and discounts everywhere!": "https://alineaanalytics.com/blog/steam_week_28/"}
    pass
