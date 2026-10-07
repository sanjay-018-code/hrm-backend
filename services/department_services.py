from fastapi import HTTPException
from bson import ObjectId

from models.department import (
    DepartmentCreate,
    DepartmentUpdate,
    DepartmentResponse
)
from models.employee import EmployeeResponse
from app.database import department_collection, employees_collection


def create_department_service(department: DepartmentCreate):

    name = department.name.strip()

    if not name:
        raise HTTPException(
            status_code=400,
            detail="Department name is required"
        )

    existing = department_collection.find_one({
        "name": name,
        "is_deleted": False
    })

    if existing:
        raise HTTPException(
            status_code=409,
            detail="Department Already Exists"
        )

    data = {
        "name": name,
        "is_deleted": False,
        "total_employees": 0
    }

    result = department_collection.insert_one(data)

    return DepartmentResponse(
        id=str(result.inserted_id),
        name=name,
        total_employees=0,
        is_deleted=False
    )


def get_all_department_service():

    departments = department_collection.find({
        "is_deleted": False
    })

    result = []

    for department in departments:

        total_employees = employees_collection.count_documents({
            "department": department["name"],
            "is_deleted": False
        })

        result.append(
            DepartmentResponse(
                id=str(department["_id"]),
                name=department["name"],
                total_employees=total_employees,
                is_deleted=False
            )
        )

    return result


def get_department_by_id_service(department_id: str):

    try:
        object_id = ObjectId(department_id)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid Department ID"
        )

    result = department_collection.find_one({
        "_id": object_id,
        "is_deleted": False
    })

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Department Not Found"
        )

    total_employees = employees_collection.count_documents({
        "department": result["name"],
        "is_deleted": False
    })

    return DepartmentResponse(
        id=str(result["_id"]),
        name=result["name"],
        total_employees=total_employees,
        is_deleted=False
    )


def update_department_by_id_service(
    department_id: str,
    department: DepartmentUpdate
):

    new_name = department.name.strip()

    if not new_name:
        raise HTTPException(
            status_code=400,
            detail="Department name is required"
        )

    try:
        object_id = ObjectId(department_id)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid Department ID"
        )

    existing = department_collection.find_one({
        "_id": object_id,
        "is_deleted": False
    })

    if not existing:
        raise HTTPException(
            status_code=404,
            detail="Department Not Found"
        )

    old_name = existing["name"]

    # Prevent duplicate department names
    duplicate = department_collection.find_one({
        "name": new_name,
        "is_deleted": False,
        "_id": {"$ne": object_id}
    })

    if duplicate:
        raise HTTPException(
            status_code=409,
            detail="Department Already Exists"
        )

    # Rename department
    department_collection.update_one(
        {
            "_id": object_id,
            "is_deleted": False
        },
        {
            "$set": {
                "name": new_name
            }
        }
    )

    # Update employees using the old department name
    employees_collection.update_many(
        {
            "department": old_name,
            "is_deleted": False
        },
        {
            "$set": {
                "department": new_name
            }
        }
    )

    total_employees = employees_collection.count_documents({
        "department": new_name,
        "is_deleted": False
    })

    return DepartmentResponse(
        id=str(object_id),
        name=new_name,
        total_employees=total_employees,
        is_deleted=False
    )


def delete_department_service(department_id: str):

    try:
        object_id = ObjectId(department_id)
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid Department ID"
        )

    department = department_collection.find_one({
        "_id": object_id,
        "is_deleted": False
    })

    if not department:
        raise HTTPException(
            status_code=404,
            detail="Department Not Found"
        )

    employee_count = employees_collection.count_documents({
        "department": department["name"],
        "is_deleted": False
    })

    # Don't allow deleting a department that still contains employees
    if employee_count > 0:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot delete department. {employee_count} employee(s) are assigned to it."
        )

    department_collection.update_one(
        {
            "_id": object_id,
            "is_deleted": False
        },
        {
            "$set": {
                "is_deleted": True
            }
        }
    )

    return {
        "message": "Department Deleted Successfully"
    }
