import requests
from bs4 import BeautifulSoup
from pathlib import Path
import re
import json


if __name__ != '__main__':
    from websites.C import C
else:
    from C import C


class _GameSpot:
    
    body_html_path = Path(__file__).parent.parent / 'database/GameSpot/body.html'
    article_url_path = body_html_path.parent / 'article_url.jsonl'
    output_path = Path().home() / 'storage/shared/ArticleOutput/GameSpot'
    
    body_html_path.parent.mkdir(parents = True, exist_ok = True)
    output_path.mkdir(parents = True, exist_ok = True)
    
    url = 'https://www.gamespot.com/games/xbox-series-x'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}


    @classmethod
    def get_write_body(cls):
        
        print(C.YELLOW('[GS]Getting body html...'), end='', flush=True)
        try:
            response = requests.get(_GameSpot.url, headers=_GameSpot.headers)
            soup = BeautifulSoup(response.text, 'html.parser').body
            body = soup.find('section', class_='editorial river js-load-forever-container')#type: ignore
            
            _GameSpot.body_html_path.write_text(body.prettify(), encoding='utf-8')#type: ignore
        except Exception as e:
            print(C.RED(f'\n[!GS]') + f'Raise error while finding tag <section>: {e}')
            return False
        
        print(C.YELLOW(' Complete.'))


    @classmethod
    def get_article_url(cls):
        
        body_html = _GameSpot.body_html_path.read_text(encoding='utf-8')
        body = BeautifulSoup(body_html, 'html.parser')
        
        #process and get article urls
        tags_contain_url = body.find_all('div', class_=re.compile('card-item base-flexbox flexbox-align-center width.*'))
        result_list = []
        for tag in tags_contain_url:
            a_tag = tag.find('a', href=True, class_=True)#type: ignore
            url = 'https://www.gamespot.com' + a_tag['href']#type: ignore
            title = a_tag.get_text(strip=True)#type: ignore
            result_list.append({title: url})
        
        #write in
        print(C.YELLOW('[GS]Writing article url...'), end='', flush=True)
        f = open(str(_GameSpot.article_url_path), 'w', encoding='utf-8')
        for title_url_dict in result_list:
            json.dump(title_url_dict, f)
            f.write('\n')
        f.close()
        print(C.YELLOW(' Complete.'))


    @classmethod
    def cls_output_article(cls, title_url_dict: dict[str, str]):
        print(C.YELLOW('[GS]Getting reaponse and writing article...'), end='', flush=True)
        
        url = next(iter(title_url_dict.values()))
        title = next(iter(title_url_dict))
        title_prefix = title[:35]
        
        #get publish date
        response = requests.get(url, headers=_GameSpot.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        try:
            pub_date = soup.find('time', datetime=True)['datetime']#type: ignore
            pub_date = re.sub(r'(\d{4}-)(\d\d)(-)(\d\d)(.*)', r'\2.\4', pub_date)#type: ignore
        except Exception as e:
            print(C.RED(f'\n[!GS]') + f'Raise error while getting publication date: {e}')
            return False
        
        #get article
        try:
            article_head = soup.find('section', class_='news-hdr js-seamless-content__page-header has-rhythm--max')
            article_head = '\n'.join([article_head.h1.text, article_head.p.text, ''])#type: ignore
        except Exception: article_head = ''
        
        class_ = ['js-content-entity-body content-entity-body','js-image-gallery__list-wrapper image-gallery__list-wrapper']
        div_tag = soup.find('div', class_=class_)
        tags_contain_article = div_tag.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])#type: ignore
        
        article = article_head
        for tag in tags_contain_article:
            article = article + '\n' + tag.get_text(separator='\n', strip=True)
        article = article + '\n\n---Published by  GameSpot'
        
        #write in article
        output_path = _GameSpot.output_path / pub_date / f'{title_prefix}….txt'
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(article, encoding='utf-8')
            print(C.YELLOW('Complete, getting images...'))
        except Exception as e:
            print(C.RED(f'\n[!GS]') + f'Raise error while writing article: {e}')
            return False
        
        #download images
        img_path = output_path.parent / f'{title_prefix}'
        img_path.mkdir(exist_ok=True)
        
        figure_tags = div_tag.find_all('figure', attrs={'data-align': 'center'})#type: ignore
        img_urls = []
        for tag in figure_tags:
            try: img_urls.append(tag['data-img-src'])#type: ignore
            except Exception: continue
        
        for i, img_url in enumerate(img_urls):
            try:
                image_response = requests.get(img_url, headers=_GameSpot.headers, stream=True)#type: ignore
                with open(str(img_path / f'[{i+1}]-{title_prefix}….png'), 'wb') as f:
                    for chunk in image_response.iter_content(2200): f.write(chunk)
                print(C.YELLOW(f'[GS]Picture {i+1} writen.'))
                
            except Exception as e:
                print(C.RED(f'[!GS]') + f'Failur to download {i+1}image: {e}')
                continue
        
        return article





if __name__ == '__main__':
    dict = {"This Ghost Story Musical Is Packed With Personality And A Fright-Filled Mystery": "https://www.gamespot.com/articles/this-ghost-story-musical-is-packed-with-personality-and-a-fright-filled-mystery/1100-6534108/"}
    pass
