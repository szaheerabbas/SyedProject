from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date, time
from uuid import UUID
from check_availability import check_availability
from find_available_slots import find_available_slots as get_available_slots
from create_appointment import create_appointment 
from cancel_appointment import cancel_appointment
from reschedule_appointment import reschedule_appointment
from agent_tool import run_agent
from context import (
     get_or_create_conversation,
     get_recent_messages,
    save_message
)
app = FastAPI()

class AvailabilityRequest(BaseModel):
     CustomerId:int
     ProviderId:int
     AppointmentDate:date
     start_time:time
     end_time: time
     ServiceId:int
     Notes:str
     AppointmentId:int


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "AI Appointment Booking API"}

@app.post("/check-availability")
def check_availability_endpoint(request: AvailabilityRequest):

    available = check_availability(
        ProviderId=request.provider_id,
        AppointmentDate=request.appointment_date,
        start_time=request.start_time,
        end_time=request.end_time
    )

    return {
        "available": available
    }

@app.get("/find_available_slots")
def find_available_slots(ProviderId: int,
    AppointmentDate: date,
    ServiceId: int):
      available = get_available_slots(
        ProviderId=ProviderId,
        AppointmentDate=AppointmentDate,
        ServiceId=ServiceId
    )

      return available  

@app.post("/create-appointment")
def create_appointment_endpoint(CustomerId: int,ProviderId: int,
                                ServiceId:int,
                                AppointmentDate:date,StartTime:time, EndTime:time, Notes:str):
      appintment = create_appointment(
         CustomerId=CustomerId,    
         ProviderId=ProviderId,
         ServiceId=ServiceId,
         AppointmentDate=AppointmentDate,   
         StartTime = StartTime,
         EndTime = EndTime,
         Notes = Notes
       )

      return appintment

@app.post("/cancel-appointment")
def cancel_appointment_endpoint(AppointmentId: int):
    result = cancel_appointment(AppointmentId)
    return result



@app.post("/reschedule-appointment")
def reschedule_appointment_endpoint(AppointmentId: int, AppointmentDate: date, StartTime:time, EndTime:time):
    result = reschedule_appointment(AppointmentId,AppointmentDate,StartTime, EndTime)
    return result


@app.post("/conversation/{customer_id}")
def get_conversation(customer_id: int):
    conversation_id = get_or_create_conversation(customer_id)
    print("Conversation_ID:", conversation_id)
    return {
        "conversation_id": str(conversation_id)
    }

@app.get("/get_messages/{conversation_id}")
def get_messages(conversation_id: str):
    recent_messages  = get_recent_messages(conversation_id)
    # print("Recent Messages:", recent_messages)
    return {
        "messages": recent_messages 
    }

@app.post("/agent/{customer_id}")
def get_agent(customer_id: int, request: AvailabilityRequest):
   
    print("CUSTOMER:", customer_id)
    print("MESSAGE:", request.message)
    print("Conversation_ID:", request.conversation_id)
    save_message(
                request.conversation_id,
                "user",
                request.message,
    )
    messages = [
        {
            "role": "user",
            "content": request.message
        }
    ]

    result = run_agent(customer_id, messages)
    save_message(
        request.conversation_id,
        "assistant",
        result
       
    )

    print("AGENT RESULT:", result)

    return result
