from git import Repo

# 현재 디렉토리를 Git 저장소로 가정합니다.
# 특정 저장소 경로를 지정할 수도 있습니다 (예: 'C:/Users/YourUser/YourRepo')
repo_path = '../'
repo = Repo(repo_path)

# 모든 브랜치의 커밋을 포함하여 커밋 이력을 반복합니다.
# 기본적으로 HEAD에서 도달 가능한 커밋만 가져오려면 `all_branches=False`로 설정하거나 생략합니다.
commits = list(repo.iter_commits(all=True))

print(f"총 커밋 수: {len(commits)}")

for commit in commits:
    print("-" * 20)
    print(f"작성자: {commit.author.name}")
    print(f"날짜: {commit.authored_datetime}")
    print(f"커밋 메시지:\n{commit.message.strip()}") # .strip()으로 공백 제거
