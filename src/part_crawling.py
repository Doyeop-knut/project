import requests
import sqlite3
import concurrent.futures

class Crawling:
    def __init__(self, max_workers = 5):
        self.api_base = "https://api.yoshiparts.com/"
        self.db_name = "part_data.db"
        self.max_workers = max_workers
        self._create_data()

    def _create_data(self):
        # 데이터베이스 생성 및 연결
        connect = sqlite3.connect(self.db_name)
        # 데이터베이스 제어 커서 
        cursor = connect.cursor()
        # ============= 데이터베이스 테이블 작성 =============
        # 1) ID (1씩 증가)
        # 2) manufacturer (제조사)
        # 3) model_name (차종)
        # 4) generation (세대)
        # 5) variant_path (판매 지역, 핸들 위치(좌/우) 등)
        # 6) 각 부품 정보 (diagram_uid)
        # 7) assy_name (부품 어셈블리 정보)
        # 8) part_name (부품 이름)
        # 9) weight (무게)
        # ==============================================
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS part_details (
                       id INTEGER PRIMARY KEY AUTOINCREMENT,
                       manufacturer TEXT,
                       model_name TEXT,
                       generation TEXT,
                       variant_path TEXT,
                       diagram_uid TEXT,
                       assy_name TEXT,
                       part_name TEXT,
                       weight TEXT,
                       UNIQUE(variant_path, diagram_uid, part_name)
                       )
                       ''')
        # DB에 수정사항 저장 및 DB 종료
        connect.commit()
        connect.close()
    def request_data(self, session, method, url, data=None):
        try:
            if method == 'GET':
                resp = session.get(url, timeout = 10)
            elif method == 'POST':
                resp = session.post(url, json=data, timeout = 10)
            if resp.status_code == 404:
                return None
            
            resp.raise_for_status()
            return resp.json()

        except Exception as e:
            print(f"ERROR OCCURED at {url} : {e}")


    def crawling(self, path):
        params_dict = {}

        # 제작사 정보 수집
        manufacturer = path.replace('/car/', '')
        print(f'\n [시작] 제작사 정보 수집 : {manufacturer}')

        # 웹사이트 연결 유지
        session = requests.Session()
        # 헤더 설정
        session.headers.update({
            'user-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
            'referer' : 'https://yoshiparts.com/'
        })
        # DB 연결 (timeout = 60)
        connect = sqlite3.connect(self.db_name, timeout = 60)

        try:
            # 모델 정보 불러오기
            models_data = self.request_data(session, 'GET', f"{self.api_base}models{path}")
            if not models_data: return 

            for model in models_data.get('models',[]):
                model_path = model["path"]
                model_name = model['name']

                # 세대 정보 불러오기
                generations = self.request_data(session, 'GET', f"{self.api_base}generations{path}/{model_path}")
                if not generations: continue

                for gen in generations.get("generations", []):
                    gen_key = gen["key"]
                    generation = gen['name']
                    
                    #Variants 데이터 불러오기
                    variant_data = self.request_data(session, 'POST', f"{self.api_base}variant-filters-3d{path}/{model_path}/{gen_key}", {"filter" : {}})
                    if not variant_data: continue

                    for var in variant_data.get('variants', []):
                        var_path = var['path']
                        var_params = var['params']
                        for p in range(len(var_params)):
                            params_dict[var_params[p][0]] = var_params[p][1][0]
                        
                        print(f"model = {model_name}, key = {params_dict.keys()}")
                            # print(params_dict["sales_rigion"])
                        # for param in range(len(var_params)):
                        #     # print(f"{var_params[param][0]} - {var_params[param][1][0]}")
                        #     parameter_names = var_params[param][0]
                        #     parameters = var_params[param][1][0]
                        #     print(f"{parameter_names} - {parameters}")
                        # 부품 분류 정보 불러오기
                        diagram_data = self.request_data(session, 'POST', f"{self.api_base}diagrams-new{path}/{var_path}", {"filter": {}})
                        if not diagram_data: continue

                        for group in diagram_data.get("diagrams", []):
                            for diagram in group:
                                uid = diagram.get("uid")

                                # 어셈블리 정보 불러오기
                                product_data = self.request_data(session, 'POST', f"{self.api_base}part-list{path}/{var_path}/{uid}", {"vin2": None})
                                if not product_data or "products" not in product_data:
                                    continue

                                parts = product_data.get('diagram', {}).get('baseName', "N/A")

                                cursor = connect.cursor()
                                for product in product_data.get('products', []):
                                    # print(product)
                                #     # ========== 정보 기록 ===========
                                #     # 1) 제조사
                                #     # 2) 차종
                                #     # 3) 세대
                                #     # 4) variant
                                #     # 5) uid
                                #     # 6) 부품 분류
                                #     # 7) ass'y 이름
                                #     # 8) 무게
                                #     # ==============================
                                    record =(
                                        manufacturer, model_name, generation, var_path,
                                        uid, parts, product.get('name'), product.get('weight')
                                    )
                                #     # ======== 데이터베이스 테이블 작성 ========
                                #     # 1) ID (1씩 증가)
                                #     # 2) manufacturer (제조사)
                                #     # 3) model_name (차종)
                                #     # 4) generation (세대)
                                #     # 5) variant_path (판매 지역, 핸들 위치(좌/우) 등)
                                #     # 6) 각 부품 정보 (diagram_uid)
                                #     # 7) assy_name (부품 어셈블리 정보)
                                #     # 8) part_name (부품 이름)
                                #     # 9) weight (무게)
                                #     # ====================================
                                    cursor.execute('''INSERT OR IGNORE INTO part_details
                                                   (manufacturer, model_name, generation, variant_path, diagram_uid, assy_name, part_name, weight)
                                                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', record)
                                    
                                connect.commit()
                                print(f"[저장 완료] {manufacturer} - {model_path} - {gen_key} : {parts} | part_name = {product.get('name')}, weight = {product.get('weight')}")

        except Exception as e:
            print(f"[에러 발생] {manufacturer} 처리 중 오류 : {e}")
        
        finally:
            connect.close()
            session.close()
            print(f"[완료] 수집 완료! {manufacturer}")
    def run(self, manufacturer):
        print(f'총 {len(manufacturer)} 개 사 데이터 수집 시작 (Thread : {self.max_workers})')

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            executor.map(self.crawling, manufacturer)
def main():
    manufacturer = [
        "/car/toyota", "/car/lexus", "/car/kia", "/car/hyundai", 
        "/car/nissan", "/car/mazda", "/car/mitsubishi", "/car/honda", "/car/mercedes"
    ]
    crawler = Crawling(max_workers=10)
    crawler.run(manufacturer)

if __name__ == "__main__":
    main()

        