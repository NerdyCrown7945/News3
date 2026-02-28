# AI · ScienceTech 뉴스 브리핑 앱

한국어 중심 요약/핵심포인트/중복제거/클러스터링 기반 브리핑 앱입니다.

## 모드
- **로컬 모드**: FastAPI(`backend/app.py`) + SQLite(확장 지점), 수집 실행 버튼 활성
- **정적 모드(GitHub Pages)**: `public/*.json`만 사용, 수집 버튼 비활성 + fallback 표시

## 데이터 파이프라인
1. `python -m backend.generate_data`
2. 산출물 생성
   - `public/feed.json`
   - `public/articles/{id}.json`
   - `public/clusters.json`
   - `public/trends.json`

## 핵심 기능
- URL canonicalize + 홈/섹션 URL 무효 처리
- 중복 제거: canonical URL + 제목 유사도 + content hash
- 클러스터링: 제목/요약 기반 코사인 유사도
- 요약기 전략 패턴: 현재 rule-based, 이후 LLM 엔진 확장
- 필터 UX: 기간 자동 완화(24h→7d→30d→all), 결과 0개 fallback 문구
- 안정 정렬: published_at 동률 시 source/title/id tie-breaker

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
python -m backend.generate_data
```

### 정적 모드 프론트
```bash
NEXT_PUBLIC_STATIC_MODE=true npm run dev
```

### 로컬 모드 프론트
```bash
NEXT_PUBLIC_STATIC_MODE=false npm run dev
```
