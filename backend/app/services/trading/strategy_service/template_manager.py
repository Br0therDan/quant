"""
Strategy Template Management
"""

import logging
from datetime import datetime
from typing import Any

from app.core.config import get_settings
from app.models.trading.strategy import (
    Strategy,
    StrategyTemplate,
    StrategyType,
    StrategyConfigUnion,
)

logger = logging.getLogger(__name__)


class TemplateManager:
    """Strategy template management handler"""

    def __init__(self):
        self.settings = get_settings()

    async def create_template(
        self,
        name: str,
        strategy_type: StrategyType,
        description: str,
        default_config: StrategyConfigUnion,
        category: str = "general",
        tags: list[str] | None = None,
    ) -> StrategyTemplate:
        """Create strategy template

        Args:
            name: Template name
            strategy_type: Type of strategy
            description: Template description
            default_config: Default configuration
            category: Template category
            tags: Optional tags

        Returns:
            Created template
        """
        template = StrategyTemplate(
            name=name,
            strategy_type=strategy_type,
            description=description,
            default_config=default_config,
            category=category,
            tags=tags or [],
        )

        await template.insert()
        logger.info(f"Created template: {name}")
        return template

    async def get_templates(
        self,
        strategy_type: StrategyType | None = None,
    ) -> list[StrategyTemplate]:
        """Get strategy templates

        Args:
            strategy_type: Optional filter by strategy type

        Returns:
            List of strategy templates
        """
        query = {}
        if strategy_type:
            query["strategy_type"] = strategy_type

        templates = await StrategyTemplate.find(query).to_list()
        return templates

    async def get_template_by_id(self, template_id: str) -> StrategyTemplate | None:
        """Get template by ID

        Args:
            template_id: Template ID

        Returns:
            Template if found, None otherwise
        """
        try:
            template = await StrategyTemplate.get(template_id)
            return template
        except Exception as e:
            logger.error(f"Failed to get template {template_id}: {e}")
            return None

    async def update_template(
        self,
        template_id: str,
        name: str | None = None,
        description: str | None = None,
        default_config: StrategyConfigUnion | None = None,
        category: str | None = None,
        tags: list[str] | None = None,
    ) -> StrategyTemplate | None:
        """Update template by ID

        Args:
            template_id: Template ID
            name: Optional new name
            description: Optional new description
            default_config: Optional new default configuration
            category: Optional new category
            tags: Optional new tags

        Returns:
            Updated template if found, None otherwise
        """
        try:
            template = await StrategyTemplate.get(template_id)
            if not template:
                return None

            # Update fields if provided
            if name is not None:
                template.name = name
            if description is not None:
                template.description = description
            if default_config is not None:
                template.default_config = default_config
            if category is not None:
                template.category = category
            if tags is not None:
                template.tags = tags

            # Update timestamp
            template.updated_at = datetime.now()
            await template.save()

            logger.info(f"Template {template_id} updated successfully")
            return template
        except Exception as e:
            logger.error(f"Failed to update template {template_id}: {e}")
            return None

    async def delete_template(self, template_id: str) -> bool:
        """Delete template by ID

        Args:
            template_id: Template ID

        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            template = await StrategyTemplate.get(template_id)
            if not template:
                return False

            await template.delete()
            logger.info(f"Template {template_id} deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to delete template {template_id}: {e}")
            return False

    async def create_strategy_from_template(
        self,
        template_id: str,
        name: str,
        strategy_type: StrategyType,
        parameter_overrides: dict[str, Any] | None = None,
        user_id: str | None = None,
        create_strategy_func=None,
    ) -> Strategy | None:
        """Create strategy instance from template

        Args:
            template_id: Template ID
            name: Strategy name
            strategy_type: Strategy type
            parameter_overrides: Optional parameter overrides
            user_id: Optional user ID
            create_strategy_func: Function to create strategy (injected dependency)

        Returns:
            Created strategy if successful, None otherwise
        """
        try:
            template = await StrategyTemplate.get(template_id)
            if not template:
                return None

            # Use template config or merge with overrides
            config = template.default_config
            if parameter_overrides:
                # Use Pydantic model_copy to update config
                config = template.default_config.model_copy(update=parameter_overrides)

            # Increment template usage
            template.usage_count += 1
            await template.save()

            # Create strategy using injected function
            if create_strategy_func is None:
                logger.error("create_strategy_func not provided")
                return None

            strategy = await create_strategy_func(
                name=name,
                strategy_type=strategy_type,
                description=f"Created from template: {template.name}",
                config=config,
                tags=template.tags,
                user_id=user_id,
            )

            return strategy

        except Exception as e:
            logger.error(f"Failed to create strategy from template: {e}")
            return None
