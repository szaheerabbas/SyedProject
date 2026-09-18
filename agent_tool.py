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

                    # Force authenticated customer
                    if "customer_id" in arguments:
                        arguments["customer_id"] = customer_id

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