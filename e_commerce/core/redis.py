import redis
from .config import settings


token_blacklist = redis.Redis(
    host=settings.REDIS_HOST, 
    port=settings.REDIS_PORT, 
    db=0, 
    decode_responses=True
)

# Connection to DB 1 (Blocked IPs)
ip_redis = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)



    

