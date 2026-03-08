# AI · ScienceTech 뉴스 브리핑 앱

한국어 중심 요약/핵심포인트/중복제거/클러스터링 기반 브리핑 앱입니다.

## 모드
- **로컬 모드**: FastAPI(`backend/app.py`) + SQLite(확장 지점), 수집 실행 버튼 활성
- **정적 모드(GitHub Pages)**: `frontend/public/data/*.json` 사용, 수집 버튼 비활성 + fallback 표시

## 데이터 파이프라인
1. `python backend/generate_data.py`
2. 산출물 생성
   - `frontend/public/data/feed.json`
   - `frontend/public/data/articles/{id}.json`
   - `frontend/public/data/clusters.json`
   - `frontend/public/data/trends.json`

## GitHub Actions
- `update-news.yml`: 2시간 주기/수동 실행, Python 3.11로 데이터 생성 후 변경된 정적 JSON 커밋/푸시
- `deploy-pages.yml`: main 푸시 시 Next.js 정적 빌드 후 GitHub Pages 배포

## 프론트 탭
- `/` 뉴스
- `/clusters` 클러스터 목록
- `/clusters/[id]` 클러스터 상세
- `/trends` 7일 트렌드
- `/planning` 기획/요구사항 문서 렌더링(`docs/planning.md` 단일 소스)

## 실행
### 로컬 API
```bash
uvicorn backend.app:app --reload --port 8000
```

### 정적 데이터 생성
```bash
python backend/generate_data.py
```

### 정적 모드 프론트
```bash
cd frontend
NEXT_PUBLIC_STATIC_MODE=true npm run dev
```

### 로컬 모드 프론트
```bash
cd frontend
NEXT_PUBLIC_STATIC_MODE=false npm run dev
```
