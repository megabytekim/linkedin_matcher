# 🏷️ 버전 관리 가이드

## 📋 현재 버전
- **v1.0.0** - Initial release (2025-07-19)

## 🎯 버전 관리 정책

### Semantic Versioning (SemVer)
- **MAJOR.MINOR.PATCH** 형식 사용
- **MAJOR**: 호환되지 않는 API 변경
- **MINOR**: 이전 버전과 호환되는 새 기능 추가
- **PATCH**: 버그 수정

### 버전 태그 생성
```bash
# 새 버전 태그 생성
git tag -a v1.1.0 -m "✨ New feature: enhanced scraping"

# 태그 푸시
git push origin v1.1.0
```

## 📝 릴리즈 노트 템플릿

### ✨ 새 기능 추가 (MINOR)
```bash
git tag -a v1.1.0 -m "✨ Release v1.1.0

✨ New Features:
- Feature 1 description
- Feature 2 description

🔧 Improvements:
- Improvement 1
- Improvement 2

🐛 Bug Fixes:
- Bug fix 1
- Bug fix 2"
```

### 🔧 버그 수정 (PATCH)
```bash
git tag -a v1.0.1 -m "🔧 Release v1.0.1

🐛 Bug Fixes:
- Fixed issue with Gmail API connection
- Resolved playwright browser compatibility

🔧 Improvements:
- Updated error handling
- Improved test coverage"
```

### 💥 주요 변경 (MAJOR)
```bash
git tag -a v2.0.0 -m "💥 Release v2.0.0

💥 Breaking Changes:
- Changed API interface
- Removed deprecated features

✨ New Features:
- Major new functionality
- Complete rewrite of core module

🔧 Improvements:
- Performance improvements
- Better error handling"
```

## 🚀 릴리즈 프로세스

### 1. 코드 안정화
```bash
# 모든 테스트 통과 확인
python run_tests.py

# CI/CD 통과 확인
git push origin main
```

### 2. 태그 생성
```bash
# 버전 태그 생성
git tag -a v1.1.0 -m "Release message"

# 태그 푸시
git push origin v1.1.0
```

### 3. GitHub 릴리즈 생성
1. GitHub에서 "Releases" 탭 방문
2. "Create a new release" 클릭
3. 태그 선택 및 릴리즈 노트 작성
4. "Publish release" 클릭

## 📊 버전 히스토리

### v1.0.0 (2025-07-19) - Initial Release
- ✅ LinkedIn job scraper with Gmail integration
- ✅ MCP (Model Context Protocol) server
- ✅ AI assistant integration with OpenAI
- ✅ Comprehensive test suite
- ✅ CI/CD pipeline with GitHub Actions
- ✅ Python 3.10+ compatibility
- ✅ Playwright for web scraping
- ✅ Gmail API integration
- ✅ Unit tests and integration tests
- ✅ Code quality checks

## 🔄 다음 버전 계획

### v1.1.0 (예정)
- [ ] Enhanced error handling
- [ ] Better logging system
- [ ] Performance optimizations
- [ ] Additional test coverage

### v1.2.0 (예정)
- [ ] New scraping features
- [ ] UI improvements
- [ ] Configuration management
- [ ] Documentation updates

---

**Happy Versioning! 🚀** 