import requests
from bs4 import BeautifulSoup
import json

class WebResponse:
    def __init__(self):
        self.default_site = "https://www.yoshiparts.com/"
        self.general = ["/car/toyota", "/car/lexus", '/car/nissan', '/car/mazda', '/car/mitsubishi', '/car/honda', '/car/kia', '/car/hyundai', '/car/mercedes']
        self.datas = {}

    def response_html(self, site = None, header = None):
        target_url = site if site else self.default_site
        model_name = []
        manufacturer = []
        generation_data = []
        path_data = []
        uid = []
        products_data = []
        gen_number = []
        vehicle_info = None
        url_model = {}
        
        #payloads
        data = {"filter" : {} }
        data2 = {"vin2" :None}

        try:
            for brand in self.general:
                model_name_url = target_url + "/models/" + brand
                response = requests.get(model_name_url)
                response.raise_for_status()
                json_data = json.loads(response.content)
                model = json_data["models"]
                for i in model:
                    model_name.append(i["path"])
                    gen_number.append(i['generationCount'])
                    url_model.update({"manufacturer" : brand, "models" : model_name, "gen_num": gen_number})
            
                print(url_model["gen_num"])
                model_name.clear()
            return products_data
        
        except requests.exceptions.RequestException as e:
            print(f"Error = {e}")
            return None
    
        
def main():
    url = 'https://api.yoshiparts.com/'
    referer = 'https://yoshiparts.com/'
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36'
    headers = {'referer' : referer, 'user-agent' : user_agent}
    web = WebResponse()
    try:
        web.response_html(url, headers)
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()

"""
model selection url = https://api.yoshiparts.com/models/car/toyota
generation selection url = https://api.yoshiparts.com/generations/car/toyota/4runner
generation filter url = https://api.yoshiparts.com/variant-filters-3d/car/toyota/4runner/4runner-gen_5
parts url = https://api.yoshiparts.com/diagrams-new/car/toyota/4runner/grn280-grn280l_gkagk-gr-1grfe-atm-5fc-lhd



"""