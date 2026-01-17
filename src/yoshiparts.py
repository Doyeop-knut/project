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
        one_gen = []
        vehicle_info = None
        param_dict = {}
        
        #payloads
        data = {"filter" : {} }
        data2 = {"vin2" :None}

        try:
            ## 모델 정보
            model_name_url = target_url +"/models" + "/car/lexus"
            response = requests.get(model_name_url)
            response.raise_for_status()
            json_data = json.loads(response.content)
            models = json_data['models']
            print(json_data['models'])

            for i in models:
                print(f"model = {i['name']}")
                pass
                # print(f"oneChildPath = {i['oneChildPath']}")
            
            ## 세대 정보
            generation_select_url = target_url + "generations" + "/car/lexus" + "/es200"
            response = requests.get(generation_select_url)
            response.raise_for_status()
            json_data = json.loads(response.content)
            generations = json_data['generations']
            print(json_data['generations'])

            for j in generations:
                print(f"generations = {j['name']}, key = {j['key']}")
                pass
                # print(f"oneVariantPaths = {j['oneVariantPath']}")

            #generation_filter_url = target_url + "variant-filters-3d" + brand + "/" +m + "/" + generation
            variants_url = "https://api.yoshiparts.com/variant-filters-3d/car/kia/ev6/ev6_gen1"

            response = requests.post(variants_url, data=data)
            response.raise_for_status()
            json_data = json.loads(response.content)
            variants = json_data["variants"]
            # print(json_data["variants"])

            for k in variants:
                print(k['params'])
                params = k['params']
                # print(f"path = {k['path']}")
                for p in range(len(params)):
                    # print(f"{params[p][0]} - {params[p][1][0]}")\
                    # param_dict.update()
                    param_dict[params[p][0]] = params[p][1][0]
                    
                print(param_dict.keys())
                print(param_dict)
                
                    # pass
                # diagram_url = target_url + "parts" + "/car/kia" + "/diagrams/" + k['path']
                # https://api.yoshiparts.com/diagrams-new/car/kia/sephia_mentor_shuma_spectra/mentor_h_b_i_ii_1997_2004-aus-right_hand-5_door-middle_grade-1600_cc-mpi_dohc-5_speed_mt_2wd
                # https://api.yoshiparts.com/diagrams-new/car/kiasephia_mentor_shuma_spectra/mentor_h_b_i_ii_1997_2004-aus-left_hand-5_door-middle_grade-1800_cc-mpi_dohc-5_speed_mt_2wd
                
                diagram_url = target_url + "diagrams-new" + "/car/kia/" + k['path']
                response = requests.post(diagram_url, data = data)
                response.raise_for_status()
                json_data = json.loads(response.content)

                diagrams = json_data['diagrams']
                # print(json_data['diagrams'])

                for m in diagrams:
                    # print(m[0]['uid'])
                    uid = m[0]['uid']
 
                    u_url = target_url + "part-list" + "/car/kia/" + k['path'] + "/" + uid
                    response = requests.post(u_url, data = data2)
                    response.raise_for_status()
                    json_data = json.loads(response.content)
                    products = json_data['products']
                    # print(json_data['products'])
                    for prd in products:
                        # print(prd['name'])
                        pass
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
