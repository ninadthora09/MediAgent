import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain import agents
from langchain.tools import tool
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from tools import check_slots, book_appointment, cancel_appointment

load_dotenv()

# ---------- Step 1: Wrap tools for LangChain ----------

@tool
def check_slots_tool(doctor_name: str, slot_date: str) -> str:
    """
    Check available appointment slots for a doctor on a specific date.
    Use this when the patient asks about availability.
    Input date format must be YYYY-MM-DD.
    """
    return check_slots(doctor_name, slot_date)


@tool
def book_appointment_tool(patient_name: str, patient_email: str,
                           doctor_name: str, slot_date: str, slot_time: str) -> str:
    """
    Book an appointment for a patient with a doctor.
    Use this when the patient confirms they want to book a slot.
    Input date format must be YYYY-MM-DD.
    Input time format must match exactly as shown in available slots.
    Always collect patient name and email before booking.
    """
    return book_appointment(patient_name, patient_email, doctor_name, slot_date, slot_time)


@tool
def cancel_appointment_tool(appointment_id: int) -> str:
    """
    Cancel an existing appointment using the appointment ID.
    Use this when the patient wants to cancel their booking.
    Always confirm the appointment ID before cancelling.
    """
    return cancel_appointment(appointment_id)


# ---------- Step 2: Setup LLM ----------

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model="llama-3.1-8b-instant",
    temperature=0
)


# ---------- Step 3: Setup Prompt ----------

prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are MediAgent, a helpful and professional AI assistant for a healthcare clinic.
Your job is to help patients book, check, and cancel appointments.

Rules:
- Always be polite and professional
- Before booking, always ask for patient name and email if not provided
- If a requested slot is not available, always suggest alternatives using check_slots_tool
- Date format is always YYYY-MM-DD
- If you are unsure about anything, ask the patient to clarify
- After booking, always confirm the appointment details back to the patient
"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])


# ---------- Step 4: Create Agent ----------

tools = [check_slots_tool, book_appointment_tool, cancel_appointment_tool]

agent = create_tool_calling_agent(llm, tools, prompt)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,
    handle_parsing_errors=True
)


# ---------- Step 5: Chat function with memory ----------

chat_histories = {}

def chat(session_id: str, user_message: str) -> str:
    if session_id not in chat_histories:
        chat_histories[session_id] = []

    history = chat_histories[session_id]

    response = agent_executor.invoke({
        "input": user_message,
        "chat_history": history
    })

    # Update history
    history.append(HumanMessage(content=user_message))
    history.append(AIMessage(content=response["output"]))

    return response["output"]