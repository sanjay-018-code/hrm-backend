from fastapi import HTTPException
from bson import ObjectId

from models.department import DepartmentCreate,DepartmentResponse
from models.employee import EmployeeResponse
from app.database import department_collection, employees_collection

def create_department_service(department:DepartmentCreate):
    existing = department_collection.find_one({"name":department.name}) 
    if existing : raise HTTPException(401,"Department Already Exists")

    data = department.model_dump()
    data["is_deleted"]  =False

    data["total_employees"] = employees_collection.count_documents({
        "department": department.name
    })

    result = department_collection.insert_one(data)
    return DepartmentResponse(
        id= str(result.inserted_id),
        **data
    )

def get_all_department_service():

    departments = department_collection.find({"is_deleted":False})
    if not departments : raise HTTPException(404, "NO Departments found")

    result = []

    for department in departments:  
        total_employees = employees_collection.count_documents({"department": department["name"],"is_deleted":False})
        result.append(
        DepartmentResponse(
            id=str(department["_id"]),
            name= department["name"],
            total_employees=total_employees
        ))

    return result

def get_department_by_id_service(department_id):
    result = department_collection.find_one({"_id":ObjectId(department_id),"is_deleted":False})
    if not result: raise HTTPException(404,"Department Not Found")
    total_employees = employees_collection.count_documents({"department": result["name"],"is_deleted":False})

    return DepartmentResponse(
        id=str(result["_id"]),
        name=result["name"],
        total_employees=(total_employees)
    )

def update_department_by_id_service(department_id,name):
    update = department_collection.update_one({
        "_id": ObjectId(department_id),
        "is_deleted":False
    },{
        "$set":{
            "name":name
        }
    })

    if update.matched_count == 0: raise HTTPException(404,"Department not Found")

    updated = department_collection.find_one({"_id":ObjectId(department_id)})
    if not updated : raise HTTPException(404,"Department not Found")

    total_employees = employees_collection.count_documents({"department":updated["name"]})

    return DepartmentResponse(
        id=str(updated["_id"]),
        name=updated["name"],
        total_employees=(total_employees)
    )

def delete_department_service(department_id):
    deleted = department_collection.update_one({
        "_id":ObjectId(department_id),
        "is_deleted":False
    },{
        "$set":{
            "is_deleted":True
        }
    })

    if deleted.matched_count == 0: raise HTTPException(404,"Department Not Found")

    return {
        "message":"Deprtment Deleted"
    }

def get_employees_by_department_services(department_id):
    existing = department_collection.find_one({"_id":ObjectId(department_id)})
    if not existing: raise HTTPException(404,"Department Not Found")

    employee = employees_collection.find({
        "is_deleted":False,
        "department":existing["name"]
    })

    employees = []

    for e in employee:
        employees.append(
            EmployeeResponse(
                id = str(e["_id"]),
                name= e["name"],
                department= e["department"],
                designation= e["designation"],
                joining_date= e["joining_date"],
                salary= e["salary"],
                phone= e["phone"],
                email= e["email"],
            )
        )

    return employees
