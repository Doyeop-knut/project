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
        
        #payloads
        data = {"filter" : {} }
        data2 = {"vin2" :None}

        try:
            # get vehicle manufacturer infos (already prepared)
            for brand in self.general:
                model_name_url = target_url + "/models/" + brand
                response = requests.get(model_name_url)
                response.raise_for_status()
                json_data = json.loads(response.content)

                model = json_data["models"]
                # get vehicle model name
                for i in model:
                    manufacturer.append(i["manufacturer"]['slug']) 
                    model_name.append(i["path"])
                    url_model = {"brand" : brand, "models": model_name}
                print("success to get model names")
                print(model_name)
                for m in model_name:
                    generation_select_url = target_url + "generations"+ brand + "/" + m
                    response = requests.get(generation_select_url)
                    response.raise_for_status()
                    json_data = json.loads(response.content)
                    generations = json_data["generations"]
                    for i in generations:
                        generation_data.append(i["key"])
                    # print(generation_data)
                print("succes to get generation data")
                print(generation_data)
            #     # get path 
                for generation in generation_data:
                    # print(generation)
                    generation_filter_url = target_url + "variant-filters-3d" + brand + "/" +m + "/" + generation
                    print(generation_filter_url)
                    response = requests.post(generation_filter_url, data=data)
                    response.raise_for_status()
                    json_data = json.loads(response.content)
                    variants = json_data['variants']
                    # print(len(json_data['variants']))
                    for i in range(len(variants)):
                        path_data.append(variants[i]['path'])
                    print(path_data)
                print("success to get path data")

            # # print(path_data)
            # # get uid
            #     for path in path_data:
            #         diagram_url = target_url + "diagrams-new" + url_model["brand"] + "/" + path
            #         response = requests.post(diagram_url, data=data)
            #         response.raise_for_status()
            #         json_data = json.loads(response.content)
            #         diagrams = json_data["diagrams"]
            #         # print(json_data["diagrams"]["uid"])
            #         for i in range(len(diagrams)):
            #             for j in range(len(diagrams[i])):
            #                 uid.append(diagrams[i][j]["uid"])
            #                 print(uid)
            # # ==================FOR DEBUG ==================
            # # # response = requests.post("https://api.yoshiparts.com/part-list/car/toyota/4runner/grn280-grn280l_gkagk-gr-1grfe-atm-5fc-lhd/1314261_0", data=data2)
            # # response.raise_for_status()
            # # json_data = json.loads(response.content)
            # # products = json_data["products"]
            # # # diagram = json_data["diagram"]
            # # print(diagram["baseName"])
            # # for i in range(len(products)):
            # #     products_data.append({"baseName" : diagram["baseName"], "parts" : {"part_name" : products[i]["name"] , "weight" : products[i]["weight"]}})
            # # ============================================== #

            #     # load assembly lists
            #     for u in uid:
            #         product_url = target_url + "part-list" + self.general + "/4runner" + "/grn280-grn280l_gkagk-gr-1grfe-atm-5fc-lhd" + "/" + u
            #         response = requests.post(product_url, data=data2)
            #         response.raise_for_status()
            #         json_data = json.loads(response.content)
            #         products = json_data["products"]
            #         basename = json_data["diagram"]["baseName"]
            #         #load product infos
            #         for i in range(len(products)):
            #             products_data.append({"baseName" : basename, "parts" : {"part_name" : products[i]["name"] , "weight" : products[i]["weight"]}})
            #     #         print(i)
            #         print(products_data)
                model_name.clear()
                generation_data.clear()
            #     path_data.clear()
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