# Justfile Guide

이 문서는 프로젝트 루트의 `justfile` 사용 방법을 안내합니다.

## 목적

`justfile`은 자주 사용하는 로컬 명령을 짧고 일관된 이름으로 실행하기 위해
사용합니다.

## 사용 전 준비

`just`가 설치되어 있는지 확인합니다.

```sh
just --version
```

설치되어 있지 않다면 환경 설정 문서의 `just` 설치 안내를 따릅니다.

- [환경 설정](./setup.md)

## 명령 목록 확인

프로젝트 루트에서 아래 명령을 실행합니다.

```sh
just
```

또는 명시적으로 아래 명령을 사용할 수 있습니다.

```sh
just --list
```

## 제공 명령

### `just install-hooks`

로컬 Git hook을 등록합니다.

```sh
just install-hooks
```

내부 실행 명령:

```sh
pre-commit install
```

### `just check`

Git이 추적 중인 전체 파일을 대상으로 pre-commit 검증을 실행합니다.

```sh
just check
```

내부 실행 명령:

```sh
pre-commit run --all-files
```

### `just check-worktree`

초기 커밋 전처럼 아직 Git이 추적하지 않는 파일까지 포함해 검증합니다.

```sh
just check-worktree
```

내부 실행 명령:

```sh
git ls-files --cached --others --exclude-standard | xargs pre-commit run --files
```

### `just status`

현재 Git 작업 상태를 짧게 확인합니다.

```sh
just status
```

내부 실행 명령:

```sh
git status --short
```

## 사용 기준

- 일반 작업 중에는 `just check`를 사용합니다.
- 초기 커밋 전에는 `just check-worktree`를 사용합니다.
- 커밋 훅을 처음 등록할 때는 `just install-hooks`를 사용합니다.
