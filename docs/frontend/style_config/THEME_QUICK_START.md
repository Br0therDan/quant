# 테마 개선 빠른 적용 가이드

> 5분 안에 시각적 변화를 확인할 수 있는 빠른 적용 가이드

## 🎨 옵션 1: 모던 핀테크 스타일 (추천)

### 1️⃣ 색상 변경 (2분)

**파일**: `frontend/src/components/shared-theme/themePrimitives.ts`

```typescript
// 기존 brand 색상을 찾아서 교체
export const brand = {
  50: "hsl(200, 95%, 97%)",
  100: "hsl(200, 93%, 94%)",
  200: "hsl(200, 95%, 86%)",
  300: "hsl(200, 96%, 73%)",
  400: "hsl(200, 95%, 61%)",
  500: "hsl(200, 98%, 48%)",
  600: "hsl(200, 100%, 39%)",
  700: "hsl(200, 100%, 31%)",
  800: "hsl(200, 100%, 23%)",
  900: "hsl(200, 100%, 15%)",
};

// gray도 약간 조정 (옵션)
export const gray = {
  50: "hsl(210, 25%, 98%)", // 약간 파란 느낌
  100: "hsl(210, 20%, 95%)",
  200: "hsl(210, 18%, 88%)",
  300: "hsl(210, 16%, 80%)",
  400: "hsl(210, 14%, 65%)",
  500: "hsl(210, 12%, 42%)",
  600: "hsl(210, 14%, 35%)",
  700: "hsl(210, 16%, 25%)",
  800: "hsl(210, 20%, 12%)",
  900: "hsl(210, 25%, 8%)",
};
```

### 2️⃣ 둥근 모서리 개선 (1분)

**파일**: `frontend/src/components/shared-theme/themePrimitives.ts`

```typescript
// shape 객체 찾아서 수정
export const shape = {
  borderRadius: 12, // 8에서 12로 증가
};
```

### 3️⃣ 그림자 개선 (2분)

**파일**: `frontend/src/components/shared-theme/themePrimitives.ts`

```typescript
// getDesignTokens 함수 내부의 baseShadow 수정
export const colorSchemes = {
  light: {
    palette: {
      // ... 기존 설정
      baseShadow:
        "0px 2px 4px -1px rgba(0, 0, 0, 0.06), 0px 4px 8px -2px rgba(0, 0, 0, 0.10)",
    },
  },
  dark: {
    palette: {
      // ... 기존 설정
      baseShadow:
        "0px 4px 8px -2px rgba(0, 0, 0, 0.3), 0px 8px 16px -4px rgba(0, 0, 0, 0.4)",
    },
  },
};
```

---

## 🌙 옵션 2: 프리미엄 다크 네이비

### 색상만 변경 (2분)

**파일**: `frontend/src/components/shared-theme/themePrimitives.ts`

```typescript
export const brand = {
  50: "hsl(220, 60%, 97%)",
  100: "hsl(220, 58%, 94%)",
  200: "hsl(220, 60%, 86%)",
  300: "hsl(220, 61%, 73%)",
  400: "hsl(220, 59%, 61%)",
  500: "hsl(220, 61%, 48%)",
  600: "hsl(220, 65%, 39%)",
  700: "hsl(220, 70%, 31%)",
  800: "hsl(220, 75%, 23%)",
  900: "hsl(220, 80%, 15%)",
};

// 다크모드 배경 개선
export const colorSchemes = {
  // ... light 설정
  dark: {
    palette: {
      // ... 기존 색상 설정
      background: {
        default: "hsl(220, 40%, 8%)",
        paper: "hsl(220, 35%, 12%)",
      },
    },
  },
};
```

---

## 🎯 옵션 3: 그라디언트 & 글래스모피즘 (고급)

### 1️⃣ 커스텀 테마 속성 추가

**파일**: `frontend/src/components/shared-theme/themePrimitives.ts`

```typescript
// 파일 상단에 declare module 추가
declare module "@mui/material/styles" {
  interface Palette {
    baseShadow: string;
    gradient: {
      primary: string;
      secondary: string;
      glass: string;
    };
  }
}

// colorSchemes에 gradient 추가
export const colorSchemes = {
  light: {
    palette: {
      // ... 기존 설정
      gradient: {
        primary:
          "linear-gradient(135deg, hsl(200, 95%, 61%) 0%, hsl(200, 100%, 39%) 100%)",
        secondary:
          "linear-gradient(135deg, hsl(220, 35%, 97%) 0%, hsl(220, 30%, 94%) 100%)",
        glass:
          "linear-gradient(135deg, rgba(255, 255, 255, 0.8) 0%, rgba(255, 255, 255, 0.5) 100%)",
      },
    },
  },
  dark: {
    palette: {
      // ... 기존 설정
      gradient: {
        primary:
          "linear-gradient(135deg, hsl(200, 95%, 65%) 0%, hsl(200, 100%, 45%) 100%)",
        secondary:
          "linear-gradient(135deg, hsl(220, 40%, 20%) 0%, hsl(220, 35%, 12%) 100%)",
        glass:
          "linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.02) 100%)",
      },
    },
  },
};
```

### 2️⃣ Card 컴포넌트에 적용

**파일**: `frontend/src/components/shared-theme/customizations/surfaces.ts`

```typescript
MuiCard: {
  styleOverrides: {
    root: ({ theme }) => ({
      // ... 기존 설정
      background: theme.palette.mode === 'dark'
        ? theme.palette.gradient.glass
        : theme.palette.background.paper,
      backdropFilter: theme.palette.mode === 'dark' ? 'blur(10px)' : 'none',
      border: `1px solid ${alpha(
        theme.palette.divider,
        theme.palette.mode === 'dark' ? 0.3 : 1
      )}`,
    }),
  },
},
```

---

## ⚡ 즉시 확인할 수 있는 변화

### Before → After

| 요소          | 변경 전          | 변경 후                     |
| ------------- | ---------------- | --------------------------- |
| 브랜드 색상   | 기본 파랑 (210°) | 시안 (200°) / 네이비 (220°) |
| 둥근 모서리   | 8px              | 12px (더 부드러운)          |
| 그림자        | 단순             | 레이어드 (입체감)           |
| 다크모드 배경 | gray[900]        | 깊은 네이비                 |

---

## 🧪 테스트 페이지

빠르게 변화를 확인하려면:

1. **메인 대시보드**: 카드, 버튼 스타일 확인
2. **Market Data 페이지**: 사이드바, 리스트 확인
3. **차트 페이지**: 다크모드 배경 확인
4. **다크모드 토글**: Header의 ColorModeIconDropdown 클릭

---

## 🔄 롤백 방법

변경이 마음에 들지 않으면:

```bash
cd /Users/donghakim/quant/frontend/src/components/shared-theme
git checkout themePrimitives.ts
```

---

## 📊 성능 영향

위 변경사항은 **런타임 성능에 영향 없음**:

- ✅ 정적 색상 값만 변경
- ✅ CSS 변수 사용으로 효율적
- ✅ 브라우저 리페인트 최소화

---

## 🎨 더 많은 옵션이 필요하면?

`THEME_IMPROVEMENT_GUIDE.md` 참고:

- 타이포그래피 개선
- 애니메이션 추가
- 차트 전용 색상
- 그라디언트 효과
- 글로우 효과
