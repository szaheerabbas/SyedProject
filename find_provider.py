import os
import pyodbc
from dotenv import load_dotenv
from db import get_connection
from datetime import date, time

def find_Provider(name:str):
     connection = get_connection()
     cursor = connection.cursor()
     try:

            query = """
                   SELECT ProviderId     
                   FROM [AIAppointmentBookingDB].[dbo].[Providers] 
                   where FirstName LIKE '%' + ? + '%'
                    OR LastName LIKE '%' + ? + '%'
                    OR (FirstName + ' ' + LastName) LIKE '%' + ? + '%' 
               """
            
            cursor.execute(query,(name, name, name))

            row = cursor.fetchone()
            if row:
                 return {
                             "ProviderId": row.ProviderId
                          }   
            else:
                return {
                           " Provider not found"
                    }    
            

     finally:
        connection.close()  


if __name__ == "__main__":
    provider_id = find_Provider("Sarah Johnson")

    print(provider_id)        
        