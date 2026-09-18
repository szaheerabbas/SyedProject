import os
import pyodbc
from dotenv import load_dotenv
from db import get_connection
from datetime import date, time

def find_Service(ServiceName:str):
     connection = get_connection()
     cursor = connection.cursor()
     try:

            query = """
                   SELECT ServiceId     
                   FROM [AIAppointmentBookingDB].[dbo].[Services] 
                   where ServiceName= ? 
               """
       
            cursor.execute(query, (ServiceName))

            row = cursor.fetchone()

            return {
                        "ServiceId": row.ServiceId
                   }   

     finally:
        connection.close()  


if __name__ == "__main__":
    service_id = find_Service("General Consultation")

    print(service_id)        
        