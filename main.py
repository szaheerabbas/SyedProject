from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import date, time
from uuid import UUID
from check_availability import check_availability
from find_available_slots import find_available_slots as get_available_slots
from CreateAppointment import create_appointment 

app = FastAPI()

class AvailabilityRequest(BaseModel):
     CustomerId:int
     ProviderId:int
     AppointmentDate:date
     start_time:time
     end_time: time
     ServiceId:int
     Notes:str


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