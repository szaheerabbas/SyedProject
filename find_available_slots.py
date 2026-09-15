import os
import pyodbc
from dotenv import load_dotenv
from db import get_connection
from datetime import date, time


def find_available_slots(ProviderId:int, AppointmentDate:date, ServiceId:int):
     connection = get_connection()
     cursor = connection.cursor()
     cursor.execute(
            """
            EXEC FindAvailableSlots
                @ProviderId = ?,
                @AppointmentDate = ?,
                @ServiceId = ?              
            """,
            ProviderId,
            AppointmentDate,
            ServiceId
           
        )
    
     rows = cursor.fetchall()
        
     slots = []

     for row in rows:
            slots.append({
                "ProviderId": row[0],
                "AvailableDate": row[1],
                "StartTime": row[2],
                "EndTime": row[3]
            })

            


     cursor.close()
     connection.close()
     return slots


# if __name__ == "__main__":
#     available = find_available_slots(
#     ProviderId=3,
#     AppointmentDate=date(2026, 9, 15),
#     ServiceId=1
# )

#     print(available)