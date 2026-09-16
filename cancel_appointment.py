import pyodbc
from db import get_connection

def cancel_appointment(AppointmentId: int):
  connection = get_connection()
  cursor = connection.cursor()

  try:
        cursor.execute(
            """
            EXEC CancelAppointment
                @AppointmentId = ?
            """,
            AppointmentId
        )

        result = cursor.fetchone()

        connection.commit()

        return {
            "success": bool(result[0]),
            "AppointmentId": int(result[1]),
            "StatusId": int(result[2])
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
  cancel_appintment = cancel_appointment(AppointmentId=13)
  print(cancel_appintment)  