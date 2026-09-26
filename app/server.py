
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from app.services import graph
from app.services.graph import graph
from app.services.state import PriceComparisonState

# --- JWT configuration ---
SECRET_KEY = "change-me-to-a-real-secret"   # TODO: load from env / .env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()
bearer_scheme = HTTPBearer()


# --- Models ---
class CreateUser(BaseModel):
    username: str
    email: str
    password: str

class UserRequest(BaseModel):
   query: str

class LoginRequest(BaseModel):
    email: str
    password: str


# --- JWT helpers ---
def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> dict:
    """FastAPI dependency – validates the Bearer token and returns the payload."""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
            )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


# --- In-memory user store ---
sampledb={}


# --- Routes ---
@app.post("/create-user")
async def create_user(user: CreateUser):
    if user.email in sampledb:
        return {"message":"User already exists!"}
    else:
        sampledb[user.email] = {"username":user.username,"email":user.email,"password":user.password}
        return {"message":"User created!"}

@app.post("/login")
async def login_request(user: LoginRequest):
    if user.email in sampledb and user.password == sampledb[user.email]["password"]:
        access_token = create_access_token(data={"sub": user.email})
        return {"message":"Login successful!", "access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

@app.post("/get-bestdeal")
async def get_best_deal(request: UserRequest, token_data: dict = Depends(verify_token)):
    print(f"Authenticated user: {token_data.get('sub')}")
    print(request.query)
    state = PriceComparisonState(query=request.query)
    final_state= await graph.ainvoke(state)
    # result = await graph.ainvoke({"messages": [{"role": "user", "content": "Hi"}]})
    print(final_state)
    # return {"best_deal": "29"}
    return {"best_deal": final_state["response"]}

if __name__ == "__main__":
    print("Calling from server......................")
