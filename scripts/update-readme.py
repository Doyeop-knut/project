import os
from git import Repo

# 설정 및 경로 (update-readme.py의 구조 활용)
title_project = "# 웹 크롤링 프로젝트"
sub_project = "### 📜 전체 커밋 히스토리"
repo_path = '../'
readme_path = "../README.md"

def get_all_commits(path):
    """모든 브랜치의 모든 커밋 이력을 가져옵니다."""
    try:
        repo = Repo(path)
        # test_commit.py 처럼 all=True를 사용하여 모든 커밋을 가져옵니다
        commits = list(repo.iter_commits(all=True))
        return commits
    except Exception as e:
        print(f"Git 저장소 로드 실패: {e}")
        return []

def make_full_commit_table(commits):
    """모든 커밋을 표 형식으로 만들고, 접기 기능을 추가합니다."""
    # 내용이 너무 길어질 수 있으므로 <details> 태그를 사용합니다.
    header = "<details>\n<summary>클릭하여 전체 커밋 내역 보기 (총 {}개)</summary>\n\n".format(len(commits))
    header += "| # | 날짜 | 작성자 | 메시지 |\n"
    header += "|---|---|---|---|\n"
    
    body = ""
    for i, commit in enumerate(commits):
        date_str = commit.authored_datetime.strftime('%Y-%m-%d %H:%M')
        # 표 내부 줄바꿈 방지 및 메시지 정리
        msg = commit.message.strip().replace('\n', ' ')
        body += f"| {len(commits) - i} | {date_str} | {commit.author.name} | {msg} |\n"
    
    footer = "\n</details>"
    return header + body + footer

def update_readme():
    commits = get_all_commits(repo_path)
    
    if not commits:
        return

    content = make_full_commit_table(commits)
    
    # README.md 파일 작성
    try:
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(title_project + "\n\n")
            f.write(sub_project + "\n\n")
            f.write(content + "\n\n")
            f.write(f"---\n*최종 갱신일: {commits[0].authored_datetime.strftime('%Y-%m-%d %H:%M:%S')}*")
        print(f"총 {len(commits)}개의 커밋 내역이 README에 반영되었습니다.")
    except Exception as e:
        print(f"파일 작성 중 오류: {e}")

if __name__ == "__main__":
    update_readme()