# Feature Engineer Modularization Plan (Phase 2.2b)

## Current State

**File**: `backend/app/services/ml_platform/infrastructure/feature_engineer.py`  
**Size**: 257 lines  
**Class**: `FeatureEngineer`  
**Purpose**: Technical indicator calculation for ML feature engineering

### Current Methods (8 methods)

1. `__init__()` - Configuration (13 lines)
2. `calculate_technical_indicators()` - Main pipeline (22 lines)
3. `_calculate_rsi()` - RSI calculation (15 lines)
4. `_calculate_macd()` - MACD calculation (12 lines)
5. `_calculate_bollinger_bands()` - Bollinger Bands (21 lines)
6. `_calculate_moving_averages()` - SMA/EMA (13 lines)
7. `_calculate_volume_indicators()` - Volume indicators (17 lines)
8. `_calculate_price_changes()` - Price changes (13 lines)
9. `get_feature_columns()` - Feature list (30 lines)
10. `prepare_training_data()` - X/y split (23 lines)

### Current Features (26 indicators)

- **RSI**: `rsi` (1)
- **MACD**: `macd`, `macd_signal`, `macd_hist` (3)
- **Bollinger Bands**: `bb_upper`, `bb_middle`, `bb_lower`, `bb_width`, `bb_position` (5)
- **Moving Averages**: `sma_5`, `sma_10`, `sma_20`, `sma_50`, `ema_12`, `ema_26` (6)
- **Volume**: `volume_sma_20`, `volume_ratio`, `obv` (3)
- **Price Changes**: `price_change_1d`, `price_change_5d`, `price_change_20d`, `hl_range` (4)
- **OHLCV**: `open`, `high`, `low`, `close`, `volume` (5 - base data)

## Proposed Module Structure

### Directory Layout

```
backend/app/services/ml_platform/infrastructure/
└── feature_engineer/
    ├── __init__.py              # FeatureEngineer integration (120 lines)
    ├── indicator_rsi.py         # RSI calculator (25 lines)
    ├── indicator_macd.py        # MACD calculator (30 lines)
    ├── indicator_bollinger.py   # Bollinger Bands calculator (40 lines)
    ├── indicator_ma.py          # Moving Averages (SMA/EMA) (35 lines)
    ├── indicator_volume.py      # Volume indicators (35 lines)
    └── indicator_price.py       # Price change indicators (30 lines)
```

### Module Breakdown

#### 1. `indicator_rsi.py` (~25 lines)

```python
class RSICalculator:
    def __init__(self, period: int = 14):
        self.period = period
    
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate RSI indicator"""
        # RSI calculation logic
        return df
```

**Features**: `rsi`

#### 2. `indicator_macd.py` (~30 lines)

```python
class MACDCalculator:
    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        self.fast = fast
        self.slow = slow
        self.signal = signal
    
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate MACD, Signal, Histogram"""
        # MACD calculation logic
        return df
```

**Features**: `macd`, `macd_signal`, `macd_hist`

#### 3. `indicator_bollinger.py` (~40 lines)

```python
class BollingerBandsCalculator:
    def __init__(self, period: int = 20, std_dev: int = 2):
        self.period = period
        self.std_dev = std_dev
    
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Bollinger Bands (upper, middle, lower, width, position)"""
        # Bollinger Bands calculation logic
        return df
```

**Features**: `bb_upper`, `bb_middle`, `bb_lower`, `bb_width`, `bb_position`

#### 4. `indicator_ma.py` (~35 lines)

```python
class MovingAverageCalculator:
    def __init__(self, sma_periods: list[int] = [5, 10, 20, 50], ema_periods: list[int] = [12, 26]):
        self.sma_periods = sma_periods
        self.ema_periods = ema_periods
    
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate SMA and EMA for multiple periods"""
        # Moving averages calculation logic
        return df
```

**Features**: `sma_5`, `sma_10`, `sma_20`, `sma_50`, `ema_12`, `ema_26`

#### 5. `indicator_volume.py` (~35 lines)

