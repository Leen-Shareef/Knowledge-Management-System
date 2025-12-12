# rag_pipeline/agent_setup.py

from langchain.agents import AgentExecutor
from langchain.agents.output_parsers import ReActSingleInputOutputParser
from langchain.agents.format_scratchpad import format_log_to_str
from langchain.tools.render import render_text_description
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from datetime import date

# Local imports
from app.tools.agent_tools import get_password_change_tool, get_knowledge_tool, get_leave_tool
from rag_pipeline.llm_models import initialize_llm

# --- PROMPT WITH SINGLE-STRING INSTRUCTION ---
AGENT_PROMPT_TEMPLATE = """
You are the KNAgent.

**Current Date:** {current_date}

**Tools:**
{tools}

**Instructions:**
1. **Greetings:** If the user greets you, just reply naturally. DO NOT use tools.
2. **Knowledge:** Use 'search_knowledge_base' for policies.
3. **Passwords:** Use 'change_my_password'. Input is just the new password.
4. **Leave:** Use 'apply_for_leave'. 
   - **CRITICAL:** The Action Input must be a SINGLE string separated by commas: "Start, End, Reason".
   - Example: "2025-12-01, 2025-12-05, Sick leave"
   - If the user says "one day", Start and End are the same date.

**Format:**
Question: the input question
Thought: think about what to do
Action: the action to take, must be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
...
Final Answer: the final response

Begin!

Question: {input}
Thought:{agent_scratchpad}
"""

def create_agent_system(user_id: str, session_id: str, user_role: str):
    llm = initialize_llm()
    
    # 1. Initialize Tools
    password_tool = get_password_change_tool(user_id) 
    knowledge_tool = get_knowledge_tool(user_role)
    leave_tool = get_leave_tool(user_id)
    
    tools = [knowledge_tool, password_tool, leave_tool]
    tool_names = ", ".join([t.name for t in tools])
    
    # 2. Build Prompt
    prompt = PromptTemplate.from_template(AGENT_PROMPT_TEMPLATE).partial(
        user_email=user_id,
        current_date=date.today().strftime("%Y-%m-%d"),
        tools=render_text_description(tools),
        tool_names=tool_names,
        user_role=user_role
    )
    
    # 3. Create Agent
    agent = (
        RunnablePassthrough.assign(
            agent_scratchpad=lambda x: format_log_to_str(x["intermediate_steps"]),
        )
        | prompt
        | llm.bind(stop=["\nObservation"]) 
        | ReActSingleInputOutputParser()
    )
    
    # 4. Create Executor
    agent_executor = AgentExecutor(
        agent=agent, 
        tools=tools, 
        verbose=True, 
        handle_parsing_errors=True
    )
    
    return agent_executor