"""
Watchlist API Routes
워치리스트 관리 API 엔드포인트
"""

from fastapi import APIRouter, HTTPException, Depends, Path

from mysingle_quant.auth import get_current_active_verified_user, User
from app.services.service_factory import service_factory
from app.schemas.watchlist import WatchlistCreate, WatchlistUpdate

router = APIRouter()


@router.post("/", summary="워치리스트 생성/업데이트")
async def create_or_update_watchlist(
    request: WatchlistUpdate,
    current_user: User = Depends(get_current_active_verified_user),
):
    """
    워치리스트 생성 또는 업데이트

    유연한 워치리스트 관리를 위한 엔드포인트입니다.
    - 이름이 없으면 'default' 워치리스트로 처리
    - 기존 워치리스트가 있으면 업데이트, 없으면 생성
    - 심볼 데이터는 백그라운드에서 자동 수집
    """
    try:
        watchlist_service = service_factory.get_watchlist_service()

        # Use default name if not provided
        watchlist_name = request.name or "default"

        # Check if watchlist exists
        existing = await watchlist_service.get_watchlist(
            watchlist_name, str(current_user.id)
        )

        if existing:
            # Update existing watchlist
            updated_watchlist = await watchlist_service.update_watchlist(
                name=watchlist_name,
                user_id=str(current_user.id),
                symbols=request.symbols,
                description=request.description,
            )

            if updated_watchlist:
                return {
                    "message": f"워치리스트 '{watchlist_name}' 업데이트 완료",
                    "name": watchlist_name,
                    "symbols": request.symbols,
                    "count": len(request.symbols),
                    "action": "updated",
                }
        else:
            # Create new watchlist
            new_watchlist = await watchlist_service.create_watchlist(
                name=watchlist_name,
                symbols=request.symbols,
                description=request.description or "",
                user_id=str(current_user.id),
            )

            if new_watchlist:
                return {
                    "message": f"워치리스트 '{watchlist_name}' 생성 완료",
                    "name": watchlist_name,
                    "symbols": request.symbols,
                    "count": len(request.symbols),
                    "action": "created",
                }

        raise HTTPException(status_code=400, detail=f"워치리스트 '{watchlist_name}' 처리 실패")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/create", summary="새 워치리스트 생성")
