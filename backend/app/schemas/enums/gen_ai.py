"""Generative AI Domain Enums"""

from enum import Enum


class PromptStatus(str, Enum):
    """프롬프트 템플릿 상태"""

    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class PromptRiskLevel(str, Enum):
    """프롬프트 위험도"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ReportFormat(str, Enum):
    """리포트 출력 형식"""

    MARKDOWN = "markdown"
    HTML = "html"
    PDF = "pdf"
    JSON = "json"


class ReportSectionType(str, Enum):
    """리포트 섹션 유형"""

    EXECUTIVE_SUMMARY = "executive_summary"
    PERFORMANCE_ANALYSIS = "performance_analysis"
    STRATEGY_INSIGHTS = "strategy_insights"
    RISK_ASSESSMENT = "risk_assessment"
    MARKET_CONTEXT = "market_context"
    RECOMMENDATIONS = "recommendations"


class ReportRecommendation(str, Enum):
    """리포트 추천 액션"""

    PROCEED = "proceed"
    OPTIMIZE = "optimize"
    REJECT = "reject"
    RESEARCH = "research"


class ChatCommandType(str, Enum):
    """챗봇 명령어 타입"""

    ANALYZE_BACKTEST = "analyze_backtest"
    OPTIMIZE_STRATEGY = "optimize_strategy"
    CHECK_DATA_QUALITY = "check_data_quality"
    EXPLAIN_RESULT = "explain_result"


class ConversationRole(str, Enum):
    """대화 역할"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class IntentType(str, Enum):
    """사용자 의도 유형"""

    CREATE_STRATEGY = "create_strategy"
    MODIFY_STRATEGY = "modify_strategy"
    EXPLAIN_STRATEGY = "explain_strategy"
    RECOMMEND_PARAMETERS = "recommend_parameters"
    OPTIMIZE_STRATEGY = "optimize_strategy"
