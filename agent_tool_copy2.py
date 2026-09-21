import ollama
from cancel_appointment import cancel_appointment
from check_availability import check_availability
from find_available_slots import find_available_slots
from create_appointment import create_appointment
from reschedule_appointment import reschedule_appointment
from find_provider import find_Provider
from find_service import find_Service
from datetime import datetime
from zoneinfo import ZoneInfo

APP_TIMEZONE = ZoneInfo("America/Chicago")

now = datetime.now(APP_TIMEZONE)

current_date = now.strftime("%Y-%m-%d")
current_time = now.strftime("%H:%M:%S")

MODEL = "qwen3:8b"


AVAILABLE_TOOLS = {
    "cancel_appointment": cancel_appointment,
    "check_availability": check_availability,
    "find_available_slots": find_available_slots,
    "create_appointment": create_appointment,
    "reschedule_appointment": reschedule_appointment,
    "find_Provider": find_Provider,
    "find_Service": find_Service
}


TOOLS = [
    cancel_appointment,
    check_availability,
    find_available_slots,
    create_appointment,
    reschedule_appointment,
    find_Provider,
    find_Service
]



def run_agent(customer_id, messages):

    system_message = {
        "role": "system",
        "content": f"""
You are an appointment booking assistant.

The authenticated customer ID is {customer_id}.

You can help customers:
- find providers
- find services
- check appointment availability
- find available appointment slots
- create appointments
- cancel appointments
- reschedule appointments

Never ask the customer for database IDs such as ProviderId,
ServiceId, or CustomerId.

Use the available tools to find those IDs when necessary.

The authenticated customer ID must always be used for
customer-specific operations.
DATE AND TIME RULES

- Current date: {current_date}
- Current time: {current_time}
- Timezone: America/Chicago

- Resolve "today", "tomorrow", "yesterday", and similar relative dates
  using the supplied current date.
- Never use dates from examples, training data, or previous conversations.
- Never invent a start_time or end_time that the user did not provide.
- If required information is genuinely missing, ask the user instead
  of guessing.
- Always pass dates to tools in YYYY-MM-DD format.


CONVERSATION CONTEXT RULES

- Use information the user has already provided in the current conversation.
- Do not ask the user again for information that has already been provided.
- If the user says "tomorrow", resolve it using the supplied current date.
- Once a relative date has been resolved, continue using the resolved date.
- Do not replace or reset a previously resolved date.

OOL USAGE RULES

Always use the available tools when the answer depends on appointment data in the database.

Never assume that an appointment slot is available or booked based only on conversation context.

Never claim that a time slot is booked unless a tool result confirms that the requested slot is unavailable.

Never claim that no appointment slots are available unless the availability tool has been called and returned no available slots.

BOOKING RULES

Before creating an appointment, ALWAYS call find_available_slots first.

Use the requested ProviderId, AppointmentDate, and ServiceId when calling find_available_slots.

Compare the user's requested StartTime and EndTime against the slots returned by find_available_slots.

Only call create_appointment if the requested time exactly matches an available slot returned by find_available_slots.

If the requested time is not returned by find_available_slots, do NOT call create_appointment.

If the requested time is unavailable, tell the customer that the requested time is unavailable and offer the available slots returned by the tool.

Never create an appointment based only on information from the conversation.

AVAILABILITY RULES

When the customer asks whether a time or date is available, ALWAYS call the appropriate availability tool.

When the customer asks for available slots, ALWAYS call find_available_slots.

The database/tool result is the source of truth for appointment availability.

Do not infer availability from previous messages, previous tool results, examples, or model knowledge.

CANCELLATION RULES

For cancellation, use the appointment information available in the conversation or retrieve it with the appropriate tool when necessary.

Do not claim that an appointment has been cancelled unless the cancellation operation succeeds.

RESCHEDULING RULES

Before rescheduling an appointment to a new date/time, ALWAYS verify that the requested new slot is available.

Do not claim that a reschedule succeeded unless the rescheduling operation succeeds.

Do not assume the requested new slot is available based on conversation context.

"""
    }

    llm_messages = [system_message] + messages

    while True:

        response = ollama.chat(
            model=MODEL,
            messages=llm_messages,
            tools=TOOLS,
        )

        print("RAW RESPONSE:")
        print(response)

        print("\nTOOL CALLS:")
        print(response.message.tool_calls)

        # No tool call - Ollama has produced the final answer
        if not response.message.tool_calls:
            return response.message.content

        # Add Ollama's tool-call message to the conversation
        llm_messages.append(response.message)

        # Execute every requested tool
                # Execute every requested tool
        for tool_call in response.message.tool_calls:

            tool_name = tool_call.function.name
            arguments = tool_call.function.arguments

            print("\nTOOL:", tool_name)
            print("ARGUMENTS:", arguments)

            function = AVAILABLE_TOOLS.get(tool_name)

            if function is None:
                result = {
                    "success": False,
                    "error": f"Unknown tool: {tool_name}"
                }

            else:
                try:

                    # ---------------------------------------------------------
                    # Always use the authenticated customer ID
                    # ---------------------------------------------------------
                    if "customer_id" in arguments:
                        arguments["customer_id"] = customer_id


                    # ---------------------------------------------------------
                    # BOOKING GUARD
                    #
                    # Never allow create_appointment to execute unless the
                    # requested slot has first been verified as available.
                    # ---------------------------------------------------------
                    if tool_name == "create_appointment":

                        provider_id = arguments.get("provider_id")
                        service_id = arguments.get("service_id")
                        appointment_date = arguments.get("appointment_date")
                        requested_start = arguments.get("start_time")
                        requested_end = arguments.get("end_time")

                        print("\nBOOKING GUARD")
                        print("Provider:", provider_id)
                        print("Service:", service_id)
                        print("Date:", appointment_date)
                        print("Requested Start:", requested_start)
                        print("Requested End:", requested_end)

                        # -----------------------------------------------------
                        # Validate required booking information
                        # -----------------------------------------------------
                        if (
                            provider_id is None
                            or service_id is None
                            or appointment_date is None
                            or requested_start is None
                            or requested_end is None
                        ):
                            result = {
                                "success": False,
                                "error": (
                                    "Cannot create appointment because "
                                    "provider, service, date, start time, "
                                    "or end time is missing."
                                )
                            }

                        else:

                            # -------------------------------------------------
                            # FIRST: Check availability
                            # -------------------------------------------------
                            availability_result = find_available_slots(
                                ProviderId=int(provider_id),
                                AppointmentDate=appointment_date,
                                ServiceId=int(service_id)
                            )

                            print("\nBOOKING GUARD - AVAILABILITY RESULT:")
                            print(availability_result)

                            # -------------------------------------------------
                            # Compare requested time against available slots
                            # -------------------------------------------------
                            slot_available = False

                            for slot in availability_result:

                                slot_start = slot["StartTime"]
                                slot_end = slot["EndTime"]
                                slot_date = slot["AvailableDate"]

                                # Convert values to strings for reliable
                                # comparison regardless of whether SQL Server
                                # returned date/time objects or strings.
                                slot_date_str = str(slot_date)
                                appointment_date_str = str(appointment_date)

                                slot_start_str = str(slot_start)
                                slot_end_str = str(slot_end)

                                requested_start_str = str(requested_start)
                                requested_end_str = str(requested_end)

                                print("\nCOMPARING SLOT:")
                                print("Slot Date:", slot_date_str)
                                print("Requested Date:", appointment_date_str)
                                print("Slot Start:", slot_start_str)
                                print("Requested Start:", requested_start_str)
                                print("Slot End:", slot_end_str)
                                print("Requested End:", requested_end_str)

                                if (
                                    slot_date_str == appointment_date_str
                                    and slot_start_str == requested_start_str
                                    and slot_end_str == requested_end_str
                                ):
                                    slot_available = True
                                    break

                            # -------------------------------------------------
                            # DO NOT CREATE if slot is unavailable
                            # -------------------------------------------------
                            if not slot_available:

                                print(
                                    "\nBOOKING GUARD: "
                                    "REQUESTED SLOT IS NOT AVAILABLE"
                                )

                                result = {
                                    "success": False,
                                    "error": "The requested appointment time is not available.",
                                    "available_slots": availability_result
                                }

                            # -------------------------------------------------
                            # ONLY NOW allow create_appointment
                            # -------------------------------------------------
                            else:

                                print(
                                    "\nBOOKING GUARD: "
                                    "REQUESTED SLOT IS AVAILABLE"
                                )

                                result = function(**arguments)


                    # ---------------------------------------------------------
                    # All other tools execute normally
                    # ---------------------------------------------------------
                    else:
                        result = function(**arguments)


                except Exception as e:

                    result = {
                        "success": False,
                        "error": str(e)
                    }


            print("TOOL RESULT:", result)

            # Send tool result back to Ollama
            llm_messages.append({
                "role": "tool",
                "tool_name": tool_name,
                "content": str(result)
            })



if __name__ == "__main__":

    print("Appointment booking assistant")
    print("Type 'exit' to quit.")

    while True:

        user_input = input("\nUser: ")

        if user_input.lower() == "exit":
            break


        messages = [
        {
            "role": "user",
            "content": user_input
        }
       ]    
        answer = run_agent(1, messages)

        print("\nAgent:", answer)  