import os
import pyodbc
from dotenv import load_dotenv
from db import get_connection
from datetime import date, time

def create_appointment(customer_id: int,provider_id: int,service_id:int,appointment_date:date,start_time:time, end_time:time, notes:str) -> dict:

    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
                    """
                    EXEC CreateAppointment
                        @CustomerId = ?,
                        @ProviderId = ?,
                        @ServiceId = ?,
                        @AppointmentDate=?,
                        @StartTime=?,
                        @EndTime=?,
                        @Notes=?

                    """,
                    customer_id,
                    provider_id,
                    service_id,
                    appointment_date,  
                    start_time,
                    end_time,
                    notes
                
                )
            
        AppointmentId = cursor.fetchone()[0]

        connection.commit()
        return {
                "success": True,
                 "AppointmentId": int(AppointmentId)
                }
    except Exception as e:
        connection.rollback()
        return {
            "success": False,
            "error": str(e)
        }
          
        
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    appintment = create_appointment(
    CustomerId=1,    
    ProviderId=3,
    ServiceId=1,
    AppointmentDate='2026-09-15',   
    StartTime = '10:00',
    EndTime = '10:30',
    Notes = 'Created through stored procedure'
  )

    print(appintment)