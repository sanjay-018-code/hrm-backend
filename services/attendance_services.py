from fastapi import HTTPException
from bson import ObjectId

from models.attendance import AttendanceCreate, AttendanceResponse, AttendanceUpdate
from app.database import attendance_collection

def create_attendance(attendance:AttendanceCreate):
    attendance_date = attendance.date.isoformat()
    existing = attendance_collection.find_one({"employee_id": attendance.employee_id, "date": attendance_date})
    
    if existing:
        if existing.get("is_deleted") == True:
            result = attendance_collection.update_one({
                "_id": existing["_id"]
            }, {
                "$set": {
                    "status": attendance.status,
                    "check_in": attendance.check_in.isoformat(),
                    "check_out": attendance.check_out.isoformat(),
                    "is_deleted": False
                }
            })
            updated = attendance_collection.find_one({"_id": existing["_id"]})
            return AttendanceResponse(
                id=str(updated["_id"]),
                employee_id=updated["employee_id"],
                date=updated["date"],
                status=updated["status"],
                check_in=updated["check_in"],
                check_out=updated["check_out"]
            )
        else:
            raise HTTPException(401,"Attendance already exists")

    data = attendance.model_dump()
    data["is_deleted"] = False
    serialized_data = {
        "employee_id": data["employee_id"],
        "date": data["date"].isoformat(),
        "status": data["status"],
        "check_in": data["check_in"].isoformat(),
        "check_out": data["check_out"].isoformat(),
        "is_deleted": False,
    }
    result = attendance_collection.insert_one(serialized_data)

    return AttendanceResponse(
        id=str(result.inserted_id),
        **serialized_data
    )

def get_all_attendance_service(page, limit, employee_id = None, order = "desc"):

    sort_order = (-1 if order=="desc" else 1)
    query = {
        "$or": [
            {"is_deleted": False},
            {"is_deleted": {"$exists": False}},
        ]
    }
    if employee_id:
        query["employee_id"] = employee_id

    skip = (page-1)*limit
    result = attendance_collection.find(query).sort("date",sort_order).skip(skip).limit(limit)
    attendance = []
    for record in result:
        attendance.append(
            AttendanceResponse(
                id=str(record["_id"]),
                employee_id=record["employee_id"],
                date=record["date"],
                status=record["status"],
                check_in=record["check_in"],
                check_out=record["check_out"]
            )
        )

    return attendance

def update_attendance_services(attendance_id, attendance:AttendanceUpdate):

    updates = attendance.model_dump(exclude_none=True)
    
    result = attendance_collection.update_one({
        "_id":ObjectId(attendance_id)
    },{
        "$set":updates
    })
    if result.matched_count == 0: raise HTTPException(404, "Attendance Not Found")
    
    updated = attendance_collection.find_one({"_id":ObjectId(attendance_id)})
    if not updated : raise HTTPException(404, "Attendance not Found")

    return AttendanceResponse(
        id=str(updated["_id"]),
        employee_id= updated["employee_id"] ,
        date= updated["date"],
        status= updated["status"],
        check_in= updated["check_in"],
        check_out= updated["check_out"]
    )

def delete_attendance_services(attendance_id):
    result = attendance_collection.update_one({
        "_id":ObjectId(attendance_id)
    },{
        "$set":{
            "is_deleted":True
        }
    })

    if result.matched_count == 0: raise HTTPException(404,"Attendance not found")

    return {
        "message":"Attendance Deleted"
    }