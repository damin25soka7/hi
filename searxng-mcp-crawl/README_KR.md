# SearXNG MCP 서버 - 향상된 에디션 (한국어)

OvertliDS/mcp-searxng-enhanced의 향상된 기능이 통합된 SearXNG용 MCP 서버입니다.

## 🌟 주요 기능

### 통합된 향상 기능
- ✅ **카테고리별 검색**: 일반, 이미지, 동영상, 파일, 지도, 소셜 미디어 검색 지원
- ✅ **PDF 읽기**: PDF 자동 감지 및 마크다운 변환
- ✅ **스마트 캐싱**: TTL 기반 메모리 캐싱 (5분 TTL, 30분 최대 유효 기간)
- ✅ **속도 제한**: 도메인별 속도 제한 (분당 10회 요청)
- ✅ **향상된 콘텐츠 추출**: Trafilatura를 사용한 깨끗한 텍스트 추출
- ✅ **Reddit 지원**: Reddit URL을 old.reddit.com으로 자동 변환
- ✅ **플러그인 시스템**: 확장 가능한 도구 아키텍처
- ✅ **시간대 지원**: 날짜/시간 도구에 시간대 설정 가능

## 🚀 빠른 시작

### 사전 요구사항
- Python 3.9 이상 (3.11 권장)
- SearXNG 인스턴스 실행 중 (자체 호스팅 또는 접근 가능한 엔드포인트)

### 설치 방법

1. **저장소 클론:**
   ```bash
   git clone <your-repo-url>
   cd hi/searxng-mcp-crawl
   ```

2. **가상 환경 생성 (권장):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. **의존성 설치:**
   ```bash
   pip install -r requirements.txt
   ```

## 📦 사용 방법

### 방법 1: NPX (권장 - 레거시 HTTP MCP 클라이언트 지원)

**새로운 기능!** npx로 서버를 즉시 실행 - 레거시 HTTP MCP 클라이언트에 완벽합니다:

```bash
# npx로 직접 실행
npx @damin25soka7/searxng-mcp-server

# 또는 로컬 디렉토리에서
cd searxng-mcp-crawl
npx .
```

**환경 변수 설정:**
```bash
SEARXNG_BASE_URL="http://localhost:32768" DESIRED_TIMEZONE="Asia/Seoul" npx .
```

**레거시 HTTP MCP 클라이언트 설정:**
```json
{
  "searxng-enhanced": {
    "url": "http://localhost:32769",
    "type": "http",
    "method": "sse"
  }
}
```

npx 스크립트의 장점:
- ✅ Python 설치 자동 확인
- ✅ 필요시 의존성 자동 설치
- ✅ SSE 지원 HTTP 서버 시작
- ✅ 레거시 MCP 클라이언트와 호환

자세한 npx 사용법은 [NPX_USAGE.md](NPX_USAGE.md)를 참조하세요.

### 방법 2: JSON 블록 설정 (최신 MCP 클라이언트용)

**별도의 Docker 실행 없이** MCP 클라이언트에서 직접 사용할 수 있습니다!

#### Claude Desktop 설정

파일 위치:
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

설정 내용:
```json
{
  "mcpServers": {
    "searxng-enhanced": {
      "command": "python3",
      "args": [
        "/절대/경로/to/searxng-mcp-crawl/mcp_stdio_server.py"
      ],
      "env": {
        "SEARXNG_BASE_URL": "http://localhost:32768",
        "CONTENT_MAX_LENGTH": "10000",
        "DESIRED_TIMEZONE": "Asia/Seoul"
      }
    }
  }
}
```

#### Cline (VS Code) 설정

파일 위치: `.vscode/cline_mcp_settings.json`

설정 내용:
```json
{
  "mcpServers": {
    "searxng-enhanced": {
      "command": "python3",
      "args": [
        "/절대/경로/to/searxng-mcp-crawl/mcp_stdio_server.py"
      ],
      "env": {
        "SEARXNG_BASE_URL": "http://localhost:32768",
        "CONTENT_MAX_LENGTH": "10000",
        "DESIRED_TIMEZONE": "Asia/Seoul"
      },
      "timeout": 60
    }
  }
}
```

**중요 사항:**
- Python 스크립트의 **절대 경로**를 사용하세요
- Python이 PATH에 있거나 Python 실행 파일의 전체 경로를 사용하세요
- 서버는 stdin/stdout으로 통신합니다 (JSON-RPC 프로토콜)
- 별도의 서버 프로세스가 필요 없습니다 - 클라이언트가 시작/중지를 관리합니다

### 방법 3: HTTP 서버 모드 (전통적 방식)

SSE를 지원하는 독립 HTTP 서버로 실행:

```bash
python server.py
```

또는 npx 사용 (의존성 자동 처리):

```bash
npx .
```

서버는 `http://localhost:32769` (또는 설정된 HOST:PORT)에서 시작됩니다.

## 🔧 사용 가능한 도구

### 1. search_web
카테고리 지원이 있는 향상된 웹 검색

**주요 기능:**
- 일반 검색: 전체 콘텐츠 추출이 있는 웹페이지
- 이미지 검색: 이미지 URL 및 메타데이터
- 동영상 검색: 동영상 정보
- 파일 검색: 파일 다운로드 링크
- 지도 검색: 위치/지도 데이터
- 소셜 미디어: 소셜 미디어 게시물

**사용 예:**
```json
{
  "name": "search_web",
  "arguments": {
    "query": "머신러닝 튜토리얼",
    "limit": 10,
    "category": "general"
  }
}
```

**이미지 검색 예:**
```json
{
  "name": "search_web",
  "arguments": {
    "query": "산 풍경",
    "limit": 10,
    "category": "images"
  }
}
```

