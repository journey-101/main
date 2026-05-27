# Project GTRPGM – Environment Setup

- 이 문서는 협업 문서와 의사결정 기록을 관리하기 위한 로컬 개발 환경 설정 방법을 안내합니다.
- 본 레포지토리의 모든 변경 사항은 GitHub Flow를 기반으로 PR을 통해 반영됩니다.
- 문서 품질과 협업 흐름을 유지하기 위해 pre-commit과 act를 사용합니다.

---

## 개발 환경 (Development Environment)

본 프로젝트의 문서 작성 및 협업을 위해 사용하는 전역 개발 환경 및 도구입니다.
모든 팀원은 아래 환경을 기준으로 작업합니다.

| 구분            | 도구                         | 용도                          |
| --------------- | ---------------------------- | ----------------------------- |
| OS              | Linux (Ubuntu 22.04+) / WSL2 | 프로젝트 기준 개발 환경       |
| Runtime         | Python 3.11                  | 표준 실행 환경                |
| Version Control | Git                          | 소스 코드 및 문서 협업        |
| Package / Tool  | uv                           | Python 환경 및 개발 도구 관리 |
| Task Runner     | just                         | 반복 명령 실행 관리           |
| Lint            | Ruff                         | Python 코드 품질 검사         |
| Doc Lint        | Markdown Lint                | 문서 스타일 검사              |
| Git Hook        | pre-commit                   | 커밋 시 자동 검증             |
| Container       | Docker / Docker Compose      | 서비스 및 테스트 환경 (선택)  |
| IDE             | VS Code (권장)               | 개발 및 문서 작성             |

### 0. 운영체제 및 기본 환경 (Operating System)

본 프로젝트는 **Linux 환경**을 기준으로 개발 및 검증됩니다.  
Windows 사용자의 경우 **WSL2 사용을 권장**합니다.

- **권장 환경**
  - Linux (Ubuntu 22.04 LTS 이상)
  - Windows + WSL2 (Ubuntu 배포판 권장)

- **필수 기본 도구**
  - curl
  - git

> macOS 환경에서도 대부분의 도구를 사용할 수 있으나,
> 공식 지원 및 검증 환경은 Linux 기준이며,  
> 이하 명령어는 Ubuntu 환경을 기준으로 작성되었습니다.

### 1. 언어 및 런타임 (Language & Runtime)

- **Python**
  - 3.11.14 사용
  - 프로젝트 전반에서 사용하는 표준 런타임
  - 패키지 호환성을 고려하여 고정

### 2. 버전 관리 및 협업 (Version Control & Collaboration)

- **Git**
  - 소스 코드 및 문서의 버전 관리
  - GitHub Flow 기반 협업 진행

### 3. 패키지 및 도구 관리 (Package & Tool Management)

- **uv**
  - Python 버전, 가상환경, 개발 도구를 통합 관리
  - 프로젝트의 Python 관련 작업은 uv 사용을 기준으로 함
  - **설치:**

    ```sh
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

- **just**
  - 프로젝트 루트의 `justfile`에 정의된 반복 명령을 실행
  - 검증, 훅 등록 등 자주 사용하는 명령을 짧게 실행하기 위해 사용
  - **설치:**

    ```sh
    curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to ~/.local/bin
    ```

  - **명령 확인:**

    ```sh
    just
    ```

---

### 4. 코드 및 문서 품질 관리 (Linting & Formatting)

- **Ruff**
  - Python 코드의 문법 오류 및 스타일 검사
  - 일부 레포에서는 formatter로도 사용
  - **설치:**

    ```sh
    uv tool install ruff
    ```

- **Markdown Lint**
  - 문서 스타일 및 형식을 일관되게 유지하기 위한 린터
  - CI 및 pre-commit 훅을 통해 자동 실행됨

---

### 5. Git Hook 및 사전 검증 (Pre-commit Hooks)

- **Pre-commit**
  - 커밋 시점에 린트 및 검증 작업을 자동으로 실행
  - CI 이전에 문제를 발견하는 것을 목표로 사용
  - **설치:**

    ```sh
    uv tool install pre-commit
    ```

  - **등록:**
    - 프로젝트 루트에서 아래 실행

    ```sh
    pre-commit install
    ```

### 6. 컨테이너 환경 (Container Environment)

- **Docker / Docker Compose**
  - 일부 레포에서 서비스 실행 및 테스트 환경 통합에 사용
  - docs 레포에서는 필수 도구가 아님

## 설치 스크립트

신규 환경에서는 아래 명령을 순서대로 실행합니다.

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
curl --proto '=https' --tlsv1.2 -sSf https://just.systems/install.sh | bash -s -- --to ~/.local/bin

uv tool install ruff
uv tool install pre-commit

pre-commit install
```

## 변경 이력

| 날짜       | 변경 내용 | 이유 |
| ---------- | --------- | ---- |
| 2026-05-27 | 초안 작성 | -    |
