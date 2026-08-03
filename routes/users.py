from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from models.user import UserRegister
from services.role_dependency import allow_roles
from services.password import hash_password
from app.database import users_collection

router = APIRouter()

@router.post("/")
def create_user(user: UserRegister, current_user = Depends(allow_roles(["admin", "hr"]))):
    existing_user = users_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(400, "Username already exists")
    
    if user.role == "admin" and current_user.get("role") != "admin":
        raise HTTPException(403, "Only admin can create admin users")
    
    if user.employee_id and user.role != "employee":
        raise HTTPException(400, "Only employee users can be linked to employees")
    
    data = user.model_dump()
    data["password"] = hash_password(data["password"])
    
    users_collection.insert_one(data)
    
    return {"message": "User created successfully"}

@router.get("/")
def get_all_users(current_user = Depends(allow_roles(["admin", "hr"]))):
    users = users_collection.find({}, {"password": 0})
    result = []
    for user in users:
        result.append({
            "id": str(user["_id"]),
            "username": user["username"],
            "role": user["role"],
            "employee_id": user.get("employee_id")
        })
    return result

@router.get("/{user_id}")
def get_user_by_id(user_id: str, current_user = Depends(allow_roles(["admin", "hr"]))):
    user = users_collection.find_one({"_id": ObjectId(user_id)}, {"password": 0})
    if not user:
        raise HTTPException(404, "User not found")
    return {
        "id": str(user["_id"]),
        "username": user["username"],
        "role": user["role"],
        "employee_id": user.get("employee_id")
    }

@router.put("/{user_id}")
def update_user(user_id: str, user_data: dict, current_user = Depends(allow_roles(["admin", "hr"]))):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(404, "User not found")
    
    if user.get("role") == "admin" and current_user.get("role") != "admin":
        raise HTTPException(403, "Only admin can update admin users")
    
    if "employee_id" in user_data and user_data["employee_id"] and user.get("role") != "employee":
        raise HTTPException(400, "Only employee users can be linked to employees")
    
    update_data = {}
    if "username" in user_data:
        update_data["username"] = user_data["username"]
    if "role" in user_data and current_user.get("role") == "admin":
        update_data["role"] = user_data["role"]
    if "password" in user_data:
        update_data["password"] = hash_password(user_data["password"])
    if "employee_id" in user_data:
        update_data["employee_id"] = user_data["employee_id"]
    
    if not update_data:
        raise HTTPException(400, "No valid fields to update")
    
    users_collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": update_data}
    )
    
    return {"message": "User updated successfully"}

@router.delete("/{user_id}")
def delete_user(user_id: str, current_user = Depends(allow_roles(["admin", "hr"]))):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(404, "User not found")
    
    if user["username"] == current_user.get("username"):
        raise HTTPException(400, "Cannot delete your own account")
    
    if user.get("role") == "admin" and current_user.get("role") != "admin":
        raise HTTPException(403, "Only admin can delete admin users")
    
    users_collection.delete_one({"_id": ObjectId(user_id)})
    return {"message": "User deleted successfully"}
