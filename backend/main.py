from db_handler import execute_query
from ai_handler import generate_sql_from_prompt

print(execute_query("Select * from employees"));
print(generate_sql_from_prompt("Give me sql query to get all employees"));