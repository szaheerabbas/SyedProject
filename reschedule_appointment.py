from db import get_connection

def reschedule_appointment(
AppointmentId: int,
AppointmentDate,
StartTime,
EndTime
):
  
  connection = get_connection()
  cursor = connection.cursor()

  try:
        cursor.execute(
                """
                EXEC RescheduleAppointment
                    @AppointmentId = ?,
                    @AppointmentDate = ?,
                    @StartTime = ?,
                    @EndTime = ?
                """,
                AppointmentId,
                AppointmentDate,
                StartTime,
                EndTime
            )

        result = cursor.fetchone()

        connection.commit()
        return {
                "success": bool(result[0]),
                "AppointmentId": int(result[1]),
                "CustomerId": int(result[2]),
                "ProviderId": int(result[3]),
                "ServiceId": int(result[4]),
                "AppointmentDate": result[5],
                "StartTime": result[6],
                "EndTime": result[7],
                "StatusId": int(result[8]),
                "Notes": result[9]
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