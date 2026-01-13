import requests
import json
import sqlite3
import time

class YoshiCrawler:
    def __init__(self):
        self.api_base = "https://api.yoshiparts.com/"
        self.session = requests.Session()
        self.session.headers.update({
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36...',
            'referer': 'https://yoshiparts.com/'
        })
        self.conn = sqlite3.connect("yoshi_parts.db")
        self._create_table()

    def _create_table(self):
        """데이터베이스 테이블 초기화"""
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS part_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                brand TEXT,
                model TEXT,
                generation TEXT,
                variant_path TEXT,
                diagram_uid TEXT,
                base_name TEXT,
                part_name TEXT,
                weight TEXT,
                UNIQUE(variant_path, diagram_uid, part_name)
            )
        ''')
        self.conn.commit()

    def request_api(self, method, url, data=None):
        """공통 요청 함수 (에러 핸들링 및 재시도 로직 추가 가능)"""
        try:
            if method == 'GET':
                resp = self.session.get(url)
            else:
                resp = self.session.post(url, json=data)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            print(f"Error requesting {url}: {e}")
            return None

    def save_to_db(self, data_tuple):
        """DB에 즉시 저장"""
        cursor = self.conn.cursor()
        query = '''INSERT OR IGNORE INTO part_details 
                   (brand, model, generation, variant_path, diagram_uid, base_name, part_name, weight)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)'''
        cursor.execute(query, data_tuple)
        self.conn.commit()

    def run(self, brands):
        for brand_path in brands:
            brand_name = brand_path.replace('/car/', '')
            print(f"\n>>> 수집 시작: {brand_name}")

            # 1. Models
            models_data = self.request_api('GET', f"{self.api_base}models{brand_path}")
            if not models_data: continue

            for model in models_data.get("models", []):
                model_path = model["path"]
                
                # 2. Generations
                gen_data = self.request_api('GET', f"{self.api_base}generations{brand_path}/{model_path}")
                if not gen_data: continue

                for gen in gen_data.get("generations", []):
                    gen_key = gen["key"]

                    # 3. Variants (POST)
                    variant_url = f"{self.api_base}variant-filters-3d{brand_path}/{model_path}/{gen_key}"
                    v_data = self.request_api('POST', variant_url, {"filter": {}})
                    if not v_data: continue

                    for variant in v_data.get('variants', []):
                        v_path = variant['path']

                        # 4. Diagrams (UID)
                        diagram_url = f"{self.api_base}diagrams-new{brand_path}/{v_path}"
                        d_data = self.request_api('POST', diagram_url, {"filter": {}})
                        if not d_data: continue

                        for group in d_data.get("diagrams", []):
                            for diagram in group:
                                uid = diagram.get("uid")
                                
                                # 5. Final Part List
                                product_url = f"{self.api_base}part-list{brand_path}/{v_path}/{uid}"
                                p_data = self.request_api('POST', product_url, {"vin2": None})
                                if not p_data: continue

                                base_name = p_data.get("diagram", {}).get("baseName", "N/A")
                                for product in p_data.get("products", []):
                                    # DB 저장용 튜플 생성
                                    record = (
                                        brand_name, model_path, gen_key, v_path, 
                                        uid, base_name, product.get("name"), product.get("weight")
                                    )
                                    self.save_to_db(record)
                                    print(f"[저장완료] {brand_name}-{model_path}: {product.get('name')}")

def main():
    brands = ["/car/toyota", "/car/lexus", "/car/kia"] # 원하는 브랜드 리스트
    crawler = YoshiCrawler()
    crawler.run(brands)

if __name__ == '__main__':
    main()