import requests
from bs4 import BeautifulSoup
import json

class WebResponse:
    def __init__(self):
        pass

    def response_html(self, site = None, header = None):
        target_url = site if site else self.default_site

        try:
            response = requests.get(target_url)
            response.raise_for_status()
            # print(response.text)
            soup = BeautifulSoup(response.text, 'html.parser')

            title = soup.title.string if soup.title else 'No title'
            
            json_data = json.loads(response.content)
            print(json_data)
            # print(soup) 

            # print(' -- [success] --')
            # print(f"URL = {target_url}")
            # print(f"title = {title}")

            return soup
        
        except requests.exceptions.RequestException as e:
            print(f"Error = {e}")
            return None
    
        
def main():
    url = 'https://comic.naver.com/api/webtoon/titlelist/weekday?order=user'
    referer = 'https://comic.naver.com/webtoon'
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36'
    headers = {'referer' : referer, 'user-agent' : user_agent}
    web = WebResponse()
    try:
        web.response_html(url, headers)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()

'''
request url = https://comic.naver.com/api/webtoon/titlelist/weekday?order=user
referer = https://comic.naver.com/webtoon
user_agnet = Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36
'''