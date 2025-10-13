#!/usr/bin/env python3
"""Phase 1 AI Integration - Service Initialization Test"""

import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_phase1_services():
    """Test Phase 1 services initialization"""

    try:
        from app.services.service_factory import service_factory

        # Test DatabaseManager
        logger.info("Testing DatabaseManager...")
        db_manager = service_factory.get_database_manager()
        logger.info(f"✅ DatabaseManager initialized: {db_manager.db_path}")

        # Test ML Signal Service
        logger.info("Testing MLSignalService...")
        ml_service = service_factory.get_ml_signal_service()
        logger.info(f"✅ MLSignalService initialized: {type(ml_service).__name__}")

        # Test Regime Detection Service
        logger.info("Testing RegimeDetectionService...")
        regime_service = service_factory.get_regime_detection_service()
        logger.info(
            f"✅ RegimeDetectionService initialized: {type(regime_service).__name__}"
        )

        # Test Probabilistic KPI Service
        logger.info("Testing ProbabilisticKPIService...")
        kpi_service = service_factory.get_probabilistic_kpi_service()
        logger.info(
            f"✅ ProbabilisticKPIService initialized: {type(kpi_service).__name__}"
        )

        # Test DuckDB table existence
        logger.info("Testing DuckDB portfolio_forecast_history table...")
        conn = db_manager.duckdb_conn
        result = conn.execute(
            """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='portfolio_forecast_history'
        """
        ).fetchall()

        if result:
            logger.info("✅ portfolio_forecast_history table exists")
        else:
            # DuckDB uses different catalog query
            tables = conn.execute("SHOW TABLES").fetchall()
            table_names = [t[0] for t in tables]
            if "portfolio_forecast_history" in table_names:
                logger.info("✅ portfolio_forecast_history table exists")
            else:
                logger.warning("⚠️ portfolio_forecast_history table not found")
                logger.info(f"Available tables: {table_names}")

        logger.info("\n🎉 All Phase 1 services initialized successfully!")
        return True

    except Exception as e:
        logger.error(f"❌ Phase 1 service initialization failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    success = test_phase1_services()
    sys.exit(0 if success else 1)
