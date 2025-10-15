#!/usr/bin/env bash
if [[ -z ${BASH_VERSINFO:-} || ${BASH_VERSINFO[0]} -lt 4 ]]; then
  echo "Requires bash >= 4" >&2
  exit 1
fi
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEST_DIR="$ROOT_DIR/backend/tests"

log() {
  printf '[phase0] %s\n' "$1"
}

ensure_dirs() {
  log 'Ensuring target directory structure exists'
  mkdir -p \
    "$TEST_DIR/domains/trading/api" \
    "$TEST_DIR/domains/trading/services" \
    "$TEST_DIR/domains/trading/strategies" \
    "$TEST_DIR/domains/market_data/api" \
    "$TEST_DIR/domains/market_data/services" \
    "$TEST_DIR/domains/ml_platform/api" \
    "$TEST_DIR/domains/ml_platform/services" \
    "$TEST_DIR/domains/gen_ai/api" \
    "$TEST_DIR/domains/gen_ai/services" \
    "$TEST_DIR/domains/user/api" \
    "$TEST_DIR/domains/user/services" \
    "$TEST_DIR/shared/fixtures"
}

migrate_files() {
  declare -A MOVES=(
    ["test_anomaly_detector.py"]="domains/ml_platform/services/test_anomaly_detector.py"
    ["test_data_processor.py"]="domains/market_data/services/test_data_processor.py"
    ["test_feature_engineer.py"]="domains/ml_platform/services/test_feature_engineer.py"
    ["test_ml_integration.py"]="domains/ml_platform/test_ml_e2e.py"
    ["test_ml_trainer.py"]="domains/ml_platform/services/test_ml_trainer.py"
    ["test_model_registry.py"]="domains/ml_platform/services/test_model_registry.py"
    ["test_orchestrator_integration.py"]="domains/trading/test_trading_e2e.py"
    ["test_strategy_config.py"]="domains/trading/strategies/test_strategy_config.py"
    ["test_strategy_executor.py"]="domains/trading/strategies/test_strategy_executor.py"
    ["test_trade_engine.py"]="domains/trading/services/test_trade_engine.py"
  )

  for SRC in "${!MOVES[@]}"; do
    DEST="${MOVES[$SRC]}"
    SRC_PATH="$TEST_DIR/$SRC"
    DEST_PATH="$TEST_DIR/$DEST"
    DEST_DIR="$(dirname "$DEST_PATH")"

    mkdir -p "$DEST_DIR"

    if [[ -f "$DEST_PATH" ]]; then
      log "Skipping $SRC → $DEST (already migrated)"
      continue
    fi

    if [[ -f "$SRC_PATH" ]]; then
      log "Moving $SRC → $DEST"
      mv "$SRC_PATH" "$DEST_PATH"
    else
      log "Source $SRC not found, skipping"
    fi
  done
}

main() {
  ensure_dirs
  migrate_files
  log 'Phase 0 migration complete'
}

main "$@"