async def create_watchlist(
    request: WatchlistCreate,
    current_user: User = Depends(get_current_active_verified_user),
):
    """
    새로운 명명된 워치리스트 생성

    명시적인 이름을 가진 새 워치리스트를 생성합니다.
    동일한 이름의 워치리스트가 이미 있으면 실패합니다.
    """
    try:
        watchlist_service = service_factory.get_watchlist_service()

        watchlist = await watchlist_service.create_watchlist(
            name=request.name,
            symbols=request.symbols,
            description=request.description,
            user_id=str(current_user.id),
        )

        if watchlist:
            return {
                "message": f"워치리스트 '{request.name}' 생성 완료",
                "name": watchlist.name,
                "symbols": watchlist.symbols,
                "description": watchlist.description,
                "created_at": watchlist.created_at,
            }
        else:
            raise HTTPException(
                status_code=400,
                detail=f"워치리스트 '{request.name}' 생성 실패 (이미 존재하거나 오류 발생)",
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", summary="워치리스트 목록 조회")
async def list_watchlists(
    current_user: User = Depends(get_current_active_verified_user),
):
    """
    사용자의 모든 워치리스트 목록 조회

    사용자에게 속한 모든 워치리스트의 요약 정보를 반환합니다.
    """
    try:
        watchlist_service = service_factory.get_watchlist_service()

        watchlists = await watchlist_service.list_watchlists(str(current_user.id))

        watchlists_summary = []
        for watchlist in watchlists:
            watchlists_summary.append(
                {
                    "name": watchlist.name,
                    "description": watchlist.description,
                    "symbol_count": len(watchlist.symbols),
                    "symbols": watchlist.symbols,
                    "auto_update": watchlist.auto_update,
                    "created_at": watchlist.created_at,
                    "updated_at": watchlist.updated_at,
                    "last_updated": watchlist.last_updated,
                }
            )

        return {
            "watchlists": watchlists_summary,
            "total_count": len(watchlists),
            "user_id": str(current_user.id),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{name}", summary="특정 워치리스트 조회")
async def get_watchlist(
    name: str = Path(..., description="워치리스트 이름"),
    current_user: User = Depends(get_current_active_verified_user),
):
    """
    특정 워치리스트의 상세 정보 조회
    """
    try:
        watchlist_service = service_factory.get_watchlist_service()

        watchlist = await watchlist_service.get_watchlist(name, str(current_user.id))

        if not watchlist:
            raise HTTPException(status_code=404, detail=f"워치리스트 '{name}'을 찾을 수 없습니다")

        return {
            "name": watchlist.name,
            "description": watchlist.description,
            "symbols": watchlist.symbols,
            "symbol_count": len(watchlist.symbols),
            "auto_update": watchlist.auto_update,
            "update_interval": watchlist.update_interval,
            "created_at": watchlist.created_at,
            "updated_at": watchlist.updated_at,
            "last_updated": watchlist.last_updated,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{name}", summary="워치리스트 업데이트")
async def update_watchlist(
    request: WatchlistUpdate,
    name: str = Path(..., description="워치리스트 이름"),
    current_user: User = Depends(get_current_active_verified_user),
):
    """
    기존 워치리스트 업데이트
    """
    try:
        watchlist_service = service_factory.get_watchlist_service()

        updated_watchlist = await watchlist_service.update_watchlist(
            name=name,
            user_id=str(current_user.id),
            symbols=request.symbols,
            description=request.description,
        )

        if not updated_watchlist:
            raise HTTPException(status_code=404, detail=f"워치리스트 '{name}'을 찾을 수 없습니다")

        return {
            "message": f"워치리스트 '{name}' 업데이트 완료",
            "name": updated_watchlist.name,
            "symbols": updated_watchlist.symbols,
            "description": updated_watchlist.description,
            "updated_at": updated_watchlist.updated_at,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{name}", summary="워치리스트 삭제")
async def delete_watchlist(
    name: str = Path(..., description="워치리스트 이름"),
    current_user: User = Depends(get_current_active_verified_user),
):
    """
    워치리스트 삭제
    """
    try:
        watchlist_service = service_factory.get_watchlist_service()

        success = await watchlist_service.delete_watchlist(name, str(current_user.id))

        if not success:
            raise HTTPException(status_code=404, detail=f"워치리스트 '{name}'을 찾을 수 없습니다")

        return {
            "message": f"워치리스트 '{name}' 삭제 완료",
            "name": name,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{name}/coverage", summary="워치리스트 데이터 커버리지")
async def get_watchlist_coverage(
    name: str = Path(..., description="워치리스트 이름"),
    current_user: User = Depends(get_current_active_verified_user),
):
    """
    워치리스트의 데이터 커버리지 정보 조회

    각 심볼별로 수집된 데이터의 상태와 품질을 확인합니다.
    """
    try:
        watchlist_service = service_factory.get_watchlist_service()

        coverage = await watchlist_service.get_watchlist_coverage(
            name, str(current_user.id)
        )

        if "error" in coverage:
            if coverage["error"] == "Watchlist not found":
                raise HTTPException(
                    status_code=404, detail=f"워치리스트 '{name}'을 찾을 수 없습니다"
                )
            else:
                raise HTTPException(status_code=500, detail=coverage["error"])

        return coverage

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/setup-default", summary="기본 워치리스트 설정")
async def setup_default_watchlist(
    current_user: User = Depends(get_current_active_verified_user),
):
    """
    기본 워치리스트 설정

    인기 주식들로 구성된 기본 워치리스트를 생성합니다.
    """
    try:
        watchlist_service = service_factory.get_watchlist_service()

        default_watchlist = await watchlist_service.setup_default_watchlist(
            str(current_user.id)
        )

        if default_watchlist:
            return {
                "message": "기본 워치리스트 설정 완료",
                "name": default_watchlist.name,
                "symbols": default_watchlist.symbols,
                "count": len(default_watchlist.symbols),
            }
        else:
            raise HTTPException(status_code=400, detail="기본 워치리스트 설정 실패")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
