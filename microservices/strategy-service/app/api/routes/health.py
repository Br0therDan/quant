"""
Health Check API Routes
"""

import asyncio
from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/")
async def health_check() -> dict[str, Any]:
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "strategy-service",
        "version": "1.0.0",
    }


# @router.get("/detailed")
# async def detailed_health_check() -> Dict[str, Any]:
#     """Detailed health check with system and database status"""
#     try:
#         # System metrics
#         cpu_percent = psutil.cpu_percent(interval=1)
#         memory = psutil.virtual_memory()
#         disk = psutil.disk_usage("/")

#         # Database status
#         db_status = await get_database_status()

#         # Service status
#         service_status = {
#             "status": "healthy",
#             "timestamp": datetime.now(timezone.utc).isoformat(),
#             "service": "strategy-service",
#             "version": "1.0.0",
#         }

#         # System status
#         system_status = {
#             "cpu_usage_percent": cpu_percent,
#             "memory": {
#                 "total": memory.total,
#                 "available": memory.available,
#                 "percent": memory.percent,
#                 "used": memory.used,
#                 "free": memory.free,
#             },
#             "disk": {
#                 "total": disk.total,
#                 "used": disk.used,
#                 "free": disk.free,
#                 "percent": (disk.used / disk.total) * 100,
#             },
#         }

#         # Overall health determination
#         overall_status = "healthy"
#         if (
#             cpu_percent > 80
#             or memory.percent > 80
#             or not db_status.get("connected", False)
#         ):
#             overall_status = "unhealthy"
#         elif cpu_percent > 60 or memory.percent > 60:
#             overall_status = "degraded"

#         return {
#             **service_status,
#             "overall_status": overall_status,
#             "database": db_status,
#             "system": system_status,
#         }

#     except Exception as e:
#         return {
#             "status": "unhealthy",
#             "timestamp": datetime.utcnow().isoformat(),
#             "service": "strategy-service",
#             "error": str(e),
#         }


# @router.get("/readiness")
# async def readiness_check() -> Dict[str, Any]:
#     """Readiness probe for Kubernetes"""
#     try:
#         # Check database connectivity
#         db_status = await get_database_status()

#         if db_status.get("connected", False):
#             return {
#                 "status": "ready",
#                 "timestamp": datetime.utcnow().isoformat(),
#                 "database": "connected",
#             }
#         else:
#             raise HTTPException(
#                 status_code=503,
#                 detail={
#                     "status": "not ready",
#                     "timestamp": datetime.utcnow().isoformat(),
#                     "database": "disconnected",
#                 },
#             )

#     except HTTPException:
#         raise
#     except Exception as e:
#         raise HTTPException(
#             status_code=503,
#             detail={
#                 "status": "not ready",
#                 "timestamp": datetime.utcnow().isoformat(),
#                 "error": str(e),
#             },
#         )


@router.get("/liveness")
async def liveness_check() -> dict[str, Any]:
    """Liveness probe for Kubernetes"""
    try:
        # Simple test to ensure the service is responsive
        await asyncio.sleep(0.1)  # Small async operation test

        return {
            "status": "alive",
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "dead",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e),
            },
        )
