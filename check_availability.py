import os
import pyodbc
from dotenv import load_dotenv
from db import get_connection
from datetime import date, time

def check_availability(ProviderId:int,  AppointmentDate: date, start_time: time, end_time: time ) -> bool:
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        EXEC CheckAvailability
            @ProviderId = ?,
            @AppointmentDate = ?,
            @StartTime = ?,
            @EndTime = ?
        """,
        ProviderId,
        AppointmentDate,
        start_time,
        end_time
    )

    result = cursor.fetchone()

    return bool(result[0])

if __name__ == "__main__":
    available = check_availability(
    ProviderId=3,
    AppointmentDate=date(2026, 9, 15),
    start_time=time(11, 0),
    end_time=time(11, 30)
)

    print(available)

