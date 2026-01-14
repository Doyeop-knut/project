from fastapi import FastAPI, Request, Query
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import sqlite3
from typing import Optional

app = FastAPI()

# 템플릿 설정
templates = Jinja2Templates(directory="templates")
DB_NAME = "part_data.db"

def get_db_rows(manufacturer: str = None, part_name: str = None):
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # 컬럼명으로 접근 가능하게 설정
    cursor = conn.cursor()
    
    query = "SELECT * FROM part_details WHERE 1=1"
    params = []
    
    if manufacturer:
        query += " AND manufacturer LIKE ?"
        params.append(f"%{manufacturer}%")
    if part_name:
        query += " AND part_name LIKE ?"
        params.append(f"%{part_name}%")
    
    query += " ORDER BY id DESC LIMIT 200" # 최신 데이터 200개만 출력
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()
    return rows

@app.get("/view", response_class=HTMLResponse)
async def read_dashboard(
    request: Request, 
    manufacturer: Optional[str] = None, 
    part_name: Optional[str] = None
):
    # DB에서 데이터 가져오기
    rows = get_db_rows(manufacturer, part_name)
    
    # HTML 템플릿 렌더링
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "rows": rows,
        "manufacturer": manufacturer,
        "part_name": part_name
    })

if __name__ == "__main__":
    import uvicorn
    # 서버 실행 (자동 재시작 모드)
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)