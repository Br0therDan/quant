# 테마 스타일 개선 가이드

> 현재 테마 시스템을 기반으로 더욱 세련된 디자인을 구현하기 위한 가이드입니다.

## 📋 목차

1. [색상 팔레트 개선](#1-색상-팔레트-개선)
2. [타이포그래피 고도화](#2-타이포그래피-고도화)
3. [그림자 & 입체감](#3-그림자--입체감)
4. [둥근 모서리 & 간격](#4-둥근-모서리--간격)
5. [애니메이션 & 전환효과](#5-애니메이션--전환효과)
6. [다크모드 최적화](#6-다크모드-최적화)
7. [금융 차트 전용 색상](#7-금융-차트-전용-색상)

---

## 1. 색상 팔레트 개선

### 현재 상태

- **Brand**: 파란색 계열 (HSL 210도)
- **Gray**: 중성 회색
- **Success/Warning/Error**: 기본 녹색/주황/빨강

### 🎨 개선 방안

#### A. 모던한 브랜드 색상 (Financial/Tech 느낌)

**파일**: `frontend/src/components/shared-theme/themePrimitives.ts`

```typescript
// 옵션 1: 딥 블루 + 시안 (핀테크 느낌)
export const brand = {
  50: "hsl(200, 95%, 97%)",
  100: "hsl(200, 93%, 94%)",
  200: "hsl(200, 95%, 86%)",
  300: "hsl(200, 96%, 73%)",
  400: "hsl(200, 95%, 61%)", // Primary
  500: "hsl(200, 98%, 48%)",
  600: "hsl(200, 100%, 39%)",
  700: "hsl(200, 100%, 31%)",
  800: "hsl(200, 100%, 23%)",
  900: "hsl(200, 100%, 15%)",
};

// 옵션 2: 보라 + 핑크 (모던 그라디언트)
export const brand = {
  50: "hsl(280, 90%, 97%)",
  100: "hsl(280, 88%, 94%)",
  200: "hsl(280, 90%, 86%)",
  300: "hsl(280, 91%, 73%)",
  400: "hsl(280, 89%, 61%)", // Primary
  500: "hsl(280, 91%, 48%)",
  600: "hsl(280, 95%, 39%)",
  700: "hsl(280, 96%, 31%)",
  800: "hsl(280, 97%, 23%)",
  900: "hsl(280, 98%, 15%)",
};

// 옵션 3: 다크 네이비 + 골드 악센트 (프리미엄 느낌)
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

// 골드 악센트 추가
export const gold = {
  50: "hsl(45, 100%, 97%)",
  100: "hsl(45, 95%, 90%)",
  200: "hsl(45, 90%, 80%)",
  300: "hsl(45, 85%, 65%)",
  400: "hsl(45, 80%, 55%)",
  500: "hsl(45, 75%, 45%)",
  600: "hsl(45, 70%, 35%)",
  700: "hsl(45, 65%, 25%)",
  800: "hsl(45, 60%, 15%)",
  900: "hsl(45, 55%, 10%)",
};
```

#### B. 금융 차트용 의미론적 색상

```typescript
// 주식/차트 전용 색상 추가
export const financial = {
  // 상승 (녹색 계열)
  bullish: {
    light: "hsl(140, 70%, 50%)", // 라이트 모드
    dark: "hsl(140, 65%, 55%)", // 다크 모드
    gradient: "linear-gradient(135deg, hsl(140, 70%, 50%), hsl(140, 80%, 40%))",
  },
  // 하락 (빨강 계열)
  bearish: {
    light: "hsl(0, 75%, 55%)",
    dark: "hsl(0, 70%, 60%)",
    gradient: "linear-gradient(135deg, hsl(0, 75%, 55%), hsl(0, 85%, 45%))",
  },
  // 중립
  neutral: {
    light: "hsl(220, 15%, 60%)",
    dark: "hsl(220, 15%, 65%)",
  },
  // 차트 그리드
  grid: {
    light: "hsla(220, 20%, 80%, 0.3)",
    dark: "hsla(220, 20%, 20%, 0.5)",
  },
};
```

---

## 2. 타이포그래피 고도화

### 현재 상태

- Roboto 폰트 단일 사용
- 기본적인 h1~h6, body1~2 정의

### ✍️ 개선 방안

**파일**: `frontend/src/components/shared-theme/themePrimitives.ts`

```typescript
// 다중 폰트 시스템
export const typography = {
  // 본문용 폰트
  fontFamily:
    "var(--font-roboto), 'Roboto', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",

  // 숫자/데이터용 모노스페이스 폰트
  fontFamilyMonospace: "'JetBrains Mono', 'Fira Code', 'Consolas', monospace",

  // 제목용 폰트 (옵션)
  fontFamilyDisplay: "'Inter', var(--font-roboto), sans-serif",

  h1: {
    fontSize: "clamp(2.5rem, 5vw, 3.5rem)", // 반응형 크기
    fontWeight: 700,
    lineHeight: 1.1,
    letterSpacing: "-0.02em",
    fontFamily: "'Inter', var(--font-roboto), sans-serif", // Display 폰트
  },
  h2: {
    fontSize: "clamp(2rem, 4vw, 2.75rem)",
    fontWeight: 700,
    lineHeight: 1.2,
    letterSpacing: "-0.01em",
  },
  h3: {
    fontSize: "clamp(1.75rem, 3vw, 2.25rem)",
    fontWeight: 600,
    lineHeight: 1.3,
  },
  h4: {
    fontSize: "clamp(1.5rem, 2.5vw, 1.875rem)",
    fontWeight: 600,
    lineHeight: 1.4,
  },
  h5: {
    fontSize: "clamp(1.25rem, 2vw, 1.5rem)",
    fontWeight: 600,
    lineHeight: 1.5,
  },
  h6: {
    fontSize: "clamp(1.125rem, 1.5vw, 1.25rem)",
    fontWeight: 600,
    lineHeight: 1.6,
  },

  // 본문 텍스트
  body1: {
    fontSize: "1rem",
    lineHeight: 1.7,
    letterSpacing: "0.01em",
  },
  body2: {
    fontSize: "0.875rem",
    lineHeight: 1.6,
    letterSpacing: "0.01em",
  },

  // 숫자/데이터 표시용 (추가)
  dataDisplay: {
    fontSize: "1.125rem",
    fontWeight: 500,
    fontFamily: "'JetBrains Mono', monospace",
    letterSpacing: "-0.01em",
  },

  // 작은 라벨
  caption: {
    fontSize: "0.75rem",
    lineHeight: 1.5,
    letterSpacing: "0.03em",
    textTransform: "uppercase" as const,
  },

  // 버튼 텍스트
  button: {
    fontSize: "0.875rem",
    fontWeight: 600,
    letterSpacing: "0.02em",
    textTransform: "none" as const,
  },
};
```

#### 폰트 추가 방법

**파일**: `frontend/src/app/layout.tsx`

```typescript
import { Roboto, Inter, JetBrains_Mono } from "next/font/google";

const roboto = Roboto({
  weight: ["300", "400", "500", "700"],
  subsets: ["latin"],
  display: "swap",
  variable: "--font-roboto",
});

const inter = Inter({
  weight: ["400", "500", "600", "700"],
  subsets: ["latin"],
  display: "swap",
  variable: "--font-inter",
});

const jetbrainsMono = JetBrains_Mono({
  weight: ["400", "500", "600"],
  subsets: ["latin"],
  display: "swap",
  variable: "--font-jetbrains-mono",
});

// HTML 태그에 적용
<html
  lang="en"
  suppressHydrationWarning
  className={`${roboto.variable} ${inter.variable} ${jetbrainsMono.variable}`}
>
```

---

## 3. 그림자 & 입체감

### 현재 상태

- 기본 MUI shadows 사용
- baseShadow만 커스터마이징

### 🌑 개선 방안

**파일**: `frontend/src/components/shared-theme/themePrimitives.ts`

```typescript
// 더 세련된 그림자 시스템
export const shadows: Shadows = [
  "none",

  // Shadow 1: 미세한 그림자 (hoverable elements)
  "0px 1px 2px 0px rgba(0, 0, 0, 0.05)",

  // Shadow 2: 약한 그림자 (cards)
  "0px 2px 4px -1px rgba(0, 0, 0, 0.06), 0px 4px 6px -1px rgba(0, 0, 0, 0.08)",

  // Shadow 3: 일반 그림자 (dropdowns)
  "0px 4px 6px -2px rgba(0, 0, 0, 0.05), 0px 10px 15px -3px rgba(0, 0, 0, 0.10)",

  // Shadow 4: 강한 그림자 (modals)
  "0px 10px 25px -5px rgba(0, 0, 0, 0.10), 0px 20px 40px -10px rgba(0, 0, 0, 0.15)",

  // Shadow 5: 매우 강한 그림자 (popovers)
  "0px 20px 40px -10px rgba(0, 0, 0, 0.15), 0px 30px 60px -20px rgba(0, 0, 0, 0.20)",

  // ... 나머지 그림자
  ...Array(19).fill("0px 2px 4px rgba(0, 0, 0, 0.08)"),
];

// 다크모드용 그림자 (더 강한 대비)
export const darkShadows: Shadows = [
  "none",
  "0px 1px 2px 0px rgba(0, 0, 0, 0.3)",
  "0px 2px 4px -1px rgba(0, 0, 0, 0.4), 0px 4px 6px -1px rgba(0, 0, 0, 0.5)",
  "0px 4px 6px -2px rgba(0, 0, 0, 0.5), 0px 10px 15px -3px rgba(0, 0, 0, 0.6)",
  "0px 10px 25px -5px rgba(0, 0, 0, 0.6), 0px 20px 40px -10px rgba(0, 0, 0, 0.7)",
  "0px 20px 40px -10px rgba(0, 0, 0, 0.7), 0px 30px 60px -20px rgba(0, 0, 0, 0.8)",
  ...Array(19).fill("0px 2px 4px rgba(0, 0, 0, 0.5)"),
];

// 글로우 효과 (액센트용)
export const glowEffects = {
  primary: "0 0 20px rgba(33, 150, 243, 0.3), 0 0 40px rgba(33, 150, 243, 0.1)",
  success: "0 0 20px rgba(76, 175, 80, 0.3), 0 0 40px rgba(76, 175, 80, 0.1)",
  error: "0 0 20px rgba(244, 67, 54, 0.3), 0 0 40px rgba(244, 67, 54, 0.1)",
  warning: "0 0 20px rgba(255, 152, 0, 0.3), 0 0 40px rgba(255, 152, 0, 0.1)",
};
```

---

## 4. 둥근 모서리 & 간격

### 현재 상태

- borderRadius: 8px (고정)
- 기본 spacing 사용

### 📐 개선 방안

**파일**: `frontend/src/components/shared-theme/themePrimitives.ts`

```typescript
export const shape = {
  // 다양한 둥근 정도
  borderRadius: 12, // 기본값 증가 (더 부드러운 느낌)

  // 추가 radius 옵션
  borderRadiusSmall: 6, // 작은 요소 (chips, badges)
  borderRadiusMedium: 12, // 중간 요소 (buttons, inputs)
  borderRadiusLarge: 16, // 큰 요소 (cards)
  borderRadiusXLarge: 24, // 매우 큰 요소 (modals)

  // 완전한 둥근 모서리
  borderRadiusPill: 9999, // 알약 모양 (pills, tags)
};

// Spacing 시스템 (8px 기반)
export const spacing = {
  unit: 8,
  xs: 4, // 0.5 * unit
  sm: 8, // 1 * unit
  md: 16, // 2 * unit
  lg: 24, // 3 * unit
  xl: 32, // 4 * unit
  xxl: 48, // 6 * unit
};
```

#### 사용 예시

```typescript
// 컴포넌트에서 사용
sx={{
  borderRadius: theme => theme.shape.borderRadiusLarge,
  padding: theme => theme.spacing(2), // 16px
  marginBottom: theme => theme.spacing(3), // 24px
}}
```

---

## 5. 애니메이션 & 전환효과

### 🎬 개선 방안

**파일**: `frontend/src/components/shared-theme/themePrimitives.ts`

```typescript
// 애니메이션 타이밍
export const transitions = {
  // Duration (지속 시간)
  duration: {
    shortest: 150,
    shorter: 200,
    short: 250,
    standard: 300,
    complex: 375,
    enteringScreen: 225,
    leavingScreen: 195,
  },

  // Easing (가속도 곡선)
  easing: {
    easeInOut: "cubic-bezier(0.4, 0, 0.2, 1)",
    easeOut: "cubic-bezier(0.0, 0, 0.2, 1)",
    easeIn: "cubic-bezier(0.4, 0, 1, 1)",
    sharp: "cubic-bezier(0.4, 0, 0.6, 1)",

    // 커스텀 easing (더 부드러운 느낌)
    smooth: "cubic-bezier(0.25, 0.46, 0.45, 0.94)",
    bounce: "cubic-bezier(0.68, -0.55, 0.265, 1.55)",
    spring: "cubic-bezier(0.175, 0.885, 0.32, 1.275)",
  },
};

// 자주 사용하는 transition 프리셋
export const commonTransitions = {
  // 부드러운 색상 변화
  color: `color 200ms cubic-bezier(0.4, 0, 0.2, 1)`,

  // 배경색 변화
  background: `background-color 250ms cubic-bezier(0.4, 0, 0.2, 1)`,

  // 그림자 변화
  shadow: `box-shadow 300ms cubic-bezier(0.4, 0, 0.2, 1)`,

  // Transform
  transform: `transform 250ms cubic-bezier(0.25, 0.46, 0.45, 0.94)`,

  // All (성능 주의)
  all: `all 250ms cubic-bezier(0.4, 0, 0.2, 1)`,

  // 호버 효과 (복합)
  hover: `
    background-color 200ms cubic-bezier(0.4, 0, 0.2, 1),
    box-shadow 200ms cubic-bezier(0.4, 0, 0.2, 1),
    transform 150ms cubic-bezier(0.25, 0.46, 0.45, 0.94)
  `,
};
```

#### Button 컴포넌트에 적용 예시

**파일**: `frontend/src/components/shared-theme/customizations/inputs.tsx`

```typescript
MuiButton: {
  styleOverrides: {
    root: ({ theme }) => ({
      transition: commonTransitions.hover,

      '&:hover': {
        transform: 'translateY(-2px)',
        boxShadow: theme.shadows[4],
      },

      '&:active': {
        transform: 'translateY(0)',
        transition: 'transform 100ms cubic-bezier(0.4, 0, 0.2, 1)',
      },
    }),
  },
},
```

---

## 6. 다크모드 최적화

### 현재 상태

- Light/Dark 모드 지원
- 기본적인 색상 반전

### 🌙 개선 방안

#### A. 더 세련된 다크모드 배경

**파일**: `frontend/src/components/shared-theme/themePrimitives.ts`

```typescript
export const colorSchemes = {
  light: {
    palette: {
      // ... 기존 라이트 모드 설정

      background: {
        default: "hsl(0, 0%, 99%)", // 순백에 가까운
        paper: "hsl(220, 35%, 98%)", // 약간 파란 느낌의 흰색
        elevated: "hsl(0, 0%, 100%)", // 순백 (카드 등)
      },
    },
  },
  dark: {
    palette: {
      // ... 기존 다크 모드 설정

      background: {
        // 옵션 1: 깊은 네이비 (금융 앱 느낌)
        default: "hsl(220, 40%, 8%)", // 매우 어두운 네이비
        paper: "hsl(220, 35%, 12%)", // 약간 밝은 네이비
        elevated: "hsl(220, 30%, 16%)", // 더 밝은 네이비 (카드)

        // 옵션 2: 순수 다크 그레이 (모던 느낌)
        // default: "hsl(0, 0%, 8%)",
        // paper: "hsl(0, 0%, 12%)",
        // elevated: "hsl(0, 0%, 16%)",

        // 옵션 3: 따뜻한 다크 (부드러운 느낌)
        // default: "hsl(25, 10%, 10%)",
        // paper: "hsl(25, 8%, 14%)",
        // elevated: "hsl(25, 6%, 18%)",
      },

      // 텍스트 대비 개선
      text: {
        primary: "hsl(0, 0%, 95%)", // 약간 어두운 흰색 (눈부심 방지)
        secondary: "hsl(220, 10%, 65%)", // 회색빛 텍스트
        disabled: "hsl(220, 10%, 45%)", // 비활성 텍스트
      },
    },
  },
};
```

#### B. 다크모드 전용 그라디언트

```typescript
export const gradients = {
  light: {
    primary:
      "linear-gradient(135deg, hsl(210, 98%, 48%) 0%, hsl(210, 100%, 35%) 100%)",
    secondary:
      "linear-gradient(135deg, hsl(220, 60%, 97%) 0%, hsl(220, 58%, 94%) 100%)",
    card: "linear-gradient(180deg, hsl(0, 0%, 100%) 0%, hsl(220, 35%, 98%) 100%)",
  },
  dark: {
    primary:
      "linear-gradient(135deg, hsl(210, 95%, 55%) 0%, hsl(210, 100%, 40%) 100%)",
    secondary:
      "linear-gradient(135deg, hsl(220, 40%, 20%) 0%, hsl(220, 35%, 12%) 100%)",
    card: "linear-gradient(180deg, hsl(220, 30%, 16%) 0%, hsl(220, 35%, 12%) 100%)",

    // 글래스모피즘 효과
    glass:
      "linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.01) 100%)",
  },
};
```

---

## 7. 금융 차트 전용 색상

### 📊 개선 방안

**파일**: `frontend/src/components/shared-theme/themePrimitives.ts`

```typescript
// 차트 전용 색상 팔레트
export const chartColors = {
  // 캔들스틱 차트
  candle: {
    up: {
      body: "hsl(140, 70%, 50%)", // 상승 캔들 몸통
      wick: "hsl(140, 70%, 40%)", // 상승 캔들 심지
      border: "hsl(140, 80%, 35%)", // 상승 캔들 테두리
    },
    down: {
      body: "hsl(0, 75%, 55%)",
      wick: "hsl(0, 75%, 45%)",
      border: "hsl(0, 85%, 40%)",
    },
  },

  // 볼륨 차트
  volume: {
    up: "hsla(140, 70%, 50%, 0.4)", // 상승 볼륨 (투명도)
    down: "hsla(0, 75%, 55%, 0.4)", // 하락 볼륨
  },

  // 인디케이터 라인
  indicators: {
    ma5: "hsl(280, 80%, 60%)", // 5일 이동평균 (보라)
    ma20: "hsl(45, 90%, 55%)", // 20일 이동평균 (노랑)
    ma60: "hsl(200, 80%, 50%)", // 60일 이동평균 (청록)
    ma120: "hsl(0, 80%, 60%)", // 120일 이동평균 (빨강)

    rsi: "hsl(280, 70%, 55%)", // RSI
    macd: "hsl(200, 75%, 50%)", // MACD
    signal: "hsl(0, 75%, 55%)", // Signal Line

    bb_upper: "hsl(200, 60%, 50%)", // 볼린저 밴드 상단
    bb_middle: "hsl(200, 50%, 60%)", // 볼린저 밴드 중간
    bb_lower: "hsl(200, 60%, 50%)", // 볼린저 밴드 하단
  },

  // 그리드 & 축
  grid: {
    light: "hsla(220, 20%, 80%, 0.2)", // 라이트 모드 그리드
    dark: "hsla(220, 20%, 40%, 0.2)", // 다크 모드 그리드
  },

  // 크로스헤어
  crosshair: {
    light: "hsla(210, 80%, 50%, 0.6)",
    dark: "hsla(210, 80%, 60%, 0.7)",
  },
};

// 데이터 시각화 색상 (다중 라인 차트용)
export const dataVizColors = [
  "hsl(210, 98%, 48%)", // 파랑
  "hsl(140, 70%, 50%)", // 녹색
  "hsl(280, 70%, 55%)", // 보라
  "hsl(45, 90%, 55%)", // 노랑
  "hsl(0, 75%, 55%)", // 빨강
  "hsl(180, 70%, 45%)", // 청록
  "hsl(320, 70%, 55%)", // 핑크
  "hsl(30, 80%, 50%)", // 주황
];
```

---

## 🚀 적용 방법

### 1단계: 색상 팔레트 변경

```typescript
// themePrimitives.ts에서 원하는 옵션 선택
export const brand = {
  // 옵션 1, 2, 3 중 선택하여 복사
};
```

### 2단계: 타이포그래피 개선

```typescript
// layout.tsx에 폰트 추가
const inter = Inter({ ... });
const jetbrainsMono = JetBrains_Mono({ ... });

// themePrimitives.ts에 fontFamily 업데이트
```

### 3단계: 그림자 & 애니메이션

```typescript
// themePrimitives.ts에 shadows, transitions 추가
export const shadows = [ ... ];
export const transitions = { ... };
```

### 4단계: 컴포넌트별 적용

```typescript
// customizations/inputs.tsx 등에서
MuiButton: {
  styleOverrides: {
    root: {
      transition: commonTransitions.hover,
      // ...
    },
  },
},
```

---

## 📝 체크리스트

- [ ] 브랜드 색상 선택 및 적용
- [ ] 금융 차트 색상 정의
- [ ] 추가 폰트 로드 (Inter, JetBrains Mono)
- [ ] 타이포그래피 시스템 업데이트
- [ ] 그림자 시스템 개선
- [ ] 애니메이션 프리셋 정의
- [ ] 다크모드 배경 최적화
- [ ] 둥근 모서리 값 조정
- [ ] 각 컴포넌트에 transition 적용
- [ ] 차트 컴포넌트에 새 색상 적용

---

## 💡 추가 팁

### 색상 선택 도구

- [Coolors.co](https://coolors.co/) - 색상 팔레트 생성
- [HSL Color Picker](https://hslpicker.com/) - HSL 값 조정
- [Material Design Color Tool](https://material.io/resources/color/) - 접근성
  체크

### 폰트 조합

- **Display + Body**: Inter + Roboto
- **Tech 느낌**: JetBrains Mono + Inter
- **Modern**: Poppins + Open Sans

### 다크모드 테스트

- 명암비 최소 4.5:1 유지 (WCAG AA)
- 순백(#FFFFFF) 피하기 (눈부심)
- 순흑(#000000) 피하기 (대비 과다)

---

## 🎯 우선순위 추천

1. **즉시 적용**: 브랜드 색상 변경 (가장 큰 시각적 임팩트)
2. **단기**: 그림자 & 둥근 모서리 개선
3. **중기**: 타이포그래피 시스템 고도화
4. **장기**: 애니메이션 & 인터랙션 세밀화
