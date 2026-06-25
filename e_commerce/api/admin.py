from fastapi import APIRouter, Depends, Request
from core.redis import ip_redis
from core.dependencies import require_admin


router = APIRouter(prefix='/admin', tags=['Admin'])

# Endpoint to check your IP address
@router.get("/my-ip")
def get_current_ip_address(request: Request):
    return {"ip_address": request.client.host}


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