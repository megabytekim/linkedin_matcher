# 🔄 CI/CD 사용법 가이드

## 📋 개요
이 프로젝트는 GitHub Actions를 사용한 간단한 CI/CD 파이프라인을 제공합니다.

## 🚀 자동 실행
다음과 같은 경우에 자동으로 CI/CD가 실행됩니다:

### ✅ CI (Continuous Integration)
- `main` 또는 `develop` 브랜치에 푸시
- `main` 브랜치로 Pull Request 생성
- **실행 내용**:
  - 의존성 설치
  - 코드 임포트 검증
  - 단위 테스트 실행
  - 코드 품질 검사

### 🚀 CD (Continuous Deployment)
- `main` 브랜치에 푸시될 때만 실행
- **실행 내용**:
  - 배포 알림
  - 배포 아티팩트 생성
  - 버전 태깅

## 🧪 로컬 테스트

### 전체 테스트 실행
```bash
python run_tests.py
```

### 개별 테스트
```bash
# 임포트 테스트
python -c "from scraper_module.job_scraper import JobScraper; print('OK')"

# 단위 테스트
python -m pytest scraper_module/tests/ -v

# 코드 품질
flake8 scraper_module/job_scraper.py --max-line-length=120
```

## 📊 테스트 결과
테스트 결과는 다음과 같이 표시됩니다:
- ✅ **PASSED**: 테스트 성공
- ❌ **FAILED**: 테스트 실패
- ⚠️ **FAILED (allowed)**: 실패하지만 허용된 테스트

## 🔧 설정 파일

### `.github/workflows/ci.yml`
GitHub Actions 워크플로우 설정

### `pytest.ini`
pytest 테스트 설정

### `requirements-dev.txt`
개발 및 CI/CD용 의존성

### `run_tests.py`
로컬 테스트 러너

## 🎯 CI/CD 성공 조건
- 필수 임포트 테스트 통과
- 단위 테스트 전체 통과
- 코드 품질 검사 (실패 허용)

## 🛠️ 커스터마이징

### 테스트 추가
`run_tests.py`의 `tests` 배열에 새로운 테스트 추가:

```python
tests = [
    # ... 기존 테스트들
    ("새로운_테스트_명령어", "테스트 설명", False),  # False = 실패시 중단
]
```

### 배포 스크립트 추가
`.github/workflows/ci.yml`의 `deploy` job에서 실제 배포 스크립트 추가

## 📈 모니터링
- GitHub Actions 탭에서 CI/CD 실행 상태 확인
- README의 배지로 현재 상태 확인
- 실패시 이메일 알림 (GitHub 설정에 따라)

---

**Happy CI/CD! 🚀** 