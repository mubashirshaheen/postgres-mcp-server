import uuid

from asgiref.sync import async_to_sync

from postgresmcpserver import PostgresMCPServer

# prompt = "list all tables in public schema"
prompt = "list names of columns in tbl_students in public schema"
# thread_id = input("thread_id")
# if not thread_id:
thread_id = str(uuid.uuid4())

agent = PostgresMCPServer()

answer = async_to_sync(agent.run_agent)(prompt, thread_id)
if isinstance(answer, dict) and answer.get("type") == "text":
    answer = answer.get("text")


print({"answer": answer, "thread_id": thread_id})
