from fastapi import HTTPException
from bson import ObjectId

from app.database import employees_collection, department_collection
from models.employee import EmployeeListResponse, EmployeeResponse, EmployeeCreate, EmployeeUpdate

def create_employee_services(employee:EmployeeCreate):
    existing = employees_collection.find_one({"name":employee.name,"department":employee.department,"is_deleted":False})
    if existing: raise HTTPException(401, "Employee Already Exists")

    find_department = department_collection.find_one({"name":employee.department})
    if not find_department : raise HTTPException(404,"Department Not Found")

    data = employee.model_dump()
    data["is_deleted"] = False

    result = employees_collection.insert_one(data)

    return EmployeeResponse(
        id=str(result.inserted_id),
        **data
    )

def get_all_employees(page, limit, search, sort_by,order, department = None):

    skip = (page-1)*limit
    query:dict[str, object] = {
        "is_deleted":False
    }
    sort_order = 1 if order.value == "asc" else -1

    if search :
        query.update(
            {
                "name":{
                    "$regex":search,"$options": "i"
                }
            }
        )

    if department:
        query["department"] = department.value

    total = employees_collection.count_documents(query)
    result = employees_collection.find(query).sort(sort_by,sort_order).skip(skip).limit(limit)

    employees = []

    for emp in result:
        employees.append(EmployeeResponse(
            id = str(emp["_id"]),
            name = emp["name"],
            department = emp["department"],
            designation= emp["designation"],
            joining_date=emp["joining_date"],
            salary=emp["salary"],
            phone=emp["phone"],
            email=emp["email"]
        ))

    return EmployeeListResponse(
        employees=employees,
        page = page,
        limit=limit,
        total = total,
        has_more = ((skip + len(employees)) < total)
    )

def update_employee_service(employee_id, employee:EmployeeUpdate):
    existing = employees_collection.find_one({"_id": ObjectId(employee_id)})
    if not existing: raise HTTPException(404, "Employee not Found")

    update_data = employee.model_dump(exclude_none=True)

    if "department" in update_data and update_data["department"] != existing.get("department"):
        new_dept = update_data["department"]
        old_dept = existing.get("department")

        if not department_collection.find_one({"name": new_dept}):
            raise HTTPException(404, "Department Not Found")

        if old_dept:
            department_collection.update_one({"name": old_dept}, {"$inc": {"total_employees": -1}})

        department_collection.update_one({"name": new_dept}, {"$inc": {"total_employees": 1}}, upsert=False)

    employees_collection.update_one({
        "_id": ObjectId(employee_id)
    },{
        "$set": update_data
    })

    updated = employees_collection.find_one({"_id":ObjectId(employee_id)})
    if not updated: raise HTTPException(404, "Employee not Found")

    return EmployeeResponse(
        id = str(updated["_id"]),
        name = updated["name"],
        department = updated["department"],
        designation= updated["designation"],
        joining_date=updated["joining_date"],
        salary=updated["salary"],
        phone=updated["phone"],
        email=updated["email"]
    )

def delete_employee_service(employee_id:str):
    existing = employees_collection.find_one({"_id": ObjectId(employee_id)})
    if not existing: raise HTTPException(404, "Employee not Found")
    if existing.get("is_deleted", False): raise HTTPException(404, "Employee not Found")

    result = employees_collection.update_one({"_id": ObjectId(employee_id)}, {"$set": {"is_deleted": True}})
    if result.modified_count == 0: raise HTTPException(404, "Employee not Found")

    dept = existing.get("department")
    if dept:
        department_collection.update_one({"name": dept}, {"$inc": {"total_employees": -1}})

    return {
        "message": "Employee Deleted"
    }

def get_employee_by_id_service(employee_id:str):
    employee = employees_collection.find_one({"_id": ObjectId(employee_id)})
    if not employee: raise HTTPException(404, "Employee Not Found")
    return EmployeeResponse(
        id = str(employee["_id"]),
        name = employee["name"],
        department = employee["department"],
        designation= employee["designation"],
        joining_date=employee["joining_date"],
        salary=employee["salary"],
        phone=employee["phone"],
        email=employee["email"]
    )