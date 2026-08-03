from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends

from models.user import UserRegister, UserLogin, ForgotUsernameRequest, ForgotPasswordRequest, RecoveryRequestUpdate
from services.password import hash_password
from services.password import verify_password
from services.jwt_handler import create_token
from app.database import users_collection, employees_collection, recovery_requests_collection

from services.role_dependency import allow_roles

router = APIRouter()


def _serialize_recovery_request(request: dict) -> dict:
    return {
        "id": str(request["_id"]),
        "request_type": request["request_type"],
        "status": request["status"],
        "username": request.get("username"),
        "employee_id": request.get("employee_id"),
        "new_username": request.get("new_username"),
        "reason": request.get("reason"),
        "requested_by": request.get("requested_by"),
        "reviewed_by": request.get("reviewed_by"),
        "review_note": request.get("review_note"),
        "created_at": request.get("created_at"),
    }


@router.post("/register")
def register(user:UserRegister,current_user =Depends(allow_roles(["hr","admin"]))):
    data = user.model_dump()

    data["password"] = (hash_password(data["password"]))
    users_collection.insert_one(data)

    return {
        "message": "User Registered Successfully"
    }


@router.post("/forgot-username")
def request_forgot_username(payload: ForgotUsernameRequest):
    employee = employees_collection.find_one({"_id": ObjectId(payload.employee_id)}) if ObjectId.is_valid(payload.employee_id) else None
    if not employee:
        raise HTTPException(404, "Employee not found")

    linked_user = users_collection.find_one({"employee_id": payload.employee_id})
    if not linked_user:
        raise HTTPException(404, "No account is linked to this employee")

    if users_collection.find_one({"username": payload.new_username}):
        raise HTTPException(400, "That username is already in use")

    recovery_requests_collection.insert_one({
        "request_type": "username",
        "user_id": linked_user["_id"],
        "employee_id": payload.employee_id,
        "username": linked_user["username"],
        "new_username": payload.new_username,
        "requested_by": payload.employee_id,
        "reason": payload.reason,
        "status": "pending",
        "created_at": datetime.utcnow(),
    })

    return {
        "message": "Forgot username request submitted for HR approval"
    }


@router.post("/forgot-password")
def request_forgot_password(payload: ForgotPasswordRequest):
    db_user = users_collection.find_one({"username": payload.username})
    if not db_user:
        raise HTTPException(404, "Username not found")

    if not verify_password(payload.old_password, db_user["password"]):
        raise HTTPException(401, "Old password is incorrect")

    recovery_requests_collection.insert_one({
        "request_type": "password",
        "user_id": db_user["_id"],
        "employee_id": db_user.get("employee_id"),
        "username": db_user["username"],
        "old_password": payload.old_password,
        "new_password": hash_password(payload.new_password),
        "requested_by": payload.username,
        "reason": payload.reason,
        "status": "pending",
        "created_at": datetime.utcnow(),
    })

    return {
        "message": "Forgot password request submitted for HR approval"
    }


@router.get("/recovery-requests")
def get_recovery_requests(current_user = Depends(allow_roles(["hr", "admin"]))):
    requests = list(recovery_requests_collection.find().sort("created_at", -1))
    return [_serialize_recovery_request(request) for request in requests]


@router.patch("/recovery-requests/{request_id}")
def update_recovery_request(request_id: str, payload: RecoveryRequestUpdate, current_user = Depends(allow_roles(["hr", "admin"]))):
    request_record = recovery_requests_collection.find_one({"_id": ObjectId(request_id)})
    if not request_record:
        raise HTTPException(404, "Recovery request not found")

    if payload.status == "approved":
        user_record = users_collection.find_one({"_id": request_record["user_id"]})
        if not user_record:
            raise HTTPException(404, "Linked user account not found")

        if request_record["request_type"] == "username":
            new_username = request_record.get("new_username")
            if not new_username:
                raise HTTPException(400, "New username was not supplied")
            if users_collection.find_one({"username": new_username, "_id": {"$ne": user_record["_id"]}}):
                raise HTTPException(400, "That username is already in use")

            users_collection.update_one(
                {"_id": user_record["_id"]},
                {"$set": {"username": new_username}}
            )

        elif request_record["request_type"] == "password":
            new_password = request_record.get("new_password")
            if not new_password:
                raise HTTPException(400, "New password was not supplied")

            users_collection.update_one(
                {"_id": user_record["_id"]},
                {"$set": {"password": new_password}}
            )

    recovery_requests_collection.update_one(
        {"_id": ObjectId(request_id)},
        {"$set": {
            "status": payload.status,
            "reviewed_by": current_user.get("username"),
            "review_note": payload.review_note,
            "reviewed_at": datetime.utcnow(),
        }}
    )

    return {
        "message": f"Recovery request {payload.status} successfully"
    }


@router.post("/login")
def login(form_data: UserLogin):
    username = form_data.username
    password = form_data.password

    db_user = users_collection.find_one({
        "username": username
    })
    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid Username"
        )
    
    valid = verify_password(password, db_user["password"])
    if not valid:
        raise HTTPException(
            status_code=401,
            detail="Wrong Password"
        )
    
    token_payload = {
        "username": db_user["username"],
        "role": db_user["role"]
    }
    if db_user.get("role") == "employee" and db_user.get("employee_id"):
        token_payload["employee_id"] = db_user["employee_id"]

    token = create_token(token_payload)

    return {
        "access_token" : token,
        "token_type": "bearer",
        "role": db_user["role"]
    }