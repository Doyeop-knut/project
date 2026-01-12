import requests
from bs4 import BeautifulSoup

class WebResponse:
    def __init__(self):
        self.default_site = None

    def response_html(self, site = None):
        target_url = site if site else self.default_site
        try:
            response = requests.get(target_url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            title = soup.title.string if soup.title else 'No title'

            print(' -- [success] --')
            # print(f"URL = {target_url}")
            print(f"title = {title}")

            return soup
        
        except requests.exceptions.RequestException as e:
            print(f"Error = {e}")
            return None
    
        
def main():
    url = 'https://www.google.com'
    web = WebResponse()
    try:
        web.response_html(url)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()