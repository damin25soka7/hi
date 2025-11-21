# 빠른 시작 가이드 - NPX & 레거시 HTTP MCP 클라이언트

## 🚀 즉시 실행하기

### 1단계: 서버 시작

```bash
cd searxng-mcp-crawl
npx .
```

또는 환경 변수 설정과 함께:

```bash
SEARXNG_BASE_URL="http://localhost:32768" DESIRED_TIMEZONE="Asia/Seoul" npx .
```

### 2단계: MCP 클라이언트 설정

레거시 HTTP 형식만 지원하는 챗봇의 경우:

```json
{
  "searxng-enhanced": {
    "url": "http://localhost:32769",
    "type": "http",
    "method": "sse"
  }
}
```

## ✅ 작동 확인

### 헬스 체크
```bash
curl http://localhost:32769/health
```

### 도구 목록 확인
```bash
curl -X POST http://localhost:32769 \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

### 현재 시간 도구 테스트
```bash
curl -X POST http://localhost:32769 \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "get_current_datetime",
      "arguments": {}
    }
  }'
```

## 📋 사용 가능한 도구

1. **search_web** - 카테고리별 검색 (일반, 이미지, 동영상, 파일, 지도, 소셜미디어)
2. **get_website** - 웹페이지 가져오기 (PDF 지원)
3. **get_current_datetime** - 현재 시간 (시간대 지원)
4. **search** - 레거시 검색
5. **fetch_webpage** - 레거시 크롤링
6. **runLLM** - AI 액세스
7. **executor** - 도구 실행기
8. **tool_planner** - 작업 플래너

## 🔧 환경 변수

```bash
# SearXNG 설정
SEARXNG_BASE_URL=http://localhost:32768

# 서버 설정
HOST=0.0.0.0
PORT=32769

# 시간대
DESIRED_TIMEZONE=Asia/Seoul

# 콘텐츠 설정
CONTENT_MAX_LENGTH=10000
SEARCH_RESULT_LIMIT=10
```

## 💡 NPX의 장점

- ✅ Python 자동 확인
- ✅ 의존성 자동 설치
- ✅ 간단한 명령어로 실행
- ✅ 레거시 HTTP 클라이언트 완벽 지원
- ✅ SSE (Server-Sent Events) 지원

## 📚 추가 문서

- `NPX_USAGE.md` - 상세한 npx 사용법
- `examples/legacy_http_config.md` - HTTP 클라이언트 설정 예제
- `README_KR.md` - 전체 한글 문서

## 🐛 문제 해결

### Python을 찾을 수 없음
```bash
# Python 설치 확인
python3 --version

# Python 설치 (필요한 경우)
# Ubuntu/Debian: sudo apt install python3
# macOS: brew install python3
# Windows: python.org에서 다운로드
```

### SearXNG 연결 실패
```bash
# SearXNG 실행 확인
curl http://localhost:32768/search?q=test&format=json

# SearXNG가 실행 중이 아니면 시작 필요
```

### 포트 사용 중
```bash
# 다른 포트 사용
PORT=8080 npx .
```

## 🎉 이제 사용 준비 완료!

서버가 실행되면 레거시 HTTP MCP 클라이언트에서 모든 향상된 기능을 사용할 수 있습니다!
