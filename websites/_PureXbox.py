import requests
from bs4 import BeautifulSoup
from pathlib import Path
import re
import json


if __name__ != '__main__':
    from websites.C import C
else:
    from C import C


class _PureXbox:
    
    body_html_path = Path(__file__).parent.parent / 'database/PureXbox/body.html'
    article_url_path = body_html_path.parent / 'article_url.jsonl'
    output_path = Path().home() / 'storage/shared/ArticleOutput/PureXbox'
    
    body_html_path.parent.mkdir(parents = True, exist_ok = True)
    output_path.mkdir(parents = True, exist_ok = True)
    
    url = 'https://www.purexbox.com/timeline'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'}



    @classmethod
    def get_write_body(cls):
        
        print(C.YELLOW('[PX]Getting body html...'), end='', flush=True)
        
        response = requests.get(_PureXbox.url, headers=_PureXbox.headers)
        soup = BeautifulSoup(response.text, 'lxml').body
        body = soup.find('div', class_='ui-listing-group-day')#type: ignore
        _PureXbox.body_html_path.write_text(soup.prettify(), encoding = 'utf-8')#type: ignore
        print(C.YELLOW(' Complete.'))


    @classmethod
    def get_article_url(cls):
        print(C.YELLOW('[PX]Writing article url...'), end='', flush=True)
        #get target <li> tags that contains article url
        body_html =_PureXbox.body_html_path.read_text(encoding = 'utf-8')#type: ignore
        body = BeautifulSoup(body_html, 'html.parser').body
        body = body.select_one('div.ui-listing-body.ui-listing-group-day')#type: ignore
        
        li_tags = body.find_all('li', class_='item-article')#type: ignore
        result_list = []
        for li in li_tags:
            info_div = li.find('div', class_='info')#type: ignore
            
            url = info_div.select_one('a.title.accent-hover')#type: ignore
            url = 'https://www.purexbox.com/' + url['href']#type: ignore
            
            gener = info_div.select_one('span.category.accent').get_text(strip=True)#type: ignore
            title = info_div.select_one('span.title.accent-hover')#type: ignore
            title = title.get_text(strip=True)#type: ignore
            
            pub_date = info_div.find('time')['datetime']#type: ignore
            pub_date = re.sub(r'(\d{4}-)(\d\d)(-)(\d\d)(.*)', r'\2.\4', pub_date)#type: ignore
            
            result_list.append({f'[{pub_date}]{gener}: {title}': url})
            if len(result_list) >= 20: break
        
        #write into local 
        f = open(str(_PureXbox.article_url_path), 'w', encoding='utf-8')
        for title_url_dict in result_list:
            json.dump(title_url_dict, f)
            f.write('\n')
        f.close()
        print(C.YELLOW(' Complete.'))


    @classmethod
    def cls_output_article(cls, title_url_dict: dict[str, str]):
        print(C.YELLOW('[PX]Getting reaponse and writing article...'), end='', flush=True)
        
        #get info and <section> tag
        url = next(iter(title_url_dict.values()))
        origin_title = next(iter(title_url_dict))
        title = re.sub(r'(\[.+?\])(.+)', r'\2', origin_title)
        title_prefix = title[:35]
        pub_date = re.sub(r'(\[)(.+?)(\].+)', r'\2', origin_title)
        
        response = requests.get(url, headers=_PureXbox.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        target_section = soup.body.article.select_one('section.text')#type: ignore
        tag_names = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'table', 'blockquote', 'div']
        tags_contain_article = target_section.find_all(tag_names, recursive=False)#type: ignore
        
        #get article
        article = title + '\n'
        for tag in tags_contain_article:
            try:
                if tag.name == 'div':#type: ignore
                    if 'poll' not in tag.get('class'): continue#type: ignore
                    
                    fieldset = tag.select_one('div fieldset')#type: ignore
                    poll_title = fieldset.find("legend").get_text(strip=True)#type: ignore
                    article += f'\n[{poll_title}](poll)\n'#type: ignore
                    
                    for label in fieldset.div.select('div > span > label'):#type: ignore
                        article += f'（ ）{label.get_text(strip=True)}\n'
                    continue
                
                if tag.name == 'ul':#type: ignore
                    for li in tag.select('ul > li'):#type: ignore
                        article += f'-{li.get_text(separator=' ', strip=True)}\n'
                    continue
                
                if tag.name == 'table':#type: ignore
                    for tr in tag.select('table tr'):#type: ignore
                        td_list = []
                        for td in tr.select('tr td'):
                            td_list.append(td.get_text(separator=' ', strip=True))
                        article += (" | ".join(td_list) + '\n')
                    continue
                
                if tag.name == 'blockquote':#type: ignore
                    article += f'—“{tag.get_text(separator=' ', strip=True)}”\n'
                    continue
                
                article += f'{tag.get_text(separator=' ', strip=True)}\n'
            except Exception as e:
                print(e)
                continue
        article += '\n——Published by PureXbox'
        
        #write in article
        output_path = _PureXbox.output_path / pub_date / f'{title_prefix}….txt'
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(article, encoding='utf-8')
            print(C.YELLOW('Complete, getting images...'))
        except Exception as e:
            print(C.RED(f'\n[!PX]Raise error while writing article: {e}'))
            return False
        
        #get image urls
        img_path = output_path.parent / f'{title_prefix}'
        img_path.mkdir(exist_ok=True)
        img_url_list = []
        
        try:
            thumbnail_url = soup.head.select_one('meta[property="og:image"]')['content']#type: ignore
            img_url_list.append(thumbnail_url)
        except Exception as e:
            print(C.RED('[!PX]') + f'Thumb nail error: {e}')
        
        for gallery in target_section.select('section > aside.gallery'):#type: ignore
            for a in gallery.select('aside a[href]'):
                try: img_url_list.append(a['href'])
                except Exception as e: print(C.RED('[!]') + f'Image error: {e}')
        
        for a in target_section.select('section > figure > a[href]')[1:]:#type: ignore
            try: img_url_list.append(a['href'])
            except Exception as e: print(C.RED('[!PX]') + f'Image error: {e}')
        
        #download images
        for i, img_url in enumerate(img_url_list):
            try:
                image_response = requests.get(img_url, headers=_PureXbox.headers, stream=True)#type: ignore
                with open(str(img_path / f'[{i+1}]-{title_prefix}….png'), 'wb') as f:
                    for chunk in image_response.iter_content(2200): f.write(chunk)
                print(C.YELLOW(f'[PX]Picture {i+1} writen.'))
                
            except Exception as e:
                print(C.RED(f'[!PX]') + f'Failur to download {i+1}image: {e}')
                continue
        
        return article



if __name__ == '__main__':
    d = {"[08.29]News: 23 New Xbox Play Anywhere Games Highlighted In Latest Monthly Roundup": "https://www.purexbox.com/news/2025/08/23-new-xbox-play-anywhere-games-highlighted-in-latest-monthly-roundup"}
    d2 = {"[08.29]News: Delta Force Dev Announces Plans For Lots More Xbox Features And FPS Improvements": "https://www.purexbox.com/news/2025/08/delta-force-dev-announces-plans-for-lots-more-xbox-features-and-fps-improvements"}
    d3 = {"[08.29]News: Yooka-Replaylee Hits Xbox In October 2025, And It's Discounted If You Own The Original": "https://www.purexbox.com/news/2025/08/yooka-replaylee-hits-xbox-in-october-2025-and-its-discounted-if-you-own-the-original"}

    _PureXbox.cls_output_article(d2)
    pass
