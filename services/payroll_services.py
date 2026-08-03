from datetime import datetime, time
from bson import ObjectId
from fastapi import HTTPException   

from models.payroll import PayrollCreate,PayrollResponse
from fastapi import HTTPException

from app.database import employees_collection,attendance_collection,leave_collection,payroll_collection

def generate_payroll_services(payroll:PayrollCreate):
    existing = payroll_collection.find_one({"employee_id":payroll.employee_id, "month": payroll.month, "year":payroll.year, "is_deleted":False})
    if existing: raise HTTPException(400, "Payroll Already Generated")

    employee = employees_collection.find_one({"_id":ObjectId(payroll.employee_id)})
    if not employee: raise HTTPException(404,"Employee not Found")

    base_salary = employee["salary"]

    attendance = list(attendance_collection.find({"employee_id":payroll.employee_id}))

    present_days = 0
    ot_amount = 0
    unpaid_leave_days = 0
    daily_salary = (base_salary/30)

    for row in attendance: 
        if row["status"] == "present":
            present_days += 1

            row_date = row["date"]
            if isinstance(row_date, str):
                row_date = datetime.fromisoformat(row_date).date()

            check_in = row["check_in"]
            check_out = row["check_out"]
            if isinstance(check_in, str):
                check_in = time.fromisoformat(check_in)
            if isinstance(check_out, str):
                check_out = time.fromisoformat(check_out)

            check_in_dt = datetime.combine(row_date, check_in)
            check_out_dt = datetime.combine(row_date, check_out)

            work_hrs = ((check_out_dt-check_in_dt).total_seconds())/3600

            if work_hrs > 8:
                ot_hrs = work_hrs - 8
                ot_amount += ot_hrs*100
            elif work_hrs < 8:
                ot_hrs = 8 - work_hrs
                ot_amount -= ot_hrs*100               
            
        elif row["status"] == "absent":
            unpaid_leave_days+=1

    approved_leaves = list(leave_collection.find({"employee_id":payroll.employee_id,"status":"approved"}))
    for leave in approved_leaves:
        if leave["leave_type"].upper() == "UNPAID":
            start = datetime.strptime(leave["start_date"],"%Y-%m-%d")
            end = datetime.strptime(leave["end_date"],"%Y-%m-%d")

            days = (end - start).days +1
            unpaid_leave_days += days

    deduction = unpaid_leave_days * daily_salary
    salary = present_days * daily_salary

    final_salary = salary + ot_amount - deduction

    data = {
        "employee_id":payroll.employee_id,
        "month": payroll.month,
        "year": payroll.year,
        "base_salary": base_salary,
        "present_days": present_days,
        "leave_days": unpaid_leave_days,
        "ot_amount": round(ot_amount,2),
        "deduction":round(deduction,2),
        "final":round(final_salary,2),
        "is_deleted": False
    }

    result = payroll_collection.insert_one(data)

    return PayrollResponse(
        id = str(result.inserted_id),
        **data
    )

def get_all_payroll_service():
    payrolls = payroll_collection.find({"is_deleted":False})

    result = []

    for payroll in payrolls:
        result.append(
            PayrollResponse(
                id = str(payroll["_id"]),
                employee_id= payroll["employee_id"],
                month= payroll["month"],
                year= payroll["year"],
                base_salary= payroll["base_salary"],
                present_days=payroll["present_days"],
                leave_days= payroll["leave_days"],
                ot_amount= payroll["ot_amount"],
                deduction= payroll["deduction"],
                final=payroll["final"]
            )
        )

    return result

def get_employee_payroll_service(employee_id):
    payrolls = payroll_collection.find({"employee_id":employee_id, "is_deleted":False})

    result = []

    for payroll in payrolls:
        result.append(
            PayrollResponse(
                id = str(payroll["_id"]),
                employee_id= payroll["employee_id"],
                month= payroll["month"],
                year= payroll["year"],
                base_salary= payroll["base_salary"],
                present_days=payroll["present_days"],
                leave_days= payroll["leave_days"],
                ot_amount= payroll["ot_amount"],
                deduction= payroll["deduction"],
                final=payroll["final"]
            )
        )

    return result

def get_payroll_by_id_service(payroll_id):
    payroll = payroll_collection.find_one({"_id":ObjectId(payroll_id), "is_deleted":False})
    if not payroll : raise HTTPException(404,"Payroll not found")

    return PayrollResponse(
        id = str(payroll["_id"]),
        employee_id= payroll["employee_id"],
        month= payroll["month"],
        year= payroll["year"],
        base_salary= payroll["base_salary"],
        present_days=payroll["present_days"],
        leave_days= payroll["leave_days"],
        ot_amount= payroll["ot_amount"],
        deduction= payroll["deduction"],
        final=payroll["final"]
    )

def delete_payroll_service(payroll_id):
    payroll = payroll_collection.find_one({"_id":ObjectId(payroll_id), "is_deleted":False})
    if not payroll : raise HTTPException(404,"Payroll not found")

    updated = payroll_collection.update_one({
        "_id":ObjectId(payroll_id)
    },{
        "$set":{
            "is_deleted":True
        }
    })
    if updated.matched_count == 0: raise HTTPException(404, "Payroll Not Found")

    return {
        "msg":"Payroll Deleted"
    }