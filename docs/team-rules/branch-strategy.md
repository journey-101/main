# 브랜치 전략 (Branching Strategy)

이 문서는 프로젝트 전반에서 사용하는 브랜치 명명법과 작업 흐름의 핵심 규칙을 정의합니다.

---

## 0. 3줄 요약

- 작업 단위는 **이슈**이며, 모든 브랜치는 이슈를 기반으로 생성합니다.
- 브랜치는 `feat`, `fix`, `docs` 등 **7가지 작업 브랜치**와 예외적인 **`hotfix` 브랜치**로 나뉩니다.
- `dev` 브랜치를 중심으로 작업을 통합하며, `main` 브랜치는 안정 버전으로 관리합니다.

```text
# Merge Flow (병합 흐름)
main   <-[ PR | Squash ]-   dev   <--[ PR | Merge ]--   작업 브랜치: ex)feat/{issue-number}-*

# Sync Flow (동기화 흐름)
main   --[ PR | Merge ]->   dev   --[ local merge ]->   작업 브랜치: ex)feat/{issue-number}-*

# Hotfix Flow
main   <-[ PR | Squash ]-------------- hotfix
  └-----[ PR | Merge ]-->   dev
```

---

## 1. 핵심 원칙

- **이슈 기반 개발**: 모든 브랜치는 특정 이슈를 해결하기 위해 생성합니다. 브랜치 이름에는 반드시 해당 **이슈 번호**가 포함되어야 합니다.
- **1 브랜치, 1인 담당**: 하나의 작업 브랜치는 한 사람이 담당하여 작업하는 것을 원칙으로 합니다. (공동 작업 시에는 `-co` 접미사를 사용)
- **`dev` 브랜치 중심**: 모든 작업 브랜치는 `dev`에서 시작하여 `dev`로 병합하는 것을 원칙으로 합니다. (`hotfix` 제외)
- **빈 커밋으로 시작**: 모든 작업 브랜치의 첫 커밋은 작업 내용 없는 빈 커밋이어야 합니다.
- **PR 기반 병합**: `main`, `dev` 브랜치에는 직접 커밋하지 않으며, 모든 변경사항은 Pull Request(PR)를 통해서만 병합합니다.

---

## 2. 브랜치 종류

### 2.1. 기본 브랜치

- **main**: 항상 배포 가능한 가장 안정적인 상태의 브랜치입니다. `dev` 브랜치의 내용이 충분히 검증된 후, 버전 단위로 병합됩니다.
- **dev**: 개발된 기능들이 통합되고 검증되는 브랜치입니다. 모든 작업 브랜치가 이곳으로 병합됩니다.

### 2.2. 작업 브랜치 (Working Branches)

작업 브랜치는 아래 7가지 타입으로 나뉩니다. 브랜치 타입은 커밋 메시지 타입과 동일합니다.

| 브랜치 타입 | 목적                     | 예시                              |
| :---------- | :----------------------- | :-------------------------------- |
| `feat`      | 새로운 기능 개발         | `feat/11-login-page`              |
| `fix`       | 버그 수정                | `fix/22-login-error`              |
| `docs`      | 문서 추가 및 수정        | `docs/31-update-readme`           |
| `refactor`  | 코드 리팩토링            | `refactor/45-simplify-user-model` |
| `test`      | 테스트 코드 추가 및 수정 | `test/52-add-login-test`          |
| `chore`     | 빌드, 설정 등 기타 잡일  | `chore/66-update-dependencies`    |
| `ops`       | DevOps, 인프라, 배포     | `ops/71-setup-cicd`               |

### 2.3. 예외 브랜치 (Exception Branch)

- **`hotfix/{issue-number}-{name}`**
  - **목적**: `main` 브랜치에서 발생한 치명적인 버그를 긴급하게 수정할 때만 사용합니다.
  - **분기 대상**: `main`
  - **병합 대상**: `main` 브랜치로 직접 PR 및 병합 후, 반드시 `dev` 브랜치에도 변경 내용을 동기화해야 합니다.
  - **예시**: `hotfix/23-critical-error`

---

## 3. 브랜치 시작 커밋

작업 브랜치를 만든 직후 첫 커밋은 반드시 아래 형식의 빈 커밋으로 생성합니다.

```sh
git commit --allow-empty -m "chore: introduce {branch-name} branch"
```

예시:

```sh
git commit --allow-empty -m "chore: introduce feat/11-login-page branch"
```

이 커밋은 브랜치 시작점을 명확히 남기기 위한 커밋이며, 실제 작업 변경 사항을 포함하지 않습니다.

---

## 4. 병합 규칙

- **`dev` 브랜치로 병합 시**: **Merge Commit** (`--no-ff`) 방식을 사용하여, 작업 히스토리를 모두 `dev`에 기록하는 것을 원칙으로 합니다.
- **`main` 브랜치로 병합 시**: **Squash and Merge** 방식을 사용하여, `dev`의 기능 개발 이력을 하나의 버전 커밋으로 묶어 `main`에 반영합니다.

---

## 5. 히스토리 관리

- `main`, `dev`와 같이 여러 사람이 함께 사용하는 공유 브랜치에서는 `rebase`나 `push --force` 등 히스토리를 변경하는 명령을 절대 사용하지 않습니다.
- 히스토리 관리는 개인의 작업 브랜치 내에서만 자유롭게 할 수 있습니다.
