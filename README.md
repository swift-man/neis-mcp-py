# NEIS MCP Server

나이스 교육정보 개방 포털의 Open API 12종을 MCP Streamable HTTP 방식으로 제공하는 Python/FastAPI 서버입니다.

## 제공 도구

- `get_school_info`: 학교기본정보 (`schoolInfo`)
- `get_meal_service_diet_info`: 급식식단정보 (`mealServiceDietInfo`)
- `get_academy_instruction_info`: 학원교습소정보 (`acaInsTiInfo`)
- `get_high_school_timetable`: 고등학교시간표 (`hisTimetable`)
- `get_school_schedule`: 학사일정 (`SchoolSchedule`)
- `get_middle_school_timetable`: 중학교시간표 (`misTimetable`)
- `get_elementary_school_timetable`: 초등학교시간표 (`elsTimetable`)
- `get_class_info`: 학급정보 (`classInfo`)
- `get_school_major_info`: 학교학과정보 (`schoolMajorinfo`)
- `get_school_affiliation_info`: 학교계열정보 (`schulAflcoinfo`)
- `get_special_school_timetable`: 특수학교시간표 (`spsTimetable`)
- `get_timetable_classroom_info`: 시간표강의실정보 (`tiClrminfo`)
- `list_neis_open_apis`: 서버가 제공하는 API 메타데이터 조회

## 실행

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

인증키가 있으면 환경 변수로 설정합니다. 인증키가 없으면 NEIS 샘플 응답 제한에 따라 일부 데이터만 조회됩니다.

```bash
export NEIS_API_KEY="발급받은_인증키"
uvicorn neis_mcp.server:app --host 127.0.0.1 --port 8000
```

MCP 클라이언트에서는 아래 URL로 연결합니다.

```text
http://127.0.0.1:8000/mcp
```

## Linux 원격 배포

다른 PC에서 Linux 서버의 MCP 서버에 접속하려면 서버를 `0.0.0.0`에 바인딩하고, 방화벽에서 포트를 열어야 합니다. 외부 접속을 허용하는 경우 `MCP_AUTH_TOKEN` 설정을 권장합니다.

```bash
cp .env.example .env
```

`.env` 예시는 다음과 같습니다.

```env
NEIS_API_KEY=발급받은_인증키
MCP_AUTH_TOKEN=충분히_긴_랜덤_토큰
MCP_HOST=0.0.0.0
MCP_PORT=8000
ALLOWED_ORIGINS=http://클라이언트PC_IP:3000,http://localhost
ALLOWED_ORIGIN_REGEX=
```

서버 실행:

```bash
source .venv/bin/activate
python -m neis_mcp
```

또는 직접 실행:

```bash
uvicorn neis_mcp.server:app --host 0.0.0.0 --port 8000
```

Ubuntu 방화벽을 사용하는 경우:

```bash
sudo ufw allow 8000/tcp
```

다른 PC의 MCP 클라이언트에는 아래 주소를 등록합니다.

```text
http://리눅스서버_IP:8000/mcp
```

`MCP_AUTH_TOKEN`을 설정했다면 MCP 클라이언트가 다음 HTTP 헤더를 보내야 합니다.

```text
Authorization: Bearer 충분히_긴_랜덤_토큰
```

브라우저 기반 MCP 클라이언트에서 접속한다면 해당 클라이언트의 Origin을 `ALLOWED_ORIGINS`에 추가합니다. 일반 데스크톱 MCP 클라이언트처럼 `Origin` 헤더를 보내지 않는 클라이언트는 이 설정의 영향을 받지 않습니다.

운영 환경에서는 가능하면 Nginx, Caddy 같은 리버스 프록시 뒤에 두고 HTTPS로 노출하세요.

### systemd 예시

`/etc/systemd/system/neis-mcp.service`:

```ini
[Unit]
Description=NEIS MCP Server
After=network-online.target
Wants=network-online.target

[Service]
WorkingDirectory=/opt/neis-mcp-py
EnvironmentFile=/opt/neis-mcp-py/.env
ExecStart=/opt/neis-mcp-py/.venv/bin/python -m neis_mcp
Restart=always
RestartSec=5
User=neis
Group=neis

[Install]
WantedBy=multi-user.target
```

적용:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now neis-mcp
sudo systemctl status neis-mcp
```

## HTTP 확인

```bash
curl http://127.0.0.1:8000/healthz
```

MCP 초기화 예시는 다음과 같습니다.

```bash
curl -X POST http://127.0.0.1:8000/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer 충분히_긴_랜덤_토큰' \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
      "protocolVersion": "2025-06-18",
      "capabilities": {},
      "clientInfo": {"name": "curl", "version": "1.0.0"}
    }
  }'
```

도구 호출 예시는 다음과 같습니다.

```bash
curl -X POST http://127.0.0.1:8000/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -H 'Authorization: Bearer 충분히_긴_랜덤_토큰' \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "get_school_info",
      "arguments": {
        "ATPT_OFCDC_SC_CODE": "T10",
        "pSize": 5
      }
    }
  }'
```

## 참고

- NEIS 데이터셋 목록: https://open.neis.go.kr/portal/data/dataset/searchDatasetPage.do
- MCP Streamable HTTP 사양: https://modelcontextprotocol.io/specification/2025-06-18/basic/transports
