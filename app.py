from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)


def create_database():
    try:
        # Connect to default database to create our app database
        print("Attempting to connect to default postgres database...")
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database="postgres",  # Connect to default postgres database
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
        conn.autocommit = True  # Required for creating database
        cur = conn.cursor()

        # Check if database exists
        cur.execute(
            "SELECT 1 FROM pg_catalog.pg_database WHERE datname = %s",
            (os.getenv("DB_NAME"),),
        )
        exists = cur.fetchone()

        if not exists:
            print(f"Creating database {os.getenv('DB_NAME')}...")
            cur.execute(f"CREATE DATABASE {os.getenv('DB_NAME')}")
            print("Database created successfully!")
        else:
            print(f"Database {os.getenv('DB_NAME')} already exists!")

        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error in create_database: {str(e)}")
        raise e


# Function to get a database connection
def get_db_connection():
    try:
        print(f"Connecting to database {os.getenv('DB_NAME')}...")
        print(
            f"Connection params: host={os.getenv('DB_HOST')}, "
            f"user={os.getenv('DB_USER')}, db={os.getenv('DB_NAME')}"
        )
        conn = psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
        print("Database connection successful!")
        return conn
    except Exception as e:
        print(f"Error in get_db_connection: {str(e)}")
        raise e


# Create tasks table if it doesn't exist
def create_tasks_table():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            task TEXT NOT NULL
        );
    """
    )
    conn.commit()
    cur.close()
    conn.close()


# Route to get all tasks
@app.route("/tasks", methods=["GET"])
def get_tasks():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM tasks;")
        tasks = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify([dict(task) for task in tasks])
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to get a single task
@app.route("/tasks/<int:task_id>", methods=["GET"])
def get_task(task_id):
    try:
        if task_id < 1:
            msg = "Invalid task ID. Task ID must be greater than 0"
            return jsonify({"error": msg}), 400

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM tasks WHERE id = %s;", (task_id,))
        task = cur.fetchone()
        cur.close()
        conn.close()

        if task is None:
            return jsonify({"error": f"Task with ID {task_id} not found"}), 404

        return jsonify(dict(task))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to add a new task
@app.route("/tasks", methods=["POST"])
def add_task():
    try:
        if not request.json or "task" not in request.json:
            return jsonify({"error": "Task content is required"}), 400

        new_task = request.json["task"]
        if not new_task or not isinstance(new_task, str):
            return jsonify({"error": "Task must be a non-empty string"}), 400

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(
            "INSERT INTO tasks (task) VALUES (%s) RETURNING id, task;",
            (new_task,),
        )
        task = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(dict(task)), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to update a task
@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_task(task_id):
    try:
        if task_id < 1:
            msg = "Invalid task ID. Task ID must be greater than 0"
            return jsonify({"error": msg}), 400

        if not request.json or "task" not in request.json:
            return jsonify({"error": "Task content is required"}), 400

        updated_task = request.json["task"]
        if not updated_task or not isinstance(updated_task, str):
            return jsonify({"error": "Task must be a non-empty string"}), 400

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # First check if the task exists
        cur.execute("SELECT id FROM tasks WHERE id = %s;", (task_id,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({"error": f"Task with ID {task_id} not found"}), 404

        # Then update the task
        cur.execute(
            "UPDATE tasks SET task = %s WHERE id = %s RETURNING id, task;",
            (updated_task, task_id),
        )
        task = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(dict(task))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Route to delete a task
@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    try:
        if task_id < 1:
            msg = "Invalid task ID. Task ID must be greater than 0"
            return jsonify({"error": msg}), 400

        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

        # First check if the task exists
        cur.execute("SELECT id FROM tasks WHERE id = %s;", (task_id,))
        if not cur.fetchone():
            cur.close()
            conn.close()
            return jsonify({"error": f"Task with ID {task_id} not found"}), 404

        # Then delete the task
        cur.execute(
            "DELETE FROM tasks WHERE id = %s RETURNING id, task;",
            (task_id,),
        )
        task = cur.fetchone()
        conn.commit()
        cur.close()
        conn.close()
        return jsonify(dict(task))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    try:
        # First create the database
        create_database()

        # Then create the table
        create_tasks_table()

        # Finally run the app
        print("Starting Flask application...")
        app.run(debug=True)
    except Exception as e:
        print(f"Error during startup: {e}")
