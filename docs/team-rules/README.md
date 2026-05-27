# 신규 팀원 온보딩: 첫 PR까지

이 문서는 새 팀원이 로컬 환경을 준비하고, 이슈 기반으로 브랜치를 만든 뒤, 첫 Pull Request(PR)를 올릴 수 있도록 돕는 실행 가이드입니다.

팀 규칙의 상세 기준은 아래 문서를 참고합니다.

- [브랜치 전략](./branch-strategy.md)
- [커밋 컨벤션](./commit-convention.md)
- [PR 규칙](./pull-request-rules.md)
- [이슈 작성 가이드](./issue-guide.md)
- [CI 범위 안내](./ci-scope.md)

---

## 빠른 참조

| 단계         | 해야 할 일         | 핵심 규칙                                      | 예시                                   |
| :----------- | :----------------- | :--------------------------------------------- | :------------------------------------- |
| 최초 설정    | 도구 설치          | `uv`, `pre-commit` 설치 후 훅 등록             | `pre-commit install`                   |
| 이슈         | 작업 단위 확인     | `[타입] <내용 요약>`                           | `[Feat] 소셜 로그인 기능 추가`         |
| 브랜치       | 작업 브랜치 생성   | `타입/이슈번호-이름`, `dev`에서 분기           | `feat/11-new-login-page`               |
| 커밋         | 변경 사항 기록     | `타입: <summary>`, 영어, 마침표 없음           | `feat: add login page structure`       |
| PR 전 확인   | 로컬 검증          | 변경 범위, 커밋 메시지, 테스트, 이슈 링크 확인 | `pre-commit run --all-files`           |
| PR           | 리뷰 요청          | 대상은 `dev`, `hotfix`만 `main`                | `Closes #11`                           |
| 리뷰         | CI와 리뷰 대응     | CI 실패 상태에서는 리뷰 요청 금지              | 추가 커밋 후 `git push`                |
| 병합 후 정리 | 브랜치 삭제/동기화 | 셀프 머지 금지, 병합 후 `dev` 최신화           | `git branch -d feat/11-new-login-page` |

---

## 0. 처음 1회만 설정하기

프로젝트에 처음 참여했다면 작업을 시작하기 전에 아래를 먼저 확인합니다.

1. GitHub 저장소 접근 권한을 받습니다.
2. 저장소를 로컬에 clone합니다.
3. Git 사용자 정보를 설정합니다.
4. [환경 설정 문서](../setup.md)에 따라 `uv`와 `pre-commit`을 설치합니다.
5. 프로젝트 루트에서 pre-commit 훅을 등록합니다.

```sh
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"

uv tool install pre-commit
pre-commit install
```

로컬에 `dev` 브랜치가 있는지 확인하고 최신 상태로 맞춥니다.

```sh
git checkout dev
git pull origin dev
```

---

## 1. 작업 시작하기

모든 작업은 이슈에서 시작합니다.

- 이미 배정된 이슈가 있다면 내용을 읽고 작업 범위를 확인합니다.
- 이슈가 없다면 [이슈 작성 가이드](./issue-guide.md)에 따라 새 이슈를 만듭니다.
- 이슈 제목은 `[Feat]`, `[Fix]`, `[Docs]`, `[Refactor]`, `[Test]`, `[Chore]`, `[Ops]` 중 하나로 시작합니다.
- 담당자와 라벨을 지정해 작업 주체와 타입을 명확히 합니다.

---

## 2. 브랜치 만들기

일반 작업 브랜치는 항상 최신 `dev`에서 분기합니다. `hotfix`만 예외적으로 `main`에서 분기합니다.

```sh
git checkout dev
git pull origin dev
git checkout -b feat/11-new-login-page
```

브랜치를 만든 직후 첫 커밋은 반드시 작업 내용 없는 빈 커밋으로 시작합니다.

```sh
git commit --allow-empty -m "chore: introduce feat/11-new-login-page branch"
```

브랜치 이름은 아래 형식을 사용합니다.

```text
<type>/<issue-number>-<short-name>
```

예시:

```text
feat/11-new-login-page
fix/22-login-error
docs/31-update-onboarding
```

브랜치 타입과 병합 규칙의 상세 기준은 [브랜치 전략](./branch-strategy.md)을 따릅니다.

---

## 3. 개발하고 커밋하기

작업 중에는 변경 범위를 자주 확인합니다.

```sh
git status
git diff
```

브랜치 시작 커밋 이후, 변경이 완료되면 필요한 파일만 stage하고 커밋합니다.

```sh
git add <file>
git commit -m "feat: add user login form"
```

커밋 메시지는 아래 형식을 사용합니다.

```text
<type>: <summary>
```

- `type`은 `feat`, `fix`, `docs`, `refactor`, `test`, `chore`, `ops` 중 하나입니다.
- `summary`는 영어로 작성합니다.
- 문장 끝에 마침표를 붙이지 않습니다.

