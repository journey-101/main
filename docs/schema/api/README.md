# API 계약 문서

변경일: 2026-08-12

FE 개발자는 개별 계약을 보기 전에
[FE API 연동 가이드](./frontend-integration.md)의 인증 범위와 `user_id` 제거 사항을
확인한다.

## 바로가기

- [Authentication API](./auth.md)
- [Directions API](./directions.md)
- [FE API 연동 가이드](./frontend-integration.md)
- [Health API](./health.md)
- [Places API](./places.md)
- [Recommendations API](./recommendations.md)
- [Trips API](./trips.md)

## 디렉토리 목적

이 디렉토리는 backend router가 제공하는 API 계약을 도메인별로 정리한다. 각 문서는 현재 코드베이스의 request, response, status code, validation 규칙을 기준으로 작성한다.

이 디렉토리의 문서가 API 외부 경계의 최신 기준이다. `docs/flows/`의 주차별
문서는 과거 개발 기록이므로 서로 다를 경우 이 문서를 우선한다.

## 작성 방법

- 파일은 router 도메인 단위로 나눈다.
- 기본 경로, 엔드포인트, 요청 body, 응답 `data`, 주요 에러 동작을 포함한다.
- 성공 응답은 실제 공통 wrapper인 `{ "success": true, "data": ... }` 형태를 기준으로 쓴다.
- 검증 규칙은 schema와 service에서 확인한 현재 동작만 기록한다.
- 코드 블록과 API 필드명은 원문 표기를 유지하고, 설명 문장은 한국어로 작성한다.
