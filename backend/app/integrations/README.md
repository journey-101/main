# Integrations

외부 API client는 이 디렉터리 아래에 둔다.

예상 위치:

- `kakao/client.py`
- `bucheon/client.py`

Domain service는 외부 API 호출 세부 구현을 직접 포함하지 않고,
필요한 client를 이 영역에서 가져와 사용한다.
