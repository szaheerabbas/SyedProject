import os
import pyodbc
from dotenv import load_dotenv
from db import get_connection
from datetime import date, time

def get_appointment_status(AppointmentId:int):
     connection = get_connection()
     cursor = connection.cursor()
     print("AppointmentId:", AppointmentId)
     appoinment =[]
     try:
                query = """
                    SELECT
                    a.AppointmentId,
                    a.CustomerId,
                    a.ProviderId,
                    a.ServiceId,
                    a.AppointmentDate,
                    a.StartTime,
                    a.EndTime,
                    a.StatusId,
                    s.StatusName,
                    a.Notes
                FROM dbo.Appointments AS a
                LEFT JOIN dbo.AppointmentStatus AS s
                    ON a.StatusId = s.StatusId
                WHERE a.AppointmentId = ?;
                """

                cursor.execute(query, (AppointmentId,))
                rows = cursor.fetchall()
                for row in rows:
                       appoinment.append({"found":True,
                                        "appointment_id": row.AppointmentId,
                                        "customer_id": row.CustomerId,
                                        "provider_id": row.ProviderId,
                                        "service_id": row.ServiceId,
                                        "appointment_date": str(row.AppointmentDate),
                                        "start_time": str(row.StartTime),
                                        "end_time": str(row.EndTime),
                                        "status_id": row.StatusId,
                                        "status_name": row.StatusName,
                                        "notes": row.Notes
                                        })
                       
                  
                return appoinment 
                   
    
     finally:
         connection.close()  



if __name__ == "__main__":
  appintment_status = get_appointment_status(AppointmentId=16)
  print(appintment_status)           