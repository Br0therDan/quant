"""
Template seeding utilities for strategy service
"""

import json
import logging
from pathlib import Path
from typing import Any

from app.models.strategy import StrategyTemplate, StrategyType

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

            # Create new template
            template = StrategyTemplate(
                name=template_data["name"],
                strategy_type=strategy_type,
                description=template_data["description"],
                default_parameters=template_data["parameters"],
                tags=template_data.get("tags", []),
                category=template_data.get("category", "trading"),  # 기본 카테고리 추가
                difficulty=template_data.get("difficulty", "intermediate"),  # 기본 난이도 추가
                parameter_schema=self._generate_parameter_schema(
                    strategy_type, template_data["parameters"]
                ),
            )

            await template.insert()
            logger.info(f"✅ Seeded template: {template_data['name']} ({strategy_type})")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in template file {filename}: {e}")
        except KeyError as e:
            logger.error(f"Missing required field in template {filename}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error seeding template {filename}: {e}")

    def _generate_parameter_schema(
        self, strategy_type: StrategyType, parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """Generate parameter schema for validation"""
        schema = {"type": "object", "properties": {}, "required": []}

        # Generate schema based on strategy type and parameters
        for param_name, param_value in parameters.items():
            param_schema = self._infer_parameter_schema(param_name, param_value)
            schema["properties"][param_name] = param_schema

        # Add strategy-specific schema requirements
        if strategy_type == StrategyType.SMA_CROSSOVER:
            schema["properties"].update(
                {
                    "short_window": {"type": "integer", "minimum": 2, "maximum": 50},
                    "long_window": {"type": "integer", "minimum": 10, "maximum": 200},
                }
            )
        elif strategy_type == StrategyType.RSI_MEAN_REVERSION:
            schema["properties"].update(
                {
                    "rsi_period": {"type": "integer", "minimum": 2, "maximum": 50},
                    "oversold_threshold": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 50,
                    },
                    "overbought_threshold": {
                        "type": "number",
                        "minimum": 50,
                        "maximum": 100,
                    },
                }
            )
        elif strategy_type == StrategyType.MOMENTUM:
            schema["properties"].update(
                {
                    "momentum_period": {
                        "type": "integer",
                        "minimum": 5,
                        "maximum": 100,
                    },
                    "price_change_threshold": {
                        "type": "number",
                        "minimum": 0.001,
                        "maximum": 0.1,
                    },
                }
            )

        return schema

    def _infer_parameter_schema(
        self, param_name: str, param_value: Any
    ) -> dict[str, Any]:
        """Infer schema from parameter value"""
        if isinstance(param_value, bool):
            return {"type": "boolean", "default": param_value}
        elif isinstance(param_value, int):
            return {"type": "integer", "default": param_value}
        elif isinstance(param_value, float):
            return {"type": "number", "default": param_value}
        elif isinstance(param_value, str):
            return {"type": "string", "default": param_value}
        elif param_value is None:
            return {"type": ["null", "integer", "number", "string"], "default": None}
        else:
            return {"type": "object", "default": param_value}


async def seed_strategy_templates() -> None:
    """Public interface for seeding templates"""
    seeder = TemplateSeeder()
    await seeder.seed_templates()
