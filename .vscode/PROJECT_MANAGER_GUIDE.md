# Project Manager 사용 가이드

## 설정 완료!

프로젝트에 **Project Manager** 확장이 최적화되어 설정되었습니다.

## 📁 설정된 프로젝트 구조

### Main Projects

- **Quant Platform (Full Stack)** - 전체 프로젝트 루트
  - 태그: `fullstack`, `production`, `main`

### Backend Development

- **Quant - Backend (FastAPI)** - FastAPI 백엔드
  - 태그: `backend`, `python`, `fastapi`
- **Quant - API Routes** - API 엔드포인트 개발
  - 태그: `api`, `backend`, `routes`
- **Quant - Services Layer** - 비즈니스 로직
  - 태그: `services`, `backend`, `business-logic`

### Frontend Development

- **Quant - Frontend (Next.js)** - Next.js 프론트엔드
  - 태그: `frontend`, `nextjs`, `react`

### Strategy Development

- **Quant - Strategy Development** - 트레이딩 전략 개발
  - 태그: `strategy`, `trading`, `development`

### Documentation

- **Quant - Documentation** - 프로젝트 문서
  - 태그: `docs`, `documentation`

### Testing

- **Quant - Tests** - 테스트 코드
  - 태그: `tests`, `testing`, `qa`

## 🚀 사용 방법

### 1. 프로젝트 목록 보기

- **단축키**: `Cmd+Shift+P` → "Project Manager: List Projects"
- **사이드바**: 왼쪽 Activity Bar에서 "Project Manager" 아이콘 클릭

### 2. 프로젝트 전환

- **빠른 전환**: `Cmd+Shift+P` → "Project Manager: List Projects" → 원하는
  프로젝트 선택
- **상태바**: 하단 상태바에서 현재 프로젝트명 클릭 → 다른 프로젝트 선택

### 3. 새 창에서 열기

- 프로젝트 목록에서 `Ctrl+Enter` (새 창)
- `Enter` (현재 창에서 전환)

### 4. 태그로 필터링

프로젝트 목록에서 태그 검색:

- `backend` - 백엔드 관련 프로젝트만
- `frontend` - 프론트엔드 프로젝트만
- `strategy` - 전략 개발 관련
- `docs` - 문서 작업 시

## 💡 활용 시나리오

### 시나리오 1: API 개발

1. "Quant - API Routes" 프로젝트 선택
2. API 엔드포인트 개발
3. "Quant - Services Layer" 프로젝트로 전환
4. 서비스 로직 구현

### 시나리오 2: 전략 개발 및 백테스트

1. "Quant - Strategy Development" 프로젝트 선택
2. 새 전략 구현
3. "Quant - Tests" 프로젝트로 전환
4. 전략 테스트 작성

### 시나리오 3: 풀스택 개발

1. "Quant - Backend" 프로젝트에서 API 개발
2. "Quant - Frontend" 프로젝트로 전환
3. UI 컴포넌트 개발
4. "Quant Platform (Full Stack)" 프로젝트로 전환
5. 통합 테스트

### 시나리오 4: 문서 작성

1. "Quant - Documentation" 프로젝트 선택
2. 문서 작성/수정
3. 코드 참조 필요 시 해당 프로젝트로 전환

## ⚙️ 설정 파일 위치

- **프로젝트 정의**: `.vscode/projects.json`
- **확장 설정**: `.vscode/settings.json`

## 🎯 주요 설정

```json
{
  "projectManager.groupList": true, // 그룹별 정리
  "projectManager.sortList": "Name", // 이름순 정렬
  "projectManager.showProjectNameInStatusBar": true, // 상태바에 프로젝트명 표시
  "projectManager.checkInvalidPathsBeforeListing": true // 유효하지 않은 경로 체크
}
```

## 🔧 커스터마이징

### 새 프로젝트 추가

`.vscode/projects.json`에 추가:

```json
{
  "name": "내 프로젝트",
  "rootPath": "/경로/to/프로젝트",
  "tags": ["태그1", "태그2"],
  "group": "그룹명",
  "enabled": true
}
```

### 태그 추가

`.vscode/settings.json`의 `projectManager.tags` 배열에 추가

## 📋 단축키 추천

VS Code의 Keyboard Shortcuts에서 설정:

```json
{
  "key": "cmd+alt+p",
  "command": "projectManager.listProjects"
},
{
  "key": "cmd+alt+s",
  "command": "projectManager.saveProject"
}
```

## 💼 워크플로우 팁

1. **컨텍스트 스위칭 최소화**:

   - 관련된 프로젝트만 열기 (예: Backend + Services)

2. **태그 활용**:

   - 작업 유형별로 프로젝트 필터링

3. **그룹 활용**:

   - 개발 영역별로 프로젝트 정리

4. **상태바 활용**:
   - 현재 작업 컨텍스트 항상 확인

## 🔗 관련 확장 프로그램

함께 사용하면 좋은 확장:

- **Peacock**: 프로젝트별 색상 테마 (컨텍스트 구분)
- **Todo Tree**: 프로젝트별 TODO 관리
- **GitLens**: Git 히스토리 추적

---

**설정 완료!** 이제 `Cmd+Shift+P` → "Project Manager"로 시작하는 명령어를
확인해보세요! 🎉
