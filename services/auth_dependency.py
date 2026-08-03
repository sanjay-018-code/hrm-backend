from fastapi import HTTPException,Depends
from fastapi.security import OAuth2PasswordBearer
from services.jwt_handler import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(token:str=Depends(oauth2_scheme)):
    print("token",token)

    payload = verify_token(token)
    print("Payload", payload)

    if not payload:
        raise HTTPException(status_code=401, detail='Invalid Token')

    return payload