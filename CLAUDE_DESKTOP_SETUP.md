# Claude Desktop MCP 설정 가이드

> **v2.0.0 MCP-Only**
>
> 이 프로젝트는 이제 Claude Desktop MCP 서버 전용입니다. 로컬/CLI 모드는 지원하지 않습니다. 반드시 Claude Desktop에서 MCP 서버로만 사용하세요.

이 가이드는 LinkedIn Job Scraper 프로젝트를 Claude Desktop에서 MCP 서버로 사용하는 방법을 설명합니다.

## 🚀 빠른 설정

### 1. Claude Desktop 설치
- [Claude Desktop](https://claude.ai/download) 다운로드 및 설치

### 2. 설정 파일 위치 찾기
**macOS**:
```bash
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Windows**:
```bash
%APPDATA%\Claude\claude_desktop_config.json
```

### 3. 설정 파일 생성/수정
위 경로에 `claude_desktop_config.json` 파일을 생성하고 다음 내용을 붙여넣기:

```json
{
  "mcpServers": {
    "linkedin-job-scraper": {
      "command": "python",
      "args": [
        "-m",
        "core.serve"
      ],
      "cwd": "/Users/michael/cursor_projects/linkedin_matcher",
      "env": {
        "PYTHONPATH": "/Users/michael/cursor_projects/linkedin_matcher"
      }
    }
  }
}
```

**⚠️ 중요**: `cwd` 경로를 실제 프로젝트 경로로 변경하세요!

### 4. Claude Desktop 재시작
- Claude Desktop 완전 종료 (⌘+Q / Alt+F4)
- 다시 실행

## 🛠️ 사용 가능한 도구들

설정 완료 후 Claude Desktop에서 다음과 같은 요청을 할 수 있습니다:

### Gmail 관련
```
"최근 수신한 LinkedIn 채용공고 이메일 5개를 보여줘"
"네이버에서 온 이메일 검색해줘"
"이메일에서 채용공고 URL 추출해줘"
```

### 스크래핑 관련
```
"LinkedIn 채용공고 상세 정보를 스크래핑해줘"
"채용공고들을 분석해서 요약해줘"
```

### 통합 워크플로우
```
"최근 채용공고 이메일을 찾아서 URL을 추출하고 상세 정보를 스크래핑해줘"
```

## 🔧 문제 해결

### 연결 확인
Claude Desktop에서 이런 메시지가 보이면 성공:
- 🔨 (해머) 아이콘이 채팅창에 표시됨
- "MCP tools available" 툴팁 확인

### 일반적인 문제들
1. **경로 오류**: `cwd` 경로가 정확한지 확인
2. **Python 환경**: 가상환경이 활성화되어 있는지 확인
3. **의존성**: `pip install -r requirements.txt` 실행
4. **권한**: Gmail API 토큰이 설정되어 있는지 확인

### 로그 확인
문제 발생 시 다음 명령어로 직접 테스트:
```bash
cd /Users/michael/cursor_projects/linkedin_matcher
PYTHONPATH=. python -m core.serve
```

## 🎯 고급 설정

### 여러 MCP 서버 함께 사용
```json
{
  "mcpServers": {
    "linkedin-job-scraper": {
      "command": "python",
      "args": ["-m", "core.serve"],
      "cwd": "/Users/michael/cursor_projects/linkedin_matcher",
      "env": {
        "PYTHONPATH": "/Users/michael/cursor_projects/linkedin_matcher"
      }
    },
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem",
        "/Users/michael/Documents"
      ]
    }
  }
}
```

### 환경 변수 추가
```json
{
  "mcpServers": {
    "linkedin-job-scraper": {
      "command": "python",
      "args": ["-m", "core.serve"],
      "cwd": "/Users/michael/cursor_projects/linkedin_matcher",
      "env": {
        "PYTHONPATH": "/Users/michael/cursor_projects/linkedin_matcher",
        "GMAIL_API_KEY": "your_key_here",
        "DEBUG": "true"
      }
    }
  }
}
```

## 📋 도구 목록

설정 완료 후 사용할 수 있는 13개 MCP 도구:

### Gmail 도구 (4개)
- `list_emails` - 이메일 검색
- `extract_job_urls` - 채용공고 URL 추출  
- `get_message_content` - 이메일 내용 조회
- `add_label` - 이메일 라벨 추가

### 스크래핑 도구 (3개)  
- `scrape_job` - 채용공고 스크래핑
- `scrape_multiple_jobs` - 여러 채용공고 스크래핑
- `validate_job_url` - URL 검증

### 통합 도구 (4개)
- `get_job_details_from_email` - 이메일에서 채용공고 정보 추출
- `scrape_jobs_from_email_urls` - 이메일 URL로 스크래핑  
- `scrape_jobs_from_url_list` - URL 리스트 스크래핑
- `process_linkedin_emails` - 완전 자동화 워크플로우

### 기타 도구 (2개)
- `convert_to_guest_url` - 게스트 URL 변환
- `get_job_summary` - 채용공고 요약

## ✅ 설정 완료 확인

1. Claude Desktop에서 🔨 아이콘 확인
2. "linkedin job scraper 사용 가능한 도구 보여줘" 메시지 전송
3. 도구 목록이 표시되면 성공!

---

이제 Claude Desktop에서 LinkedIn 채용공고 검색과 스크래핑을 자연어로 요청할 수 있습니다! 🎉 