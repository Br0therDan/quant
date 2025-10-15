"""ChatOps API endpoints for operational diagnostics."""

from fastapi import APIRouter

from app.schemas.gen_ai.chatops import ChatOpsRequest, ChatOpsResponse
from app.services.service_factory import service_factory

router = APIRouter(tags=["ChatOps"])


@router.post("/", response_model=ChatOpsResponse)
async def execute_chatops(request: ChatOpsRequest) -> ChatOpsResponse:
    """Execute the ChatOps agent with the provided request payload."""

    agent = service_factory.get_chatops_agent()
    result = await agent.run(request.question, request.user_roles)

    return ChatOpsResponse(
        answer=result.answer,
        used_tools=result.used_tools,
        denied_tools=result.denied_tools,
        cache_status=result.cache_status,
        data_quality=result.data_quality,
        recent_failures=result.recent_failures,
        external_services=result.external_services,
    )


__all__ = ["router"]
