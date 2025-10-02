"""
Watchlist Management API Routes
"""

from datetime import datetime, timezone
from typing import AsyncGenerator
from fastapi import APIRouter, HTTPException, Depends
from app.schemas.watchlist import WatchlistCreate, WatchlistUpdate
from app.services.data_pipeline import DataPipeline
from mysingle_quant.auth import get_current_active_verified_user, User

router = APIRouter()


async def get_data_pipeline() -> AsyncGenerator[DataPipeline, None]:
    """
    Dependency injection for DataPipeline service.

    Provides a DataPipeline instance with proper resource cleanup.
    """
    pipeline = DataPipeline()
    try:
        yield pipeline
    finally:
        await pipeline.cleanup()


@router.post("/watchlist")
async def update_watchlist(
    request: WatchlistUpdate,
    current_user: User = Depends(get_current_active_verified_user),
    pipeline: DataPipeline = Depends(get_data_pipeline),
):
    """
    Create or update a watchlist with flexible naming support.

    This endpoint provides a convenient way to create new watchlists or update
    existing ones. If no name is provided, it defaults to the 'default' watchlist
    which is used by the pipeline for automated updates. This endpoint combines
    creation and update functionality for ease of use.

    Args:
        request: Watchlist configuration containing:
            - symbols: List of stock symbols to include
            - name: Optional watchlist name (defaults to 'default')
            - description: Optional description of the watchlist

    Returns:
        dict: Operation result containing:
            - message: Success message indicating action taken
            - name: Watchlist name that was processed
            - symbols: List of symbols in the watchlist
            - count: Number of symbols in the watchlist
            - action: Either 'created' or 'updated'

    Raises:
        HTTPException: 400 if watchlist creation fails
        HTTPException: 500 if operation fails

    Note:
        Updates to the 'default' watchlist automatically update pipeline symbols.
        This affects which symbols are processed during automated updates.
    """
    try:
        # Use default name if not provided
        watchlist_name = request.name or "default"
        watchlist_description = request.description or ""

        # Check if watchlist exists
        existing_watchlist = await pipeline.get_watchlist(
            watchlist_name, str(current_user.id)
        )

        if existing_watchlist:
            # Update existing watchlist
            existing_watchlist.symbols = request.symbols
            existing_watchlist.description = (
                watchlist_description or existing_watchlist.description
            )
            existing_watchlist.updated_at = datetime.now(timezone.utc)
            await existing_watchlist.save()

            # Also update pipeline symbols if this is the default watchlist
            if watchlist_name == "default":
                await pipeline.update_watchlist(request.symbols)

            return {
                "message": f"Watchlist '{watchlist_name}' updated successfully",
                "name": watchlist_name,
                "symbols": request.symbols,
                "count": len(request.symbols),
                "action": "updated",
            }
        else:
            # Create new watchlist
            watchlist = await pipeline.create_watchlist(
                name=watchlist_name,
                symbols=request.symbols,
                description=watchlist_description,
                user_id=str(current_user.id),
            )

            if watchlist:
                # Also update pipeline symbols if this is the default watchlist
                if watchlist_name == "default":
                    await pipeline.update_watchlist(request.symbols)

                return {
                    "message": f"Watchlist '{watchlist_name}' created successfully",
                    "name": watchlist_name,
                    "symbols": request.symbols,
                    "count": len(request.symbols),
                    "action": "created",
                }
            else:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to create watchlist '{watchlist_name}'",
                )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/watchlists")