pre-commit이 실패하면서 파일을 자동 수정했다면 수정된 파일을 다시 stage한 뒤 커밋합니다.

```sh
git status
git add <fixed-file>
git commit -m "feat: add user login form"
```

상세 규칙은 [커밋 컨벤션](./commit-convention.md)을 따릅니다.

---

## 4. PR 올리기 전 확인하기

PR을 만들기 전에 아래를 확인합니다.

- 작업 브랜치가 최신 `dev` 기준인지 확인합니다.
- 의도하지 않은 파일이 포함되지 않았는지 `git status`와 `git diff`로 확인합니다.
- 커밋 메시지가 컨벤션을 따르는지 확인합니다.
- 로컬 검증을 실행합니다.
- PR 본문에 연결할 이슈 번호를 준비합니다.

가능하면 아래 검증을 먼저 실행합니다.

```sh
pre-commit run --all-files
```

프로젝트에 테스트나 린트 명령이 제공된다면 함께 실행합니다.

```sh
uv run pytest tests
ruff check .
```

레포에 해당 도구나 테스트 설정이 없다면 PR 본문에 실행하지 못한 이유를 적습니다.

---

## 5. PR 만들기

작업 브랜치를 원격 저장소에 push합니다.

```sh
git push origin feat/11-new-login-page
```

GitHub에서 PR을 생성합니다.

- 일반 작업 브랜치의 대상은 `dev`입니다.
- `hotfix/*` 브랜치의 대상만 `main`입니다.
- PR 제목은 커밋 메시지와 같은 형식인 `<type>: <summary>`를 사용합니다.
- PR 본문에는 변경 목적, 주요 변경 사항, 검증 결과를 적습니다.
- 관련 이슈는 본문 마지막 줄에 `Closes #11` 또는 `Fixes #22` 형식으로 연결합니다.

상세 기준은 [PR 규칙](./pull-request-rules.md)을 따릅니다.

---

## 6. 리뷰와 CI 대응하기

PR을 만들면 CI가 실행됩니다.

- CI가 실패한 상태에서는 리뷰를 요청하지 않습니다.
- 실패 로그를 확인하고 수정 커밋을 추가한 뒤 다시 push합니다.
- 리뷰 코멘트를 반영할 때도 같은 브랜치에 추가 커밋을 쌓고 push합니다.
- 리뷰어가 변경 의도를 이해할 수 있도록 필요한 설명을 PR 코멘트에 남깁니다.

```sh
git add <file>
git commit -m "fix: handle empty login response"
git push origin feat/11-new-login-page
```

CI가 언제 무엇을 확인하는지는 [CI 범위 안내](./ci-scope.md)를 참고합니다.

---

## 7. 병합 후 정리하기

PR이 승인되면 지정된 리뷰어 또는 maintainer가 병합합니다. PR 작성자는 기본적으로 직접 병합하지 않습니다.

병합 후에는 로컬 `dev`를 최신화합니다.

```sh
git checkout dev
git pull origin dev
```

완료된 작업 브랜치를 삭제합니다.

```sh
git branch -d feat/11-new-login-page
git push origin --delete feat/11-new-login-page
```

진행 중인 다른 브랜치가 있다면 최신 `dev`를 반영합니다.

```sh
git checkout fix/22-login-error
git merge dev
```

---

## 자주 막히는 상황

### pre-commit이 파일을 수정한 경우

pre-commit은 일부 형식 문제를 자동으로 고칠 수 있습니다. 이때 커밋은 중단되므로 수정된 파일을 다시 stage하고 커밋합니다.

```sh
git status
git add <fixed-file>
git commit -m "docs: update onboarding guide"
```

### 잘못된 브랜치에서 작업한 경우

아직 커밋하지 않았다면 새 브랜치를 만들고 작업을 이어갑니다.

```sh
git checkout -b feat/11-new-login-page
```

이미 커밋했다면 팀원에게 상황을 공유한 뒤 브랜치 이동 또는 cherry-pick 방식으로 정리합니다.

### 충돌이 난 경우

`dev`를 병합하는 과정에서 conflict가 나면 충돌 파일을 수정한 뒤 다시 커밋합니다.

```sh
git status
git add <resolved-file>
git commit
```

### CI가 실패한 경우

실패 로그에서 어떤 검증이 깨졌는지 먼저 확인합니다. 수정 후 추가 커밋을 push하면 같은 PR에서 CI가 다시 실행됩니다.

---

## 상세 규칙 문서

이 README는 첫 PR까지의 실행 흐름을 다룹니다. 세부 정책은 아래 문서를 기준으로 판단합니다.

- [브랜치 전략](./branch-strategy.md)
- [커밋 컨벤션](./commit-convention.md)
- [PR 규칙](./pull-request-rules.md)
- [이슈 작성 가이드](./issue-guide.md)
- [CI 범위 안내](./ci-scope.md)
