from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from core.database import get_db
from core.redis import ip_redis
from core.dependencies import require_admin
from schemas.users import StaffUserCreate, UserResponse
from services.users import create_user as create_user_record


router = APIRouter(prefix='/admin', tags=['Admin'])

# Endpoint to check your IP address
@router.get("/my-ip")
def get_current_ip_address(request: Request):
    return {"ip_address": request.client.host}

@router.get("/blocked-ips", dependencies=[Depends(require_admin)], tags=["Admin"])
def get_blocked_ips():
    blocked_ips = ip_redis.keys('*')
    return {"blocked_ips": [ip.decode('utf-8') for ip in blocked_ips]}


# Endpoint for IP Blocking
@router.post("/block-ip", dependencies=[Depends(require_admin)], tags=["Admin"])
def block_ip(ip: str, hours: int = 24):
    # Calculating TTL of the key in seconds
    seconds = hours * 3600
    # Writting to redis db 1 with TTL set
    ip_redis.setex(ip, seconds, "banned")
    return {"status": "success", "message": f"IP {ip} is blocked for {hours} hrs."}

# Endpoint for IP unblocking
@router.delete("/unblock-ip", dependencies=[Depends(require_admin)], tags=["Admin"])
def unblock_ip(ip: str):
    deleted = ip_redis.delete(ip)
    if deleted:
        return {"status": "success", "message": f"IP {ip} is unblocked"}
    return {"status": "error", "message": "IP wasn't found in blacklist."}


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_admin)],
)
def create_staff_user(
    user_data: StaffUserCreate,
    db: Annotated[Session, Depends(get_db)],
):
    return create_user_record(
        db,
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        role=user_data.role,
    )
