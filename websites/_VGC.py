import requests
from bs4 import BeautifulSoup
from pathlib import Path
import re
import json


if __name__ != '__main__':
    from websites.C import C
else:
    from C import C


class _VGC:
    
    body_html_path = Path(__file__).parent.parent / 'database/VGC/body.html'
    article_url_path = body_html_path.parent / 'article_url.jsonl'
    output_path = Path().home() / 'storage/shared/ArticleOutput/VGC'
    
    body_html_path.parent.mkdir(parents = True, exist_ok = True)
    output_path.mkdir(parents = True, exist_ok = True)
    
    url = 'https://www.videogameschronicle.com/platforms/xbox'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}



    @classmethod
    def get_write_body(cls):
        
        print(C.YELLOW('[VGC]Getting body html...'), end='', flush=True)
        
        try:
            response = requests.get(_VGC.url, headers=_VGC.headers)
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser').body
            body = soup.find('div', class_='vgc-listing vgc-listing--index')#type: ignore
            
            _VGC.body_html_path.write_text(body.prettify(), encoding='utf-8')#type: ignore
        except Exception as e:
            print(C.RED(f'\n[!VGC]Raise error while finding tag <div>: {e}'))
            return False
            
        print(C.YELLOW(' Complete.'))


    @classmethod
    def get_article_url(cls):
        print(C.YELLOW('[VGC]Writing article url...'), end='', flush=True)
        
        #get target <article> that contains article url
        body_html = _VGC.body_html_path.read_text(encoding='utf-8')
        body = BeautifulSoup(body_html, 'html.parser')
        target_tags = body.find_all('article')
        
        f = open(_VGC.article_url_path, 'w', encoding='utf-8')
        for tag in target_tags:
            a = tag.find('a', title=True)#type: ignore
            try:
                title = a['title'].strip()#type: ignore
                url = a['href']#type: ignore
                pub_date = tag.find('time')['datetime'].strip()#type: ignore
                pub_date = re.sub(r'(\d{4}-)(\d\d)(-)(\d\d)(.*)', r'\2.\4', pub_date)#type: ignore
                
                json.dump({f'[{pub_date}] {title}': url}, f)
                f.write('\n')
            except Exception as e:
                print(C.RED(f'\n[!VGC]Raise error: {e}'))
                
        f.close()
        print(C.YELLOW(' Complete.'))


    @classmethod
    def cls_output_article(cls, title_url_dict: dict[str, str]):
        print(C.YELLOW('[VGC]Getting reaponse and writing article...'), end='', flush=True)
        
        #get info
        url = next(iter(title_url_dict.values()))
        origin_title = next(iter(title_url_dict))
        title = re.sub(r'(\[.+?\] )(.+)', r'\2', origin_title)
        pub_date = re.sub(r'(\[)(.+?)(\].+)', r'\2', origin_title)
        title_prefix = title[:35]
        
        #get publish date and tags that contain article text
        response = requests.get(url, headers=_VGC.headers)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        
        #get and write article to local
        article_tag = soup.find('article')
        
        title_tag = article_tag.find('div', class_='post__header-main')#type: ignore
        article = title_tag.get_text(separator='\n', strip=True)#type: ignore
        
        content_div = article_tag.find('div', id='content_body')#type: ignore
        content_tags = content_div.find_all(re.compile(r'(?:p|h\d|ul|blockquote)'), recursive=False)#type: ignore
        for tag in content_tags:
            article = article + '\n' + tag.get_text(separator='\n', strip=True)
        article = article + '\n\n——Published by VGC'
        
        output_path =_VGC.output_path / pub_date / f'{title_prefix}….txt'
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(article, encoding='utf-8')
            print(C.YELLOW('Complete, getting images...'))
        except Exception as e:
            print(C.RED(f'\n[!VGC]Raise error while writing article: {e}'))
            return False
        
        #get and download images to local
        img_path = output_path.parent / f'{title_prefix}'
        img_path.mkdir(exist_ok=True)
        img_url_list = []
        img_url_head = 'https://www.videogameschronicle.com'
        
        try:
            figure_tag = article_tag.find('figure', class_='post__featured-image')#type: ignore
            figure_img_srcset = img_url_head + figure_tag.find('img')['srcset']#type: ignore
            figure_img_url = re.search(r'480w, (.+) 768w', figure_img_srcset)
            figure_img_url = img_url_head + figure_img_url.group(1)#type: ignore
            img_url_list.append(figure_img_url)
        except Exception as e: print(C.RED(f'[!VGC]Thumb nail error: {e}'))
        
        figure_tags = content_div.find_all('figure', recursive=False)#type: ignore
        if figure_tags != []:
            for figure in figure_tags:
                try:
                    img_url = figure.find('img')['data-srcset']#type: ignore
                    img_url = re.search(r'480w, (.+) 768w', img_url)#type: ignore
                    img_url = img_url_head + img_url.group(1)#type: ignore
                    img_url_list.append(img_url)
                except Exception as e: print(C.RED(f'[!VGC]Image error: {e}'))
        
        for i, img_url in enumerate(img_url_list):
            try:
                image_response = requests.get(img_url, headers=_VGC.headers, stream=True)#type: ignore
                with open(str(img_path / f'[{i+1}]-{title_prefix}….png'), 'wb') as f:
                    for chunk in image_response.iter_content(2200): f.write(chunk)
                print(C.YELLOW(f'[VGC]Picture {i+1} writen.'))
                
            except Exception as e:
                print(C.RED(f'[!VGC]Failur to download {i+1}image: {e}'))
                continue
        
        return article




if __name__ == '__main__':
    t_u_list = {"[09.12] Xbox is reporting \u2018major outages\u2019 in certain online multiplayer features": "https://www.videogameschronicle.com/news/xbox-is-reporting-major-outages-in-certain-online-multiplayer-features/"}
    _VGC.cls_output_article(t_u_list)
    pass
