import requests
import json
from pathlib import Path
import re


if __name__ !='__main__': from websites.C import C
else: from websites.C import C


class DeepSeek:
    prompts_path = Path(__file__).parent / 'database/DeepSeek_prompts/prompts.json'
    with open(str(prompts_path), 'r', encoding='utf-8') as f:
        prompts: dict[str,str] = json.load(f)
    
    history_path = Path().home() / 'storage/shared/ArticleOutput/history'
    history_path.mkdir(parents=True, exist_ok=True)

    api_url = 'https://api.deepseek.com/chat/completions'
    key = '<your key here>'

    payload = {
            'messages': [],
            'model': 'deepseek-chat',
            'max_tokens': 8000,
            'response_format': {'type': 'text'},
            'stream': True,
            'temperature': 0.4
            }
    headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + key}

    
    @classmethod
    def output(cls, style: str, article: str, stream:bool=True, show=True):
        if not article: return None
        
        if style not in DeepSeek.prompts:
            print(C.BLUE('[DeepSeek]') + 'Prompt style not found.')
            return False
        
        messages = [{'role': 'system', 'content': DeepSeek.prompts[style]},
                   {'role': 'user', 'content': article}]
        
        payload = DeepSeek.payload
        payload['messages'] = messages
        payload['stream'] = stream
        payload = json.dumps(payload, ensure_ascii=False)
        
        if stream: print(C.BLUE('[DeepSeek]') + 'Getting stream response:\n')
        else: print(C.BLUE('[DeepSeek]') + 'Getting static response...\n')
        ai_response = requests.post(DeepSeek.api_url, headers=DeepSeek.headers, data=payload, stream=stream)
        history = DeepSeek.history_path / f'{article[:35]}.txt'
        
        result = ''
        if stream:
            for line in ai_response.iter_lines():
                if not line: continue
                line = line.decode('utf-8')
                if not line.startswith('data: '): continue
                data = line[6:]
                if data == '[DONE]': break
                try:
                    data = json.loads(data)
                    if ('choices' not in data) or (not data['choices']): continue
                    delta = data['choices'][0].get('delta', {})
                    if 'content' not in delta: continue
                    if (not delta['content']) or (re.fullmatch(' +', delta['content'])): continue
                    content = re.sub(r'  +', r' ', delta['content'])
                    content = re.sub(r'(  )([^!-~])', r'\2', content)
                    result += content
                    if show: print(content, end='', flush=True)
                except json.JSONDecodeError:
                    continue
            result = result + '\n'
            if show: print('\n')
            history.write_text(result)
        
        else:
            data = ai_response.json()
            if ('choices' in data and data['choices'] and
                'message' in data['choices'][0] and
                'content' in data['choices'][0]['message']):
                
                result = data['choices'][0]['message']['content'] + '\n'
                if show: print(result)
                history.write_text(result)
            
            else:
                history.write_text(result)
                print(C.BLUE('[!DeepSeek]') + 'Invalid response format, original response data writen.')


