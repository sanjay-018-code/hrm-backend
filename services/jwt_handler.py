from jose import jwt, JWTError
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

SECRET =str(os.getenv("JWT_SECRET"))
ALGORITHM = str(os.getenv("JWT_ALGORITHM"))
TOKEN_EXPIRE_MINUTES=12*60

def create_token(data):
    payload = data.copy()
    expire = (datetime.utcnow()+ timedelta(minutes=TOKEN_EXPIRE_MINUTES))
    payload["exp"] = expire

    token = jwt.encode(payload,SECRET,algorithm = ALGORITHM)
    return token

def verify_token(token):
    try:
        payload = jwt.decode(
            token,
            SECRET,
            algorithms=[ALGORITHM]
        )
        return payload
    except JWTError:
        return None