### 2. get_website
향상된 기능으로 웹페이지에서 콘텐츠 가져오기 및 추출

**주요 기능:**
- PDF를 자동으로 감지하고 마크다운으로 변환
- 빠른 반복 액세스를 위한 결과 캐싱
- Reddit URL을 old.reddit.com으로 변환
- Trafilatura를 사용한 깨끗한 콘텐츠 추출

**사용 예:**
```json
{
  "name": "get_website",
  "arguments": {
    "url": "https://example.com/article",
    "max_length": 10000,
    "use_cache": true
  }
}
```

### 3. get_current_datetime
설정된 시간대의 현재 날짜 및 시간 가져오기

**사용 예:**
```json
{
  "name": "get_current_datetime",
  "arguments": {}
}
```

## ⚙️ 설정

### 환경 변수

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `SEARXNG_BASE_URL` | SearXNG 인스턴스 URL | `http://localhost:32768` |
| `HOST` | 서버 호스트 (HTTP 모드) | `0.0.0.0` |
| `PORT` | 서버 포트 (HTTP 모드) | `32769` |
| `CONTENT_MAX_LENGTH` | 페이지당 최대 콘텐츠 길이 | `10000` |
| `SEARCH_RESULT_LIMIT` | 기본 검색 결과 제한 | `10` |
| `DESIRED_TIMEZONE` | datetime 도구용 시간대 | `America/New_York` |

**한국 시간대 사용:** `DESIRED_TIMEZONE=Asia/Seoul`

### 캐시 설정

`enhanced_crawler.py`에서 캐싱 시스템을 구성할 수 있습니다:
- `cache_maxsize`: 최대 캐시 항목 수 (기본값: 100)
- `cache_ttl_minutes`: 캐시 TTL(분) (기본값: 5)
- `cache_max_age_minutes`: 캐시 검증을 위한 최대 수명(분) (기본값: 30)

### 속도 제한 설정

`enhanced_crawler.py`에서 속도 제한을 구성할 수 있습니다:
- `rate_limit_requests_per_minute`: 도메인당 분당 최대 요청 수 (기본값: 10)
- `rate_limit_timeout_seconds`: 속도 제한 추적 창(초) (기본값: 60)

## 🎯 주요 개선 사항

### OvertliDS/mcp-searxng-enhanced에서 통합된 기능들:

1. **카테고리별 검색 결과**
   - 이미지, 동영상, 파일, 지도, 소셜 미디어 등 각 카테고리에 맞는 구조화된 데이터

2. **PDF 문서 처리**
   - PyMuPDF 및 pymupdf4llm을 사용한 자동 PDF 감지 및 마크다운 변환

3. **Trafilatura 기반 콘텐츠 추출**
   - 깨끗하고 읽기 쉬운 텍스트 추출

4. **TTL 캐싱**
   - 구성 가능한 캐시 (100개 항목, 5분 TTL, 30분 최대 수명)

5. **도메인 기반 속도 제한**
   - 도메인당 분당 10회 요청으로 제한하여 서비스 남용 방지

6. **Reddit URL 변환**
   - www.reddit.com을 old.reddit.com으로 자동 변환하여 더 나은 스크래핑

7. **향상된 오류 처리**
   - 사용자 정의 예외 타입과 명확한 오류 메시지

## 🔌 플러그인 시스템

서버는 확장 가능한 플러그인 시스템을 사용합니다.

**사용 가능한 플러그인:**
- `enhanced_search_plugin.py`: 카테고리가 있는 향상된 웹 검색
- `enhanced_crawl_plugin.py`: 캐싱 및 PDF 지원이 있는 향상된 웹페이지 가져오기
- `datetime_plugin.py`: 시간대 지원이 있는 현재 날짜/시간 도구
- `search_plugin.py`: 원래 검색 플러그인 (레거시)
- `crawl_plugin.py`: 원래 크롤 플러그인 (레거시)

## 🐛 문제 해결

### SearXNG에 연결할 수 없음
- SearXNG가 실행 중인지 확인: `curl http://localhost:32768/search?q=test&format=json`
- `SEARXNG_BASE_URL` 환경 변수 확인
- 방화벽/네트워크 설정 확인

### ModuleNotFoundError
- 모든 의존성이 설치되었는지 확인: `pip install -r requirements.txt`
- 가상 환경을 사용하는 경우 활성화되었는지 확인

### PDF 처리 실패
- `pymupdf` 및 `pymupdf4llm`이 설치되었는지 확인
- PDF에 액세스할 수 있고 손상되지 않았는지 확인

### 속도 제한 오류
- `enhanced_crawler.py`에서 `rate_limit_requests_per_minute` 조정
- 속도 제한 창이 만료될 때까지 대기 (기본값: 60초)

### MCP 클라이언트가 서버를 찾을 수 없음
- JSON 설정에서 절대 경로 사용
- Python이 PATH에 있는지 확인
- `mcp_stdio_server.py`가 실행 가능한지 확인: `chmod +x mcp_stdio_server.py` (Unix)

## 🙏 감사의 말

이 프로젝트는 다음에서 기능을 통합합니다:
- [OvertliDS/mcp-searxng-enhanced](https://github.com/OvertliDS/mcp-searxng-enhanced) - SearXNG용 향상된 MCP 서버
- [SearXNG](https://github.com/searxng/searxng) - 개인정보 보호 메타 검색 엔진
- [Trafilatura](https://github.com/adbar/trafilatura) - 웹 스크래핑 및 콘텐츠 추출
- [PyMuPDF](https://pymupdf.readthedocs.io/) - PDF 처리 라이브러리

## 📄 라이선스

MIT License
