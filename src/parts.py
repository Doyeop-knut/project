import requests
import json
import sqlite3
import time
import concurrent.futures

class YoshiCrawler:
    def __init__(self, max_workers=5):
        self.api_base = "https://api.yoshiparts.com/"
        self.db_name = "yoshi_parts.db"
        self.max_workers = max_workers
        self._create_table()

    def _create_table(self):
        """테이블 생성은 메인 쓰레드에서 한 번만 수행"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
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
        conn.commit()
        conn.close()

    def request_api(self, session, method, url, data=None):
        """쓰레드별로 할당된 세션을 사용하여 요청"""
        try:
            if method == 'GET':
                resp = session.get(url, timeout=10)
            else:
                resp = session.post(url, json=data, timeout=10)
            
            if resp.status_code == 404:
                return None
            
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            # 에러 발생 시 로그만 찍고 None 반환하여 흐름 유지
            # print(f"Error requesting {url}: {e}")
            return None

    def crawl_brand(self, brand_path):
        """브랜드 단위의 워커 함수 (하나의 쓰레드가 담당)"""
        brand_name = brand_path.replace('/car/', '')
        print(f"\n[시작] 브랜드 수집: {brand_name}")
        
        # 1. 쓰레드별 독립적인 세션과 DB 연결 생성 (중요)
        session = requests.Session()
        session.headers.update({
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36...',
            'referer': 'https://yoshiparts.com/'
        })
        
        # timeout을 넉넉히 주어 'database is locked' 에러 방지
        conn = sqlite3.connect(self.db_name, timeout=60)
        
        try:
            # Models
            models_data = self.request_api(session, 'GET', f"{self.api_base}models{brand_path}")
            if not models_data: return

            for model in models_data.get("models", []):
                model_path = model["path"]
                
                # Generations
                gen_data = self.request_api(session, 'GET', f"{self.api_base}generations{brand_path}/{model_path}")
                if not gen_data: continue

                for gen in gen_data.get("generations", []):
                    gen_key = gen["key"]

                    # Variants
                    variant_url = f"{self.api_base}variant-filters-3d{brand_path}/{model_path}/{gen_key}"
                    v_data = self.request_api(session, 'POST', variant_url, {"filter": {}})
                    if not v_data: continue

                    for variant in v_data.get('variants', []):
                        v_path = variant['path']

                        # Diagrams
                        diagram_url = f"{self.api_base}diagrams-new{brand_path}/{v_path}"
                        d_data = self.request_api(session, 'POST', diagram_url, {"filter": {}})
                        if not d_data: continue

                        for group in d_data.get("diagrams", []):
                            for diagram in group:
                                uid = diagram.get("uid")
                                
                                # Final Part List
                                product_url = f"{self.api_base}part-list{brand_path}/{v_path}/{uid}"
                                p_data = self.request_api(session, 'POST', product_url, {"vin2": None})
                                
                                if not p_data or "products" not in p_data:
                                    continue

                                base_name = p_data.get("diagram", {}).get("baseName", "N/A")
                                
                                # DB 저장 (쓰레드 내부에서 직접 수행)
                                cursor = conn.cursor()
                                for product in p_data.get("products", []):
                                    record = (
                                        brand_name, model_path, gen_key, v_path, 
                                        uid, base_name, product.get("name"), product.get("weight")
                                    )
                                    cursor.execute('''INSERT OR IGNORE INTO part_details 
                                       (brand, model, generation, variant_path, diagram_uid, base_name, part_name, weight)
                                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', record)
                                
                                # 배치 단위로 커밋하여 성능 향상
                                conn.commit()
                                print(f"[저장완료] {brand_name}-{model_path}: {base_name}")

        except Exception as e:
            print(f"[에러] {brand_name} 처리 중 오류: {e}")
        finally:
            conn.close()
            session.close()
            print(f"[완료] 브랜드 수집 종료: {brand_name}")

    def run(self, brands):
        """멀티쓰레드 실행"""
        print(f"총 {len(brands)}개 브랜드 수집 시작 (쓰레드 개수: {self.max_workers})")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 각 브랜드 경로를 워커 함수(crawl_brand)에 전달
            executor.map(self.crawl_brand, brands)

def main():
    brands = [
        "/car/toyota", "/car/lexus", "/car/kia", "/car/hyundai", 
        "/car/nissan", "/car/mazda", "/car/mitsubishi", "/car/honda", "/car/mercedes"
    ]
    # 동시에 5개의 브랜드씩 처리
    crawler = YoshiCrawler(max_workers=5)
    crawler.run(brands)

if __name__ == '__main__':
    main()