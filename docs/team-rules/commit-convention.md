# Commit Convention

이 문서는 프로젝트 전반에서 사용하는 커밋 메시지 규칙을 정의합니다.
모든 커밋은 아래 규칙을 따르는 것을 원칙으로 합니다.

---

## 0. 3줄 요약

- 커밋메시지는 작업의 의미단위별로 나눠서 7개 타입중에 할당하고, 상세 내용은 소문자로 기록하기
- 브랜치에 첫 커밋은 작업내용 없는 빈 커밋 `git commit --allow-empty -m "chore: introduce {branch-name} branch"`
- 개인 브랜치에서는 과거 커밋 수정 자유, 공유 브랜치에서는 절대 안됨

---

## 1. 기본 형식

```text
<type>: <summary>
```

- 한 줄로 작성합니다.
- 영어를 사용합니다.
- summary는 변경 내용을 간결하게 설명합니다.
- 마침표(`.`)는 사용하지 않습니다.

---

## 2. 사용 가능한 타입

아래 타입만 사용합니다.

- **feat**: 새로운 기능 추가 (로직 추가)
- **fix**: 버그 수정
- **refactor**: 기능 변경 없는 코드 구조 개선 (로직이 변경 될 수 있으나 입출력 동일)
- **docs**: 문서 추가 또는 수정
- **test**: 테스트 코드 추가 또는 수정
- **chore**: 설정, 규칙, 도구, 브랜치 시작, 기타 잡일
- **ops**: DevOps, 배포, 인프라 관련 작업

> 브랜치, 설정 관련 작업은 `chore`를, 배포/인프라 관련 작업은 `ops`를 사용합니다.

---

## 3. 예시

```text
chore: add initial collaboration rules
docs: add environment setup guide
feat: implement rule graph builder
fix: handle empty scenario input
```

---

## 4. 권장 규칙

- 한 커밋은 하나의 논리적인 변경만 포함합니다.
- 서로 다른 목적의 변경은 커밋을 분리합니다.
- 의미 없는 커밋 메시지는 지양합니다.

---

## 5. 금지 사항

아래와 같은 메시지는 사용하지 않습니다.

```text
init
update
fix bug
작업함
```

> 위와 같은 메시지는 변경 내용을 추적하기 어렵게 만듭니다.

---

## 6. 브랜치 시작 커밋

브랜치의 첫 커밋은 반드시 아래 메시지 형식의 빈 커밋으로 생성합니다.
`{branch-name}`에는 실제 브랜치 이름을 넣습니다.

```text
chore: introduce {branch-name} branch
```

```sh
git commit --allow-empty -m "chore: introduce {branch-name} branch"
```

## 7. 히스토리 수정(리라이트) 원칙

- 원격(공유) 브랜치(`main`, `dev`)에서는 rebase, force push 등 히스토리 수정을 하지 않습니다.
- 실수한 커밋은 새로운 커밋으로 수정하거나, PR에서 정리(squash)합니다.
- 예외: 개인 작업 브랜치에서는  rebase, force push 사용 가능합니다.

---
