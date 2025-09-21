from datetime import datetime, timedelta,timezone
from jose import jwt

SECRET_KEY = "P4Mqw7qbHoThXKGS0pfT_UEF8F3PBK_4grjiTvYaPFs"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

