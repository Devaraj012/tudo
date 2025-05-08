from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import mariadb
from pydantic import BaseModel
import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins. You can specify your app’s URL here.
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Database connection
def get_db_connection():
    try:
        connection = mariadb.connect(  # Use mariadb.connect
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT")),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        return connection
    except mariadb.Error as err:
        # Handle connection errors robustly
        print(f"Error connecting to MariaDB: {err}")
        raise  # Re-raise the exception

# Pydantic model for Todo item
class TodoItem(BaseModel):
    title: str
    completed: bool = False

@app.get("/todos")
def read_todos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM todos")
    todos = cursor.fetchall()
    cursor.close()
    conn.close()
    return todos

@app.post("/todos")
def create_todo(todo: TodoItem):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO todos (title, completed) VALUES (%s, %s)", (todo.title, todo.completed))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Todo created successfully"}

@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, todo: TodoItem):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE todos SET title = %s, completed = %s WHERE id = %s", (todo.title, todo.completed, todo_id))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Todo updated successfully"}

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM todos WHERE id = %s", (todo_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Todo deleted successfully"}