```python
class VolumeIndicatorCalculator:
    def __init__(self, sma_period: int = 20):
        self.sma_period = sma_period
    
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate volume indicators (volume_sma, volume_ratio, OBV)"""
        # Volume indicators calculation logic
        return df
```

**Features**: `volume_sma_20`, `volume_ratio`, `obv`

#### 6. `indicator_price.py` (~30 lines)

```python
class PriceChangeCalculator:
    def __init__(self, periods: list[int] = [1, 5, 20]):
        self.periods = periods
    
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate price change rates and HL range"""
        # Price change calculation logic
        return df
```

**Features**: `price_change_1d`, `price_change_5d`, `price_change_20d`, `hl_range`

#### 7. `__init__.py` (~120 lines)

```python
class FeatureEngineer:
    """
    Unified Feature Engineering Service
    Delegates to specialized indicator calculators
    """
    
    def __init__(self):
        self.rsi_calc = RSICalculator()
        self.macd_calc = MACDCalculator()
        self.bb_calc = BollingerBandsCalculator()
        self.ma_calc = MovingAverageCalculator()
        self.volume_calc = VolumeIndicatorCalculator()
        self.price_calc = PriceChangeCalculator()
    
    # 10 methods:
    # - calculate_technical_indicators()  # Main pipeline
    # - get_feature_columns()             # Feature list
    # - prepare_training_data()           # X/y split
```

## Implementation Strategy

### Phase 2.2b Execution Steps

1. **Create directory structure**
   ```bash
   mkdir -p backend/app/services/ml_platform/infrastructure/feature_engineer
   ```

2. **Create indicator modules** (6 files)
   - `indicator_rsi.py`
   - `indicator_macd.py`
   - `indicator_bollinger.py`
   - `indicator_ma.py`
   - `indicator_volume.py`
   - `indicator_price.py`

3. **Create integration module**
   - `__init__.py` with `FeatureEngineer` class

4. **Backup legacy**
   ```bash
   mv feature_engineer.py feature_engineer_legacy.py
   ```

5. **Validate & commit**
   ```bash
   get_errors (7 modules)
   pnpm gen:client
   git commit "Phase 2.2b completion"
   ```

## Key Design Principles

### 1. Delegation Pattern (Consistent with Phase 2.1 & 2.2a)

- Each indicator has its own calculator class
- `FeatureEngineer` delegates to calculators
- Independently testable modules

### 2. Configuration Flexibility

- Each calculator accepts parameters in `__init__()`
- Default values match current implementation
- Easy to customize per strategy

### 3. Pandas DataFrame Pipeline

- All calculators accept/return `pd.DataFrame`
- Column-based feature engineering
- Consistent with current API

### 4. No Breaking Changes

- Public API remains identical
- `calculate_technical_indicators()` same signature
- `get_feature_columns()` same output
- `prepare_training_data()` same behavior

## Benefits

### Code Organization
- ✅ **Modularity**: 257 lines → 7 focused modules (~30-40 lines each)
- ✅ **Testability**: Each indicator independently testable
- ✅ **Maintainability**: Clear separation of concerns

### Performance
- ✅ **No overhead**: Direct delegation (no abstraction penalty)
- ✅ **Same algorithm**: Identical calculation logic

### Future Extensibility
- ✅ **Easy to add indicators**: Create new calculator module
- ✅ **Easy to customize**: Override calculator parameters
- ✅ **Easy to compose**: Mix and match indicators

## Risk Assessment

### Low Risk ✅
- Pure refactoring (no logic changes)
- Backward compatible API
- Same test coverage
- Type-safe with pandas stubs

### Mitigation
- Run existing tests after refactoring
- Verify OpenAPI schema unchanged
- Check frontend client generation

## Timeline

**Estimated**: 1-2 hours

- Module creation: 30 min
- Integration class: 20 min
- Testing & validation: 20 min
- Documentation & commit: 10 min

## Success Criteria

- ✅ All 7 modules created with no type errors
- ✅ `FeatureEngineer` API unchanged
- ✅ All existing tests pass
- ✅ OpenAPI client regenerated successfully
- ✅ Git commit with clear message

---

**Next Phase**: Phase 2.2c - `anomaly_detector.py` modularization (273 lines)
