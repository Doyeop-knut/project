import os
from git import Repo

# 1. 설정 및 초기화
title_project = "# 웹 크롤링 프로젝트"
sub_project = "### 최신 커밋 내역 (자동 업데이트)"
repo_path = '../'  # test_commit.py 기준 경로
readme_path = "../README.md"

def get_commit_history(path, limit=10):
    """최신 커밋 이력을 리스트로 가져옵니다."""
    try:
        repo = Repo(path)
        # HEAD 브랜치의 최신 커밋부터 limit 개수만큼 가져옵니다.
        commits = list(repo.iter_commits(max_count=all))
        return commits
    except Exception as e:
        print(f"Git 저장소를 읽는 중 오류 발생: {e}")
        return []

def make_commit_table(commits):
    """커밋 객체 리스트를 마크다운 표 형식으로 변환합니다."""
    header = "| # | 날짜 | 작성자 | 커밋 메시지 |\n"
    header += "|---|---|---|---|\n"
    
    body = ""
    for i, commit in enumerate(commits):
        # 날짜 포맷 변경 (YYYY-MM-DD HH:MM)
        date_str = commit.authored_datetime.strftime('%Y-%m-%d %H:%M')
        # 메시지에서 줄바꿈 제거 (표 깨짐 방지)
        msg = commit.message.strip().replace('\n', ' ')
        author = commit.author.name
        
        body += f"| {i+1} | {date_str} | {author} | {msg} |\n"
    
    return header + body

def update_readme():
    # 2. 데이터 가져오기 (최신 10개 커밋)
    commits = get_commit_history(repo_path, limit=10)
    
    if not commits:
        print("작성된 커밋이 없습니다.")
        return

    # 3. 마크다운 내용 생성
    table_content = make_commit_table(commits)
    
    # 4. README.md 파일 쓰기
    try:
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(title_project + "\n\n")
            f.write(sub_project + "\n\n")
            f.write(table_content + "\n")
            f.write(f"\n*마지막 업데이트 일시: {commits[0].authored_datetime.strftime('%Y-%m-%d %H:%M:%S')}*")
        print(f"성공적으로 {readme_path}가 갱신되었습니다.")
    except Exception as e:
        print(f"파일 저장 중 오류 발생: {e}")

if __name__ == "__main__":
    update_readme()