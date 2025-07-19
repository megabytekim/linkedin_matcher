# 🔍 LinkedIn 채용공고 스크래퍼

Gmail에서 LinkedIn 채용공고를 자동으로 찾아서 스크래핑하는 AI 어시스턴트 도구입니다.

## ✨ 주요 기능

- **📧 Gmail 연동**: 이메일에서 LinkedIn 채용공고 링크 자동 추출
- **🌐 LinkedIn 스크래핑**: 채용공고 상세 정보 자동 수집
- **🤖 AI 어시스턴트 연동**: OpenAI GPT-4와 MCP(Model Context Protocol) 통합
- **🔄 워크플로우 자동화**: 이메일 검색 → URL 추출 → 채용공고 스크래핑 자동화

## 🏗️ 아키텍처

```
linkedin_matcher/
├── 📁 core/                    # MCP 서버 (핵심)
│   ├── server_app.py          # 단일 FastMCP 인스턴스
│   ├── serve.py               # 서버 런처
│   └── tools/                 # MCP 도구들
│       ├── gmail.py           # Gmail 도구 등록
│       └── scraper.py         # 스크래핑 도구 등록
├── 📁 host/                   # AI 호스트
│   └── openai_host.py         # OpenAI GPT-4 호스트
├── 📁 gmail_module/           # Gmail API 모듈
│   ├── gmail_api.py           # Gmail 연동 클래스
│   └── tests/                 # Gmail 테스트
├── 📁 scraper_module/         # 스크래핑 모듈
│   ├── job_scraper.py         # LinkedIn 스크래퍼
│   └── tests/                 # 스크래핑 테스트
├── mcp_config.json            # MCP 서버 설정
├── config.py                  # 전역 설정
└── test_mcp.py               # 통합 테스트
```

### 🔄 데이터 흐름

```
사용자 요청 → OpenAI Host → MCP Server → Gmail/Scraper Tools → 결과 반환
```

## 🚀 빠른 시작

### 1️⃣ 환경 설정

```bash
# 저장소 클론
git clone [repository-url]
cd linkedin_matcher

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는 venv\Scripts\activate  # Windows

# 의존성 설치
pip install -r requirements.txt

# Playwright 브라우저 설치
playwright install
```

### 2️⃣ API 키 설정

`.env` 파일을 생성하고 OpenAI API 키를 추가하세요:

```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
```

### 3️⃣ Gmail API 설정

