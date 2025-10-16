"""
Template seeding utilities for strategy service
"""

import json
import logging
from pathlib import Path
from typing import Any

from app.models.trading.strategy import StrategyTemplate, StrategyType
from app.strategies.configs import (
    SMACrossoverConfig,
    RSIMeanReversionConfig,
    MomentumConfig,
    BuyAndHoldConfig,
)

logger = logging.getLogger(__name__)


class TemplateSeeder:
    """Strategy template seeding utility"""

    def __init__(self):
        # Navigate from app/utils/ to app/seed_templates/
        self.templates_dir = Path(__file__).parent.parent / "seed_templates"
        self.template_files = {
            "standard_buy_and_hold.json": StrategyType.BUY_AND_HOLD,
            "balanced_momentum.json": StrategyType.MOMENTUM,
            "conservative_sma_crossover.json": StrategyType.SMA_CROSSOVER,
            "standard_rsi_mean_reversion.json": StrategyType.RSI_MEAN_REVERSION,
        }

    async def seed_templates(self) -> None:
        """Seed strategy templates from JSON files"""
        logger.info("Starting template seeding...")

        if not self.templates_dir.exists():
            logger.warning(f"Templates directory not found: {self.templates_dir}")
            return

        # 기존 템플릿들 삭제 (스키마 변경으로 인한 호환성 문제 해결)
        try:
            deleted_count = await StrategyTemplate.delete_all()
            logger.info(f"Deleted {deleted_count} existing templates for fresh seeding")
        except Exception as e:
            logger.warning(f"Failed to delete existing templates: {e}")

        seeded_count = 0
        for template_file, strategy_type in self.template_files.items():
            try:
                await self._seed_single_template(template_file, strategy_type)
                seeded_count += 1
            except Exception as e:
                logger.error(f"Failed to seed template {template_file}: {e}")

        logger.info(
            f"✅ Template seeding completed. {seeded_count}/{len(self.template_files)} templates processed"
        )

    async def _seed_single_template(
        self, filename: str, strategy_type: StrategyType
    ) -> None:
        """Seed a single template file"""
        template_path = self.templates_dir / filename

        if not template_path.exists():
            logger.warning(f"Template file not found: {template_path}")
            return

        try:
            with open(template_path, "r", encoding="utf-8") as f:
                template_data = json.load(f)

            # 디버깅: JSON 데이터 구조 확인
            logger.info(f"Template data keys: {list(template_data.keys())}")
            logger.info(f"Category value: {template_data.get('category', 'NOT_FOUND')}")
            logger.info(
                f"Difficulty value: {template_data.get('difficulty', 'NOT_FOUND')}"
            )

            # parameters를 config_type을 포함한 default_config로 변환
            parameters = template_data.get("parameters", {})
            default_config = self._build_default_config(strategy_type, parameters)

            # Create new template
            template = StrategyTemplate(
                name=template_data["name"],
                strategy_type=strategy_type,
                description=template_data["description"],
                default_config=default_config,
                tags=template_data.get("tags", []),
                category=template_data.get("category", "trading"),
                difficulty=template_data.get("difficulty", "intermediate"),
            )

            await template.insert()
            logger.info(f"✅ Seeded template: {template_data['name']} ({strategy_type})")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in template file {filename}: {e}")
        except KeyError as e:
            logger.error(f"Missing required field in template {filename}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error seeding template {filename}: {e}")

    def _build_default_config(
        self, strategy_type: StrategyType, parameters: dict[str, Any]
    ):
        """Build default_config from parameters based on strategy type"""
        # 공통 기본값
        common_defaults = {
            "lookback_period": 252,
            "min_data_points": 30,
            "max_position_size": 1.0,
        }

        # 전략별 Config 클래스 인스턴스 생성
        if strategy_type == StrategyType.SMA_CROSSOVER:
            return SMACrossoverConfig(
                config_type="sma_crossover",
                **common_defaults,
                **parameters,
            )
        elif strategy_type == StrategyType.RSI_MEAN_REVERSION:
            return RSIMeanReversionConfig(
                config_type="rsi_mean_reversion",
                **common_defaults,
                **parameters,
            )
        elif strategy_type == StrategyType.MOMENTUM:
            return MomentumConfig(
                config_type="momentum",
                **common_defaults,
                **parameters,
            )
        elif strategy_type == StrategyType.BUY_AND_HOLD:
            return BuyAndHoldConfig(
                config_type="buy_and_hold",
                **common_defaults,
                **parameters,
            )
        else:
            raise ValueError(f"Unknown strategy type: {strategy_type}")


async def seed_strategy_templates() -> None:
    """Public interface for seeding templates"""
    seeder = TemplateSeeder()
    await seeder.seed_templates()
