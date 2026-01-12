import requests
from bs4 import BeautifulSoup
import json

class WebResponse:
    def __init__(self):
        self.default_site = ""
        self.datas = {}

    def response_html(self, site = None, header = None):
        target_url = site if site else self.default_site
        # print(header)
        try:
            response = requests.get(target_url)
            response.raise_for_status()
            json_data = json.loads(response.content)
            week = [*json_data["titleListMap"].keys()]
            for w in week:
                data_title, data_score = [], []
                contents =[*json_data['titleListMap'][w]]
                # print(f"\n ===== 요일 : {w} ====== \n")
                for i in contents:
                    # print(f"요일 : {w}, 제목 : <<{i['titleName']}>> , 별점 = {round(i['starScore'],2)} 점")
                    data_title.append(i['titleName'])
                    data_score.append(i['starScore'])
                    self.datas[w] = {'title' : data_title, 'score' : data_score}
            print(f"keys = {self.datas.keys()} \n")
            print(f"values = {self.datas.values()} \n \n")
            print(f"all datas = {self.datas}")
            return self.datas
        
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