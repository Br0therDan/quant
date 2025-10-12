# 테마 스타일 가이드 - 목차

> 퀀트 백테스트 플랫폼의 테마를 세련되게 개선하기 위한 완전한 가이드

## 📚 문서 구성

### 1. [테마 개선 가이드 (메인)](./THEME_IMPROVEMENT_GUIDE.md)

**대상**: 개발자  
**내용**:

- 색상 팔레트 개선 (7가지 옵션)
- 타이포그래피 고도화 (3종 폰트 시스템)
- 그림자 & 입체감
- 애니메이션 & 전환효과
- 다크모드 최적화
- 금융 차트 전용 색상

**사용 시점**: 전체적인 테마 개선을 계획할 때

---

### 2. [빠른 시작 가이드](./THEME_QUICK_START.md)

**대상**: 빠르게 변화를 보고 싶은 개발자  
**내용**:

- 5분 안에 적용 가능한 개선
- 3가지 스타일 옵션 (핀테크/프리미엄/그라디언트)
- 즉시 확인 방법
- 롤백 방법

**사용 시점**: 빠르게 시각적 변화를 테스트할 때

---

### 3. [시각적 비교](./THEME_VISUAL_COMPARISON.md)

**대상**: 디자인 결정을 내려야 하는 팀  
**내용**:

- Before/After 비교
- 3가지 추천 조합 (보수적/중간/전면)
- 색상 샘플 코드
- AB 테스트 방법
- 접근성 체크리스트

**사용 시점**: 어떤 스타일을 적용할지 결정할 때

---

## 🎯 시작 가이드

### Step 1: 현재 상태 파악

현재 테마는 다음과 같이 구성되어 있습니다:

**파일 구조**

```
frontend/src/components/shared-theme/
├── AppTheme.tsx                    # 테마 Provider (루트)
├── themePrimitives.ts              # 색상, 폰트, 그림자 정의
├── ColorModeIconDropdown.tsx       # 다크모드 토글
└── customizations/
    ├── dataDisplay.tsx             # List, Chip, Table 등
    ├── feedback.tsx                # Alert, Dialog, Progress
    ├── inputs.tsx                  # Button, Input, Checkbox 등
    ├── navigation.tsx              # Menu, Tabs, Drawer 등
    └── surfaces.ts                 # Card, Paper, Accordion
```

**적용 위치**

```
app/layout.tsx → AppTheme으로 전체 앱 감싸기
```

---

### Step 2: 개선 방향 선택

#### 🟦 옵션 A: 보수적 개선 (추천)

- 시간: 5분
- 위험도: ⭐☆☆☆☆
- 변경: 둥근 모서리, 그림자만 개선
- 문서: [빠른 시작 가이드](./THEME_QUICK_START.md)

#### 🟨 옵션 B: 브랜드 색상 변경

- 시간: 15분
- 위험도: ⭐⭐☆☆☆
- 변경: 색상 팔레트 + 그림자
- 문서: [빠른 시작 가이드](./THEME_QUICK_START.md) > 옵션 1 or 2

#### 🟪 옵션 C: 전면 리디자인

- 시간: 1시간
- 위험도: ⭐⭐⭐⭐☆
- 변경: 색상, 타이포그래피, 애니메이션, 그라디언트
- 문서: [테마 개선 가이드](./THEME_IMPROVEMENT_GUIDE.md)

---

### Step 3: 적용 및 테스트

#### 변경할 파일

```
1순위: themePrimitives.ts         (색상, 그림자, 둥근 모서리)
2순위: app/layout.tsx              (폰트 추가)
3순위: customizations/*.tsx        (컴포넌트별 세부 조정)
```

#### 테스트 체크리스트

```
✓ 라이트 모드 확인
✓ 다크 모드 확인
✓ 버튼 호버 효과
✓ 카드 그림자
✓ 차트 색상
✓ 사이드바 스타일
✓ 모바일 반응형
```

---

## 🎨 주요 개선 항목 요약

### 색상 (Priority: ⭐⭐⭐⭐⭐)

```typescript
// themePrimitives.ts
export const brand = { ... }      // 브랜드 색상
export const financial = { ... }  // 차트 색상 (추가)
```

**효과**: 가장 큰 시각적 변화

### 둥근 모서리 (Priority: ⭐⭐⭐⭐☆)

```typescript
export const shape = {
  borderRadius: 12, // 8 → 12
};
```

**효과**: 부드럽고 모던한 느낌

### 그림자 (Priority: ⭐⭐⭐☆☆)

```typescript
baseShadow: "0px 2px 4px ..., 0px 4px 8px ...";
```

**효과**: 입체감 증가

### 타이포그래피 (Priority: ⭐⭐☆☆☆)

```typescript
fontFamily: "Inter + Roboto + JetBrains Mono";
```

**효과**: 가독성 향상, 전문적인 느낌

### 애니메이션 (Priority: ⭐☆☆☆☆)

```typescript
transition: "all 250ms cubic-bezier(...)";
```

**효과**: 부드러운 인터랙션

---

## 💡 빠른 의사결정 가이드

### "무엇을 먼저 해야 할까?"

```
시간이 5분 있다면:
→ 둥근 모서리만 변경 (12px)

시간이 15분 있다면:
→ 색상 + 둥근 모서리 변경

시간이 1시간 있다면:
→ 색상 + 타이포그래피 + 그림자

디자이너와 협의할 시간이 있다면:
→ 시각적 비교 문서 보면서 AB 테스트
```

### "어떤 색상을 선택할까?"

```
금융/핀테크 느낌 → 시안 (200°)
프리미엄/전문가 → 네이비 (220°)
모던/창의적 → 보라 (280°)
안전하게 → 기존 유지하고 그림자만 개선
```

---

## 🔗 관련 문서

### 프로젝트 문서

- [AGENTS.md](../AGENTS.md) - 프로젝트 아키텍처
- [copilot-instructions.md](../.github/copilot-instructions.md) - 개발 컨벤션

### MUI 공식 문서

- [Theming](https://mui.com/material-ui/customization/theming/)
- [Color Schemes](https://mui.com/material-ui/customization/palette/#color-schemes)
- [Typography](https://mui.com/material-ui/customization/typography/)

### 디자인 리소스

- [Coolors.co](https://coolors.co/) - 색상 팔레트
- [Material Design Color Tool](https://material.io/resources/color/)
- [HSL Color Picker](https://hslpicker.com/)

---

## 📞 문의 및 피드백

테마 개선 후:

1. 스크린샷 찍기
2. Before/After 비교
3. 팀원 피드백 받기
4. 필요시 롤백 또는 조정

---

## ⚡ TL;DR (한 줄 요약)

| 문서                       | 한 줄 요약                        |
| -------------------------- | --------------------------------- |
| THEME_IMPROVEMENT_GUIDE.md | 모든 개선 옵션과 상세 코드        |
| THEME_QUICK_START.md       | 5분 안에 적용 가능한 3가지 스타일 |
| THEME_VISUAL_COMPARISON.md | Before/After 비교와 추천 조합     |
| THEME_INDEX.md (현재)      | 문서 네비게이션 및 빠른 시작      |

---

**🚀 지금 바로 시작하기**: [빠른 시작 가이드](./THEME_QUICK_START.md)
