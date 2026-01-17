from fastapi import FastAPI, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import sqlite3
from typing import Optional

# 웹 서버
app = FastAPI()
# 템플릿 보관 폴더 설정
templates = Jinja2Templates(directory="templates")
# 조회 대상 db
DB_NAME = "part_data.db"

# 데이터 조회
def get_db_rows(page : int, limit : int, manufacturer: str = None, part_name: str = None, model_name: str = None, generation : str = None):
    conn = sqlite3.connect(DB_NAME) # 데이터베이스에 연결
    conn.row_factory = sqlite3.Row  # 컬럼명으로 접근
    cursor = conn.cursor()

    # 개수 조회 및 데이터 조회 공통 사용
    where = " WHERE 1=1"
    # query = "SELECT * FROM part_details WHERE 1=1" #기본 쿼리
    params = []
    # 동적 쿼리 (검색창)
    if manufacturer and manufacturer != "전체":
        # query += " AND manufacturer LIKE ?"
        where += " AND manufacturer LIKE ?"
        params.append(manufacturer)
    if model_name and model_name != "전체":
        where += " AND model_name LIKE ?"
        params.append(model_name)

    if generation and generation != "전체":
        where += " AND generation LIKE ?"
        params.append(generation)
        
    if part_name:
        where += " AND part_name LIKE ?"
        params.append(f"%{part_name}%")

    # 데이터 전체 조회

    cursor.execute("SELECT DISTINCT manufacturer FROM part_details WHERE manufacturer IS NOT NULL ORDER BY manufacturer")
    brand_list = [row[0] for row in cursor.fetchall()]

    model_where = " WHERE 1=1"
    model_params = []
    if manufacturer and manufacturer != "전체":
        model_where += " And manufacturer LIKE ?"
        model_params.append(manufacturer)

    cursor.execute(f"SELECT DISTINCT model_name FROM part_details{model_where} AND model_name IS NOT NULL ORDER BY model_name", model_params)
    model_list = [row[0] for row in cursor.fetchall()]

    gen_where = " WHERE 1=1"
    gen_params = []
    if model_name and model_name != "전체":
        gen_where += " AND model_name LIKE ?"
        # gen_params.append(f"%{model_name}%")
        gen_params.append(model_name)
    elif manufacturer and manufacturer != "전체":
        gen_where += " AND manufacturer LIKE ?"
        gen_params.append(manufacturer)

    cursor.execute(f"SELECT DISTINCT generation FROM part_details{gen_where} AND generation IS NOT NULL ORDER BY generation", gen_params)
    gen_list = [row[0] for row in cursor.fetchall()]

    cursor.execute(f"SELECT COUNT(*) FROM part_details{where}", params)
    total_count = cursor.fetchone()[0]

    offset = (page -1) * limit
    query = f"SELECT * FROM part_details{where} ORDER BY id DESC LIMIT ? OFFSET ?"
    cursor.execute(query, params + [limit, offset])
    # cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows, total_count, gen_list, brand_list, model_list

# /view 입력 시 실행되는 함수
@app.get("/view", response_class=HTMLResponse)
async def read_dashboard(
    request: Request, 
    #사용자가 검색어를 입력하지 안항도 에러 없이 작동
    page : int = Query(1, ge = 1), # 기본값 1페이지, 최소값 1
    manufacturer: Optional[str] = None,
    part_name: Optional[str] = None,
    model_name: Optional[str] = None,
    generation: Optional[str] = None
):
    def clean_param(p):
        return p if p and p != "전체" else None

    manufacturer = clean_param(manufacturer)
    part_name = clean_param(part_name)
    model_name = clean_param(model_name)
    generation = clean_param(generation)
    # 페이지 당 20개 고정
    limits = 20
    # DB에서 데이터 가져오기
    rows, total_count, gen_list, brand_list, model_list = get_db_rows(page, limits, manufacturer, part_name, model_name, generation)
    # rows = get_db_rows(manufacturer, part_name, model_name)
    import math
    total_pages = math.ceil(total_count / limits)
    # 수집된 row 데이터와 사용자 요청 정보를 index.html에 통째로 넘겨줌.
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "rows": rows,
        "page": page,
        "total_pages" : total_pages,
        "total_count" : total_count,
        "gen_list": gen_list,
        "generation": generation,
        "manufacturer": manufacturer,
        "manufacturer_list": brand_list,
        "part_name": part_name,
        "model_name": model_name,
        "model_list" : model_list
    })

if __name__ == "__main__":
    import uvicorn
    # 서버 실행 (자동 재시작 모드)
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)