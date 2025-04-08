from fastapi import APIRouter, HTTPException, status

router = APIRouter()

@router.post("/users")
async def create_users(data: dict):
    return {"message": "Created users", "data": data}

@router.get("/users")
async def read_userss():
    return {"message": "List all userss"}

@router.get("/users/{users_id}")
async def read_users(users_id: int):
    return {"message": f"Get users {users_id}"}

@router.put("/users/{users_id}")
async def update_users(users_id: int, data: dict):
    return {"message": f"Update users {users_id}", "data": data}

@router.delete("/users/{users_id}")
async def delete_users(users_id: int):
    return {"message": f"Delete users {users_id}"}