async def create_watchlist(
    request: WatchlistCreate,
    current_user: User = Depends(get_current_active_verified_user),
    pipeline: DataPipeline = Depends(get_data_pipeline),
):
    """
    Create a new named watchlist with validation.

    This endpoint is specifically for creating new watchlists with explicit
    naming requirements. Unlike the /watchlist endpoint, this requires a name
    and will fail if a watchlist with the same name already exists.

    Args:
        request: Watchlist creation parameters containing:
            - name: Required unique name for the watchlist
            - symbols: List of stock symbols to include
            - description: Optional description of the watchlist purpose

    Returns:
        dict: Creation result containing:
            - message: Success confirmation message
            - name: Name of the created watchlist
            - symbols: List of symbols in the watchlist
            - description: Watchlist description
            - created_at: UTC timestamp of creation

    Raises:
        HTTPException: 400 if watchlist creation fails or name conflicts
        HTTPException: 500 if database operation fails

    Note:
        Watchlist names must be unique. Use PUT /watchlists/{name} to update existing ones.
    """
    try:
        watchlist = await pipeline.create_watchlist(
            name=request.name,
            symbols=request.symbols,
            description=request.description,
            user_id=str(current_user.id),
        )

        if watchlist:
            return {
                "message": f"Watchlist '{request.name}' created successfully",
                "name": watchlist.name,
                "symbols": watchlist.symbols,
                "description": watchlist.description,
                "created_at": watchlist.created_at,
            }
        else:
            raise HTTPException(
                status_code=400, detail=f"Failed to create watchlist '{request.name}'"
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/watchlists")
async def list_watchlists(
    current_user: User = Depends(get_current_active_verified_user),
    pipeline: DataPipeline = Depends(get_data_pipeline),
):
    """
    Retrieve a comprehensive list of all watchlists.

    Returns summary information for all watchlists in the system, including
    metadata like symbol counts, update settings, and timestamps. This is
    useful for dashboard displays and watchlist management interfaces.

    Returns:
        dict: All watchlists summary containing:
            - watchlists: List of watchlist summaries with:
                - name: Watchlist name
                - description: Watchlist description
                - symbol_count: Number of symbols in the watchlist
                - auto_update: Whether automatic updates are enabled
                - last_updated: Timestamp of last modification
                - created_at: Timestamp of creation
            - total_count: Total number of watchlists in the system

    Raises:
        HTTPException: 500 if retrieval fails

    Note:
        This endpoint returns summary data only. Use GET /watchlists/{name}
        for detailed information including full symbol lists.
    """
    try:
        watchlists = await pipeline.list_watchlists(str(current_user.id))

        return {
            "watchlists": [
                {
                    "name": wl.name,
                    "description": wl.description,
                    "symbol_count": len(wl.symbols),
                    "auto_update": wl.auto_update,
                    "last_updated": wl.last_updated,
                    "created_at": wl.created_at,
                }
                for wl in watchlists
            ],
            "total_count": len(watchlists),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{name}")
async def get_watchlist(
    name: str,
    current_user: User = Depends(get_current_active_verified_user),
    pipeline: DataPipeline = Depends(get_data_pipeline),
):
    """
    Retrieve complete information for a specific watchlist.

    Returns detailed information about a named watchlist including the full
    list of symbols, configuration settings, and all metadata. This provides
    all information needed to display or modify a specific watchlist.

    Args:
        name: Name of the watchlist to retrieve (case-sensitive)

    Returns:
        dict: Complete watchlist information containing:
            - name: Watchlist name
            - description: Detailed description
            - symbols: Complete list of stock symbols
            - auto_update: Automatic update configuration
            - update_interval: Update frequency in seconds
            - last_updated: Timestamp of last symbol update
            - created_at: Timestamp of watchlist creation

    Raises:
        HTTPException: 404 if watchlist with specified name not found
        HTTPException: 500 if retrieval operation fails

    Note:
        Watchlist names are case-sensitive. Use GET /watchlists to see all available names.
    """
    try:
        watchlist = await pipeline.get_watchlist(name, str(current_user.id))

        if watchlist:
            # 소유권 체크
            if watchlist.user_id != str(current_user.id):
                raise HTTPException(status_code=403, detail="Access denied")
            return {
                "name": watchlist.name,
                "description": watchlist.description,
                "symbols": watchlist.symbols,
                "auto_update": watchlist.auto_update,
                "update_interval": watchlist.update_interval,
                "last_updated": watchlist.last_updated,
                "created_at": watchlist.created_at,
            }
        else:
            raise HTTPException(status_code=404, detail=f"Watchlist '{name}' not found")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{name}")
async def update_watchlist_by_name(
    name: str,
    request: WatchlistUpdate,
    current_user: User = Depends(get_current_active_verified_user),
    pipeline: DataPipeline = Depends(get_data_pipeline),
):
    """
    Update an existing watchlist with new symbols and settings.

    Modifies the symbols and metadata of an existing watchlist. This endpoint
    requires the watchlist to exist and will fail if the specified name is
    not found. Use POST /watchlists to create new watchlists.

    Args:
        name: Name of the existing watchlist to update
        request: Update parameters containing:
            - symbols: New list of symbols (replaces current list)
            - description: Optional new description (if provided)

    Returns:
        dict: Update confirmation containing:
            - message: Success confirmation message
            - name: Name of the updated watchlist
            - symbols: New symbols list
            - description: Current description (updated if provided)
            - count: Number of symbols in updated watchlist
            - updated_at: Timestamp of the update

    Raises:
        HTTPException: 404 if watchlist with specified name not found
        HTTPException: 500 if update operation fails

    Note:
        Updates to the 'default' watchlist automatically update pipeline symbols.
        Symbol list is completely replaced, not merged with existing symbols.
    """
    try:
        existing_watchlist = await pipeline.get_watchlist(name, str(current_user.id))

        if not existing_watchlist:
            raise HTTPException(status_code=404, detail=f"Watchlist '{name}' not found")

        # 소유권 체크
        if existing_watchlist.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")

        # Update watchlist
        existing_watchlist.symbols = request.symbols
        if request.description:
            existing_watchlist.description = request.description
        existing_watchlist.updated_at = datetime.now(timezone.utc)
        existing_watchlist.last_updated = datetime.now(timezone.utc)
        await existing_watchlist.save()

        # Also update pipeline symbols if this is the default watchlist
        if name == "default":
            await pipeline.update_watchlist(request.symbols)

        return {
            "message": f"Watchlist '{name}' updated successfully",
            "name": name,
            "symbols": request.symbols,
            "description": existing_watchlist.description,
            "count": len(request.symbols),
            "updated_at": existing_watchlist.updated_at,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{name}")
async def delete_watchlist(
    name: str,
    current_user: User = Depends(get_current_active_verified_user),
    pipeline: DataPipeline = Depends(get_data_pipeline),
):
    """
    Delete a named watchlist from the system.

    Permanently removes a watchlist and all associated metadata. This action
    cannot be undone. The 'default' watchlist cannot be deleted as it is
    required for pipeline operations.

    Args:
        name: Name of the watchlist to delete

    Returns:
        dict: Deletion confirmation containing:
            - message: Success confirmation message
            - name: Name of the deleted watchlist

    Raises:
        HTTPException: 400 if attempting to delete the 'default' watchlist
        HTTPException: 404 if watchlist with specified name not found
        HTTPException: 500 if deletion operation fails

    Note:
        Deletion is permanent and cannot be undone. Consider backing up
        important watchlists before deletion.
    """
    try:
        if name == "default":
            raise HTTPException(
                status_code=400, detail="Cannot delete the default watchlist"
            )

        existing_watchlist = await pipeline.get_watchlist(name, str(current_user.id))

        if not existing_watchlist:
            raise HTTPException(status_code=404, detail=f"Watchlist '{name}' not found")

        # 소유권 체크
        if existing_watchlist.user_id != str(current_user.id):
            raise HTTPException(status_code=403, detail="Access denied")

        await existing_watchlist.delete()

        return {"message": f"Watchlist '{name}' deleted successfully", "name": name}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
