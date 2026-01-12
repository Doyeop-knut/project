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
                data_title_score = []
                contents =[*json_data['titleListMap'][w]]
                min_score = float('inf')

                print(f"\n ===== 요일 : {w} ====== \n")
                for i in contents:
                    # print(f"요일 : {w}, 제목 : <<{i['titleName']}>> , 별점 = {round(i['starScore'],2)} 점")
                    # data_title.append(i['titleName'])
                    # data_score.append(i['starScore'])
                    data_title_score.append({'title' : i['titleName'], 'score' : i['starScore']})
                    self.datas[w] = data_title_score
                # print(f"{self.datas[w]} \n \n \n")
                # print(f"length = {len(self.datas[w])}")
                for k in range(len(self.datas[w])):

                    if self.datas[w][k]['score'] < 9.5: # 9.5점 미만인 웹툰 제목
                        print(f"제목 : {self.datas[w][k]['title']} |  평점 : {self.datas[w][k]['score']}")

                    if min_score > self.datas[w][k]['score']:
                        min_score = self.datas[w][k]['score']
                        
                    if self.datas[w][k]['score'] == min_score:
                        min_scored_title = self.datas[w][k]['title']
            
                print(f"최하 평점 웹툰 제목 : {min_scored_title}, 평점 : {min_score}")
                    
                    
            # print(f"keys = {self.datas.keys()} \n")
            # print(f"values = {self.datas.values()} \n \n")
            # print(f"all datas = {self.datas['MONDAY']}")
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