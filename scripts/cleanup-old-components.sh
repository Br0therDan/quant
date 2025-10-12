#!/bin/bash

# 이 스크립트는 -old.tsx 파일들을 제거합니다
# 작업 완료 후 실행하세요: ./scripts/cleanup-old-components.sh

echo "🧹 -old.tsx 파일 정리 시작..."

# 워치리스트 관련 컴포넌트
OLD_FILES=(
  "frontend/src/components/watchlists/CreateWatchlistDialog-old.tsx"
  "frontend/src/components/watchlists/WatchlistCard-old.tsx"
  "frontend/src/components/market-data/WatchlistBar-old.tsx"
)

for file in "${OLD_FILES[@]}"; do
  if [ -f "$file" ]; then
    echo "  ❌ 삭제: $file"
    rm "$file"
  else
    echo "  ⚠️  파일 없음: $file"
  fi
done

echo "✅ 정리 완료!"
echo ""
echo "📝 참고: 다음 파일들은 새로운 컴포넌트로 대체되었습니다:"
echo "  - MarketDataSidebar.tsx (새로운 통합 사이드바)"
echo "  - WatchlistEditDialog.tsx (워치리스트 편집 다이얼로그)"
