from fastapi import APIRouter, Depends
from core.redis import ip_redis
from services.auth import get_current_user
from models.users import User


router = APIRouter(prefix='/admin', tags=['Admin'])

# Endpoint for IP Blocking
@router.post("/block-ip", tags=["Admin"])
def block_ip(ip: str, hours: int = 24, authorized_user: User = Depends(get_current_user)):
    # Calculating TTL of the key in seconds
    seconds = hours * 3600
    # Writting to redis db 1 with TTL set
    ip_redis.setex(ip, seconds, "banned")
    return {"status": "success", "message": f"IP {ip} is blocked for {hours} hrs."}

# Endpoint for IP unblocking
@router.delete("/unblock-ip")
def unblock_ip(ip: str, authorized_user: User = Depends(get_current_user)):
    deleted = ip_redis.delete(ip)
    if deleted:
        return {"status": "success", "message": f"IP {ip} is blocked"}
    return {"status": "error", "message": "IP wasn't found in blacklist."}