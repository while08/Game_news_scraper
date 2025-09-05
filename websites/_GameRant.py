import requests
from bs4 import BeautifulSoup
from pathlib import Path
import re
import json


if __name__ != '__main__':
    from websites.C import C
else:
    from C import C


class _GameRant:
    
    body_html_path = Path(__file__).parent.parent / 'database/GameRant/body.html'
    article_url_path = body_html_path.parent / 'article_url.jsonl'
    output_path = Path().home() / 'storage/shared/ArticleOutput/GameRant'
    
    body_html_path.parent.mkdir(parents = True, exist_ok = True)
    output_path.mkdir(parents = True, exist_ok = True)
    
    url = 'https://gamerant.com/tag/xbox'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}


    @classmethod
    def get_write_body(cls):
        
        print(C.YELLOW('[Ran]Getting body html...'), end='', flush=True)
        try:
            response = requests.get(_GameRant.url, headers=_GameRant.headers)
            soup = BeautifulSoup(response.text, 'html.parser').body
            body = soup.select_one(#type: ignore
                    'body > main > section.wrapper.w-section-latest div.sentinel-listing-page-list')
            
            _GameRant.body_html_path.write_text(body.prettify(), encoding='utf-8')#type: ignore
        except Exception as e:
            print(C.RED(f'\n[!Ran]') + f'Raise error while writing body html: {e}')
            return False
        
        print(C.YELLOW(' Complete.'))


    @classmethod
    def get_article_url(cls):
        
        body_html = _GameRant.body_html_path.read_text(encoding='utf-8')
        body = BeautifulSoup(body_html, 'html.parser').div
        divs_contain_url = body.select('div > div.article')#type: ignore
        
        result_list = []
        for div in divs_contain_url:
            a_tag = div.select_one('div h5 > a')
            
            title = a_tag['title'].strip()#type: ignore
            url = 'https://gamerant.com' + a_tag['href']#type: ignore
            pub_date = div.select_one('div time')['datetime']#type: ignore
            pub_date = re.sub(r'(\d{4}-)(\d\d)(-)(\d\d)(.*)', r'\2.\4', pub_date)#type: ignore
            
            result_list.append({f'[{pub_date}]{title}': url})
        
        #write in
        print(C.YELLOW('[Ran]Writing article url...'), end='', flush=True)
        f = open(str(_GameRant.article_url_path), 'w', encoding='utf-8')
        for title_url_dict in result_list:
            json.dump(title_url_dict, f)
            f.write('\n')
        f.close()
        print(C.YELLOW(' Complete.'))


    @classmethod
    def cls_output_article(cls, title_url_dict: dict[str, str]):
        print(C.YELLOW('[Ran]Getting reaponse and writing article...'), end='', flush=True)
        
        #get info
        url = next(iter(title_url_dict.values()))
        origin_title = next(iter(title_url_dict))
        title = re.sub(r'(\[.+?\])(.+)', r'\2', origin_title)
        title_prefix = title[:35]
        pub_date = re.sub(r'(\[)(.+?)(\].+)', r'\2', origin_title)
        
        response = requests.get(url, headers=_GameRant.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        #get article
        target_div = soup.body.select_one('body > main > article > section#article-body > div')#type: ignore
        article = title + '\n'
        
        for tag in target_div.find_all(recursive=False)[:-1]:#type: ignore
            try:
                if tag.name == 'section' and 'emaki-custom-note' in tag.get('class'):#type: ignore
                    article += f'(Note: "{tag.get_text(separator=' ', strip=True)}")\n'
                    continue
                
                if tag.name == 'ul':#type: ignore
                    for li in tag.select('ul li'):#type: ignore
                        article +=  f'-{li.get_text(separator=" ", strip=True)}\n'
                    continue
                
                if tag.name == 'div' and 'table-container' in tag.get('class'):#type: ignore
                    for tr in tag.select('div > table tr'):#type: ignore
                        row_list = []
                        for td in tr.find_all(['td', 'th']):
                            row_list.append(td.get_text(separator=' ', strip=True))
                        article += ' | '.join(row_list) + '\n'
                    continue
                
                if tag.name == 'div' and 'body-img' in tag.get('class'):#type: ignore
                    continue
                
                if tag.name == 'script':#type: ignore
                    continue
                
                if not tag.get_text(strip=True):
                    continue
                
                article += tag.get_text(separator=' ', strip=True) + '\n'
            except Exception as e:
                print(e)
                continue
                
        article += '\n——Published by GameRant'
        
        #write in article
        output_path = _GameRant.output_path / pub_date / f'{title_prefix}….txt'
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(article, encoding='utf-8')
            print(C.YELLOW('Complete, getting images...'))
        except Exception as e:
            print(C.RED(f'\n[!Ran]Raise error while writing article: {e}'))
            return False
        
        #get image urls
        img_path = output_path.parent / f'{title_prefix}'
        img_path.mkdir(exist_ok=True)
        img_url_list = []
        
        try:#thumb nail
            thumbnail_url = soup.head.select_one('meta[property="og:image"]')['content']#type: ignore
            img_url_list.append(thumbnail_url)
        except Exception as e:
            print(C.RED('[!Ran]') + f'Thumb nail error: {e}')
        
        #article images
        for div in target_div.find_all('div', class_='body-img', recursive=False):#type: ignore
            try:
                img_url = div.select_one('div img')['data-img-url']#type: ignore
                img_url_list.append(img_url)
            except Exception as e:
                print(C.RED('[!Ran]') + f'Image error: {e}')
        
        #download images
        for i, img_url in enumerate(img_url_list):
            try:
                image_response = requests.get(img_url, headers=_GameRant.headers, stream=True)#type: ignore
                with open(str(img_path / f'[{i+1}]-{title_prefix}….png'), 'wb') as f:
                    for chunk in image_response.iter_content(2200): f.write(chunk)
                print(C.YELLOW(f'[Ran]Picture {i+1} writen.'))
                
            except Exception as e:
                print(C.RED(f'[!Ran]') + f'Failur to download {i+1}image: {e}')
                continue
        
        return article




if __name__ == '__main__':
    d1 = {"[08.31]MGS Delta: Snake Eater Is Seemingly Off to a Slow Start": "https://gamerant.com/mgs-delta-snake-eater-play-count-sales-estimate-launch-week/"}
    _GameRant.cls_output_article(d1)
    pass