1. [Google Cloud Console](https://console.cloud.google.com/)에서 새 프로젝트 생성
2. Gmail API 활성화
3. OAuth 2.0 클라이언트 ID 생성 (데스크톱 애플리케이션)
4. `credentials.json` 파일을 프로젝트 루트에 저장

### 4️⃣ 테스트 실행

```bash
# MCP 도구 테스트
PYTHONPATH=. python test_mcp.py
```

모든 테스트가 통과하면 설정이 완료된 것입니다! ✅

## 🛠️ 사용법

### MCP 서버 모드 (권장)

**1단계: MCP 서버 시작**
```bash
PYTHONPATH=. python core/serve.py
```

**2단계: AI 어시스턴트에서 MCP 설정**
- `mcp_config.json` 파일을 AI 어시스턴트의 MCP 설정에 추가
- 서버가 `stdio://core/serve.py`로 연결됨

**3단계: 자연어로 요청**
```
최근 LinkedIn 이메일을 검색해서 채용공고가 있는지 확인해주세요.
채용공고가 있으면 스크래핑해서 상세 정보를 알려주세요.
```

### 로컬 호스트 모드

```bash
# OpenAI 호스트 직접 실행
python host/openai_host.py
```

대화형 모드에서 AI 어시스턴트와 채팅할 수 있습니다.

## 🔧 도구 기능

### 📧 Gmail 도구

- **`list_emails`**: 검색 쿼리로 이메일 목록 조회
- **`extract_job_urls`**: 이메일에서 LinkedIn 채용공고 URL 추출
- **`get_email_content`**: 이메일 전체 내용 조회
- **`label_email`**: 이메일에 라벨 추가
- **`get_job_details_from_email`**: 이메일에서 채용공고 상세 정보 추출

### 🌐 스크래핑 도구

- **`scrape_job`**: LinkedIn 채용공고 스크래핑
- **`scrape_multiple_jobs`**: 여러 채용공고 일괄 스크래핑
- **`validate_linkedin_url`**: LinkedIn URL 유효성 검증
- **`convert_to_guest_url`**: 로그인 불필요한 게스트 URL 변환
- **`get_job_summary`**: 채용공고 요약 정보 조회

## 💡 사용 예제

### 이메일에서 채용공고 찾기

```python
# 최근 LinkedIn 이메일 검색
emails = list_emails("from:linkedin.com", 5)

# 첫 번째 이메일에서 채용공고 URL 추출
if emails:
    urls = extract_job_urls(emails[0]['id'])
    
    # 채용공고 스크래핑
    for url_info in urls:
        job_data = scrape_job(url_info['url'])
        print(f"직무: {job_data['title']}")
        print(f"회사: {job_data['company']}")
```

### AI 어시스턴트 워크플로우

```
사용자: "최근 3일간 받은 LinkedIn 이메일을 확인해서 
       Senior Developer 관련 채용공고가 있으면 
       상세 정보를 스크래핑해서 정리해줘"

AI: 1. Gmail에서 최근 LinkedIn 이메일 검색
    2. 각 이메일에서 채용공고 URL 추출
    3. "Senior Developer" 키워드가 포함된 공고 필터링
    4. 해당 공고들을 스크래핑하여 상세 정보 수집
    5. 결과를 정리하여 제공
```

## 📊 세션 메모리

시스템은 대화 기록과 도구 실행 결과를 자동으로 저장합니다:

- **`openai_conversation_history.json`**: 대화 내역
- **`openai_session_memory.json`**: 도구 실행 결과

이전 대화에서 추출한 채용공고 정보를 계속 참조할 수 있습니다.

## ⚙️ 설정 파일

### `mcp_config.json`
MCP 서버 연결 설정
```json
{
  "mcpServers": {
    "linkedin-scraper": {
      "command": "python",
      "args": ["-u", "core/serve.py"],
      "cwd": "/path/to/linkedin_matcher",
      "env": {"PYTHONPATH": "."}
    }
  }
}
```

### `config.py`
Gmail API 및 전역 설정
```python
GMAIL_SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
CREDENTIALS_FILE = Path('credentials.json')
TOKEN_FILE = Path('token.json')
```

## 🐛 문제 해결

### Common Issues

**1. Gmail API 권한 부족**
```
Error: insufficientPermissions
```
→ `credentials.json` 재생성 후 `token.json` 삭제

**2. Playwright 브라우저 없음**
```
Error: Executable doesn't exist
```
→ `playwright install` 실행

**3. OpenAI API 키 오류**
```
Error: 401 Unauthorized
```
→ `.env` 파일의 API 키 확인

**4. MCP 서버 연결 실패**
```
→ PYTHONPATH=. python core/serve.py로 서버 수동 실행 테스트
```

## 🔒 보안 주의사항

- **API 키**: `.env` 파일을 Git에 커밋하지 마세요
- **Gmail 토큰**: `token.json`은 민감한 정보입니다
- **스크래핑**: LinkedIn 이용약관을 준수하여 적절한 간격으로 요청하세요

## 🤝 기여 방법

1. 이슈 리포트: 버그나 개선사항 제안
2. 풀 리퀘스트: 코드 개선 및 새 기능 추가
3. 문서 개선: 사용법이나 설정 가이드 개선

## 📄 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.

---

## 🆘 도움이 필요하신가요?

- 📖 **설정 가이드**: 위의 '빠른 시작' 섹션을 따라하세요
- 🧪 **테스트**: `python test_mcp.py`로 모든 도구가 정상 작동하는지 확인
- 🐛 **버그 리포트**: GitHub Issues에 문제를 신고해주세요

**Happy Scraping! 🚀** 