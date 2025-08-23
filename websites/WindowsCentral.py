import requests
from bs4 import BeautifulSoup
from pathlib import Path
import re
import json


if __name__ != '__main__':
    from websites.C import C
else:
    from C import C


class WindowsCentral:

    body_html_path = Path(__file__).parent.parent / 'database/WindowsCentral/body.html'
    article_url_path = body_html_path.parent / 'article_url.jsonl'
    output_path = Path().home() / 'storage/shared/ArticleOutput/WindowsCentral'

    body_html_path.parent.mkdir(parents = True, exist_ok = True)
    output_path.mkdir(parents = True, exist_ok = True)

    url = 'https://www.windowscentral.com/gaming/news'
    headers = {'User-Agent': "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36"}




    @classmethod
    def get_write_body(cls):
        print(C.YELLOW('[Win]Getting response...'))
        
        response = requests.get(WindowsCentral.url, headers = WindowsCentral.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        body = soup.body
        
        WindowsCentral.body_html_path.write_text(body.prettify(), encoding = 'utf-8')#type: ignore
        print(C.YELLOW('[Win]Body html has been writen.'))
        return



    @classmethod
    def get_article_url(cls):
        print(C.YELLOW('[Win]Processing body html...'))
        
        #get new url list from local body file
        with open(str(WindowsCentral.body_html_path), 'r', encoding = 'utf-8') as f:
            body = BeautifulSoup(f.read(), 'html.parser')
        
        news_div = body.find('div', class_ = "listingResults news")#type: ignore
        new_list = news_div.find_all('a', class_ = 'article-link')#type: ignore
        
        for i, a in enumerate(new_list):
            new_list[i] = {a['aria-label'].strip() : a['href']}#type: ignore
            
        #get original url list from local article_url file
        with open(WindowsCentral.article_url_path, 'r+', encoding = 'utf-8') as f:
            f.seek(0)
            original_list = []
            for line in f: original_list.append(json.loads(line.strip()))
            
            #process and get result_list
            result_list = []
            for x in (new_list + original_list):
                if not x in result_list: result_list.append(x)
            
            #write in new title_url_dict
            f.seek(0)
            for title_url_dict in result_list[:20]:
                json.dump(title_url_dict, f, ensure_ascii = False)
                f.write('\n')
            f.truncate()
            
            print(C.YELLOW('[Win]Article url and title has been writen.'))



    @classmethod
    def cls_output_article(cls, title_url_dict: dict[str, str]):
        print(C.YELLOW('[Win]Getting and processing article response...'))
        url = next(iter(title_url_dict.values()))
        title_prefix = next(iter(title_url_dict.keys()))[:14]
        
        #get publish date and tags that contain article text from target url
        response = requests.get(url, headers = WindowsCentral.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        pub_date: str = soup.find('meta', attrs = {'name': 'pub_date'})['content']#type: ignore
        pub_date = re.sub(r'\d\d\d\d-(\d\d)-(\d\d).*', r'\1.\2', pub_date)
        
        body = soup.body.find('div', id = 'article-body')#type: ignore
        content_tags = body.find_all(['a', 'p', 'ul'], recursive = False)#type: ignore
        
        
        #format article
        join_list = []
        for tag in content_tags:
            join_list.append(re.sub(r'\n\s*\n', '\n', tag.text).strip())
        article = ' '.join(join_list)
         
        processed_article = re.sub('\n', ' ', article)
        processed_article = re.sub(r'\s\s*\s', ' ', processed_article)
        processed_article = re.sub(r'(\.)([ "]*?[A-Z])', r'\1\n\2', processed_article)
        #generate direction with date and write in artile
        output_path = WindowsCentral.output_path / pub_date
        output_path.mkdir(parents = True, exist_ok = True)
        
        (output_path / f'{title_prefix}.txt').touch()
        (output_path / f'{title_prefix}.txt').write_text(processed_article, encoding = 'utf-8')
        
        print(C.YELLOW(f'[Win]Article "{title_prefix}.txt" has created.'))
        
        
        #get and download article picture
        picture_path = (output_path / f'{title_prefix}')
        picture_path.mkdir(parents = True, exist_ok = True)
        
        print(C.YELLOW('[Win]Searching for picture url.'))
        tags_cantain_picture = body.find_all(lambda tag: tag.find('figcaption', recursive = False))#type: ignore
        for i, tag in enumerate(tags_cantain_picture):
            try:
                picture_url = tag.find('img')['data-original-mos']#type: ignore
                picture_response = requests.get(picture_url, stream = True)#type: ignore
                with open(str(picture_path / f'{i+1}-{title_prefix}.png'), 'wb') as f:
                    for chunk in picture_response.iter_content(2200): f.write(chunk)
                print(C.YELLOW(f'[Win]Picture {i+1} writen.'))
            
            except Exception as e:
                print(C.RED(f'[!Win]Failur to download {i+1} picture: {e}'))
                continue





if __name__ == '__main__':
    WindowsCentral.get_article_url()
    pass
