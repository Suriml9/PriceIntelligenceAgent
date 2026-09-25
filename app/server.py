
from fastapi import FastAPI
from pydantic import BaseModel

from app.services import graph
from app.services.graph import graph
from app.services.state import PriceComparisonState

app = FastAPI()
class CreateUser(BaseModel):
    username: str
    email: str
    password: str

class UserRequest(BaseModel):
   query: str

class LoginRequest(BaseModel):
    email: str
    password: str


sampledb={}
@app.post("/create-user")
async def create_user(user: CreateUser):
    if user.email in sampledb:
        return {"message":"User already exists!"}
    else:
        sampledb[user.email] = {"username":user.username,"email":user.email,"password":user.password}
        return {"message":"User created!"}

@app.post("/login")
async def login_request(user: LoginRequest):
    if user.email in sampledb   and user.password == sampledb[user.email]["password"]:
        return {"message":"Login successful!"}
    else:
        return {"message":"Login failed!"}

@app.post("/get-bestdeal")
async def get_best_deal( request: UserRequest):
    print(request.query)
    state = PriceComparisonState(query=request.query)
    final_state= await graph.ainvoke(state)
    # result = await graph.ainvoke({"messages": [{"role": "user", "content": "Hi"}]})
    print(final_state)
    # return {"best_deal": "29"}
    return {"best_deal": final_state["response"]}

if __name__ == "__main__":
    print("Calling from server.....................")

