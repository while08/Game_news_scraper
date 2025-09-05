import requests
from bs4 import BeautifulSoup
from pathlib import Path
import re
import json


if __name__ != '__main__':
    from websites.C import C
else:
    from C import C


class _TheVerge:

    body_html_path = Path(__file__).parent.parent / 'database/TheVerge/body.html'
    article_url_path = body_html_path.parent / 'article_url.jsonl'
    output_path = Path().home() / 'storage/shared/ArticleOutput/TheVerge'
    
    body_html_path.parent.mkdir(parents = True, exist_ok = True)
    output_path.mkdir(parents = True, exist_ok = True)
    
    url = 'https://www.theverge.com/games'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}



    @classmethod
    def get_write_body(cls):
        print(C.YELLOW('[Veg]Getting body html...'), end='', flush=True)
        
        response = requests.get(_TheVerge.url, headers=_TheVerge.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        
        try:
            body1 = (soup.body
                   .find_all('div', recursive=False)[0]#type: ignore
                   .find_all('div', recursive=False)[0]#type: ignore
                   .find_all('div', recursive=False)[2]#type: ignore
                   .main#type: ignore
                   .find_all('div', recursive=False)[4]#type: ignore
                   .find_all('div', recursive=False)[0]#type: ignore
                   .find_all('div', recursive=False)[0]#type: ignore
                   .find_all('div', recursive=False)[0])#type: ignore
        except Exception as e:
            print(C.RED(f'\n[!Veg]Faild to get first 2 article urls: {e}'))
            body1 = BeautifulSoup('<div></div>')
        
        try:
            body2 = (soup.body
                   .find_all('div', recursive=False)[0]#type: ignore
                   .find_all('div', recursive=False)[0]#type: ignore
                   .find_all('div', recursive=False)[2]#type: ignore
                   .main#type: ignore
                   .find_all('div', recursive=False)[4]#type: ignore
                   .find_all('div', recursive=False)[0]#type: ignore
                   .find_all('div', recursive=False)[1]#type: ignore
                   .find_all('div', recursive=False)[0]#type: ignore
                   .find_all('div', recursive=False)[0]#type: ignore
                   .find_all('div', recursive=False)[1]#type: ignore
                   .div)#type: ignore
        except Exception as e:
            print(C.RED(f'\n[!Veg]Path of target div tag might be changed, please check: {e}'))
            return False
        
        for useless_tag in body2.find_all('div', attrs={'data-concert-ads-name': True}, recursive=False): useless_tag.extract()#type: ignore
        
        body_html = body1.prettify() + '<!--SEP-->\n' + body2.prettify()#type: ignore
        _TheVerge.body_html_path.write_text(body_html, encoding='utf-8')#type: ignore
        print(C.YELLOW(' Complete.'))


    @classmethod
    def get_article_url(cls):
        
        #get target  that contains article url
        body_html = _TheVerge.body_html_path.read_text(encoding='utf-8')
        body = BeautifulSoup(body_html, 'html.parser')
        result_list = []
        
        body1 = body.find_all(recursive=False)[0]#type: ignore
        body2 = body.find_all(recursive=False)[1]#type: ignore
        url_head = 'https://www.theverge.com'
        
        #body1
        if body1.find_all(recursive=False) != []:#type: ignore
            tags_contain_url = body1.find_all('div', recursive=False)#type: ignore
            for tag in tags_contain_url:
                try:
                    a = tag.find('a')#type: ignore
                    title = a.text.strip()#type: ignore
                    url = url_head + a['href']#type: ignore
                    result_list.append({title: url})
                except Exception: continue
        
        #body2
        for tag in body2.find_all(recursive=False):#type: ignore
            try:
                
                if tag.has_attr('role'): continue#type: ignore
                title_url_dict = {tag.a.text.strip(): url_head + tag.a['href']}#type: ignore
                result_list.append(title_url_dict)
            
            except Exception as e:
                print(C.RED(f'[!Veg]Url error: {e}'))
                continue
        
        #write in title_url_dict
        print(C.YELLOW('[Veg]Writing article url...'), end='', flush=True)
        f = open(str(_TheVerge.article_url_path), 'w', encoding='utf-8')
        
        for title_url_dict in result_list:#type: ignore
            try:
                json.dump(title_url_dict, f)
                f.write('\n')
                
            except Exception as e:
                print(C.RED(f'\n[!Veg]Raise error: {e}'))
                continue
        f.close()
        print(C.YELLOW(' Complete.'))


    @classmethod
    def cls_output_article(cls, title_url_dict: dict[str, str]):
        print(C.YELLOW('[Veg]Getting reaponse and writing article...'), end='', flush=True)
        
        url = next(iter(title_url_dict.values()))
        title = next(iter(title_url_dict))
        title_prefix = title[:35]
        
        #get publish date and tags that contain article text
        response = requests.get(url, headers=_TheVerge.headers)
        article_tag = BeautifulSoup(response.text, 'html.parser').article
        for useless_tag in article_tag.find_all(['ul', 'aside']):#type: ignore
            if useless_tag.name == 'ul' and 'duet--article--unordered-list' in useless_tag.get('class'): continue#type: ignore
            useless_tag.extract()
        try:
            pub_date = article_tag.div.find('time')['datetime']#type: ignore
            pub_date = re.sub(r'(\d{4}-)(\d\d)(-)(\d\d)(.*)', r'\2.\4', pub_date)#type: ignore
        except Exception as e:
            print(C.RED(f'\n[!Veg]Raise error while getting publish date: {e}'))
            return False
        
        #title of article
        try:
            div1 = article_tag.find(lambda tag: tag.name == 'div' and tag.get('class') == [])#type: ignore
            article = div1.get_text(separator=' / ', strip=True) + '\n'#type: ignore
        except Exception: article = ''
        
        #main article
        tag_contains_id = article_tag.find_all('div', recursive=False)[1]#type: ignore
        tag_contains_id = tag_contains_id.find('div', id=True)#type: ignore
        tags_contain_article = (tag_contains_id#type: ignore
            .find_all((lambda tag: tag.name == 'div' and tag.find(['p', 'h2', 'ul']) is not None), recursive=False))#type: ignore
        
        for tag in tags_contain_article:
            if tag.find('ul', recursive=False):#type: ignore
                li_list = tag.ul.find_all(recursive=False)#type: ignore
                for li in li_list:#type: ignore
                    para = '-' + li.get_text(separator=' ', strip=True) + '\n'
                    article = article + para
                continue
            
            para = tag.get_text(separator=' ', strip=True) + '\n'
            article = article + para
        article = article + '---\nPublished by The Verge'
        
        #write in article
        output_path = _TheVerge.output_path / pub_date / f'{title_prefix}….txt'
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(article, encoding='utf-8')
            print(C.YELLOW('Complete, getting images...'))
        except Exception as e:
            print(C.RED(f'\n[!Veg]Raise error while writing article: {e}'))
            return False
        
        #get images url
        img_url_list = []
        try:
            img_url = article_tag.div.img['srcset']#type: ignore
            img_url = re.search(r'828w, (.*?) 1080w,', img_url).group(1)#type: ignore
            img_url_list.append(img_url)
        except Exception as e: print(C.RED(f'[!Veg]Get image url wrong: {e}'))
        
        img_tags = tag_contains_id.find_all('img', src=True)#type: ignore
        if len(img_tags) != 0:
            for tag in img_tags:
                try:
                    img_url = tag['srcset']#type: ignore
                    img_url = re.search(r'828w, (.+?) 1080w,', img_url).group(1)#type: ignore
                    img_url_list.append(img_url)
                except Exception as e: print(C.RED(f'[!Veg]Get image url wrong: {e}'))
        
        #download images
        img_path = output_path.parent / f'{title_prefix}'
        img_path.mkdir(exist_ok=True)
        
        for i, img_url in enumerate(img_url_list):
            try:
                image_response = requests.get(img_url, headers=_TheVerge.headers, stream=True)#type: ignore
                with open(str(img_path / f'[{i+1}]-{title_prefix}….png'), 'wb') as f:
                    for chunk in image_response.iter_content(2200): f.write(chunk)
                print(C.YELLOW(f'[Veg]Image {i+1} writen.'))
            
            except Exception as e:
                print(C.RED(f'[!Veg]Failur to download {i+1}image: {e}'))
                continue
        
        return article




if __name__ == '__main__':
    d = {"2025 is turning into a good year for long-awaited games": "https://www.theverge.com/games/763698/delayed-games-silksong-metroid-prime-4-2025"}
    d2 = {"Microsoft\u2019s Xbox handheld is a good first step toward a Windows gaming OS": "https://www.theverge.com/notepad-microsoft-newsletter/763357/microsoft-asus-xbox-ally-handheld-hands-on-notepad"}

