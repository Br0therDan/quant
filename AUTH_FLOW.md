좋습니다. 아래는 요구하신 내용을 기반으로 구성한 **Markdown 문서**입니다:

---

# 🔐 Next.js (Frontend) + FastAPI (Backend) 인증 전략 문서

이 문서는 **ID/PW 인증 + Google OAuth2 인증 혼용** 시 **효율적인 인증 흐름**을
설명하며, **Mermaid 시퀀스 다이어그램**을 통해 전체 흐름과 **디바이스 유형별
최적의 로그인 UX 전략**을 정리합니다.

---

## 📌 시스템 구성

- **Frontend**: Next.js (App Router, SSR + CSR 혼용)
- **Backend**: FastAPI (OAuth2 / JWT 기반 인증 처리)
- **DB**: PostgreSQL (Users, Sessions, OAuth Accounts 테이블 구성)
- **Auth Provider**: Google OAuth 2.0
- **Token 방식**: JWT (Access + Refresh)

---

## 1️⃣ 공통 인증 로직 (ID/PW + Google 로그인 혼용)

### 🎯 목적

- 사용자에게 **다양한 인증 옵션** 제공
- **프론트/백 간 역할 명확 분리** (FastAPI는 인증 처리, Next.js는 UI 처리)

### ✅ 인증 시나리오

- 사용자는 로그인 페이지에서 ID/PW 또는 Google 로그인을 선택
- ID/PW는 FastAPI의 `/auth/login` 엔드포인트로 직접 전달
- Google 로그인은 Next.js에서 OAuth2 인증 플로우를 시작 → 백엔드로 auth code
  전달 → 토큰 발급

### 🔁 공통 시퀀스 다이어그램 (Mermaid)

```mermaid
sequenceDiagram
    participant User
    participant Frontend (Web)
    participant Native App (Mobile)
    participant Backend (FastAPI)
    participant Google OAuth

    %% --- OAuth Flow: Start ---
    alt Web 로그인
        User->>Frontend (Web): "구글로 로그인" 클릭
        Frontend->>Google OAuth: redirect with code_challenge
        Google OAuth-->>Frontend (Web): Redirect (Auth Code)
        Frontend->>Backend: POST /auth/google { code, code_verifier }
    else Native 로그인
        User->>Native App (Mobile): "구글로 로그인" 클릭
        Native App->>Google OAuth: open system browser (with PKCE)
        Google OAuth-->>Native App (Mobile): redirect to custom URI (with code)
        Native App->>Backend: POST /auth/mobile/google { code, code_verifier }
    end

    %% --- Token Exchange ---
    Backend->>Google OAuth: POST /token (code + code_verifier + client_id)
    Google OAuth-->>Backend: access_token + id_token + user info

    %% --- Backend 처리 ---
    Backend->>Backend: 사용자 존재 여부 확인 / 생성
    Backend-->>Frontend (Web): JWT (Set-Cookie or JSON)
    Backend-->>Native App (Mobile): JWT (JSON for Secure Storage)

    %% --- 사용 이후 요청 ---
    Frontend (Web)->>Backend: 요청 (Authorization: Bearer <access_token>)
    Native App (Mobile)->>Backend: 요청 (Authorization: Bearer <access_token>)
    Backend->>Backend: JWT 검증 및 권한 처리

```

---

## 2️⃣ 디바이스별 UX 최적화 전략

기기마다 인증 경험을 최적화하기 위해 **UI/UX와 인증 처리 전략을 분리
설계**합니다.

---

### 💻 MacOS / Windows (Desktop Browser)

```mermaid
sequenceDiagram
    participant User
    participant Browser
    participant Next.js Server
    participant FastAPI Server
    participant Google OAuth

    %% -- Step 1: OAuth 요청 시작 --
    User->>Browser: "Google 로그인" 클릭
    Browser->>Next.js Server: GET /auth/google/start
    Next.js Server->>Google OAuth: Redirect to Google (Auth URL with code_challenge)

    %% -- Step 2: 인증 처리 & 리디렉션 --
    Google OAuth-->>Browser: Redirect to /auth/google/callback?code=XYZ
    Browser->>Next.js Server: GET /auth/google/callback?code=XYZ

    %% -- Step 3: Auth Code 전달 to FastAPI --
    Next.js Server->>FastAPI Server: POST /auth/google { code: XYZ, code_verifier }

    %% -- Step 4: FastAPI에서 토큰 교환 --
    FastAPI Server->>Google OAuth: POST /token { code, code_verifier, client_id, client_secret }
    Google OAuth-->>FastAPI Server: access_token, id_token, user info

    %% -- Step 5: JWT 발급 및 응답 --
    FastAPI Server->>FastAPI Server: 유저 존재 확인 or 생성
    FastAPI Server-->>Next.js Server: JWT (access + refresh)

    %% -- Step 6: 클라이언트 세션 저장 --
    Next.js Server-->>Browser: Set-Cookie: access_token, refresh_token (HttpOnly)
    Browser->>FastAPI Server: 이후 요청 시 Authorization: Bearer <access_token>


```

**특징 & 전략**

- 팝업 또는 새 탭에서 Google 로그인 → 사용자 흐름 방해 최소화
- JWT는 **HttpOnly 쿠키**로 전달해 XSS 대응
- 로컬 스토리지 대신 쿠키 저장 권장

---

### 📱 모바일앱 (네이티브)

```mermaid
sequenceDiagram
    participant User
    participant Native App
    participant FastAPI Server
    participant Google OAuth

    %% --- Step 1: 사용자 인증 시작 ---
    User->>Native App: 클릭 "구글 로그인"
    Native App->>Google OAuth: Launch system browser (OAuth URL with code_challenge)

    %% --- Step 2: 인증 후 리디렉션 ---
    Google OAuth-->>Native App: Redirect (custom URI with Auth Code)

    %% --- Step 3: Auth Code 전달 to 백엔드 ---
    Native App->>FastAPI Server: POST /auth/mobile/google { code, code_verifier }

    %% --- Step 4: 백엔드 → 토큰 교환 요청 ---
    FastAPI Server->>Google OAuth: POST /token { code, code_verifier, client_id }

    %% --- Step 5: 응답 및 JWT 발급 ---
    Google OAuth-->>FastAPI Server: access_token + id_token + user info
    FastAPI Server->>FastAPI Server: 사용자 DB 확인 or 생성
    FastAPI Server-->>Native App: JWT 발급 (access_token, optional refresh_token)

    %% --- Step 6: 인증 완료 후 앱 내 요청 ---
    Native App->>FastAPI Server: 요청 시 Authorization: Bearer <access_token>
    FastAPI Server->>FastAPI Server: JWT 검증 → 응답

```

**특징 & 전략**

- iOS는 팝업 제한 → **리디렉션 기반 OAuth2 권장**
- **Universal Links or Deep Links** 사용 시 native 앱 연동 가능
- In-App Browser 제한 대응 위해 **Safari로 강제 리디렉션 고려**

---
