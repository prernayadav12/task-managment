import json
import os
import sys
import unittest

# Add the parent directory to the Python path so we can import app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app  # noqa: E402


class TestApp(unittest.TestCase):
    def setUp(self):
        """Set up test client before each test."""
        self.app = app.test_client()
        self.app.testing = True

    def test_get_tasks_empty(self):
        """Test getting tasks when none exist."""
        response = self.app.get("/tasks")
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)

    def test_create_task(self):
        """Test creating a new task."""
        response = self.app.post(
            "/tasks",
            data=json.dumps({"task": "Test task"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn("id", data)
        self.assertIn("task", data)
        self.assertEqual(data["task"], "Test task")

    def test_create_task_invalid_input(self):
        """Test creating a task with invalid input."""
        # Test missing task field
        response = self.app.post(
            "/tasks",
            data=json.dumps({}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

        # Test empty task
        response = self.app.post(
            "/tasks",
            data=json.dumps({"task": ""}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_update_task(self):
        """Test updating a task."""
        # First create a task
        create_response = self.app.post(
            "/tasks",
            data=json.dumps({"task": "Test task"}),
            content_type="application/json",
        )
        task_id = json.loads(create_response.data)["id"]

        # Then update it
        update_response = self.app.put(
            f"/tasks/{task_id}",
            data=json.dumps({"task": "Updated task"}),
            content_type="application/json",
        )
        self.assertEqual(update_response.status_code, 200)
        data = json.loads(update_response.data)
        self.assertEqual(data["task"], "Updated task")

    def test_update_nonexistent_task(self):
        """Test updating a task that doesn't exist."""
        response = self.app.put(
            "/tasks/9999",
            data=json.dumps({"task": "Updated task"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 404)

    def test_update_invalid_task_id(self):
        """Test updating a task with invalid ID."""
        response = self.app.put(
            "/tasks/0",
            data=json.dumps({"task": "Updated task"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_delete_task(self):
        """Test deleting a task."""
        # First create a task
        create_response = self.app.post(
            "/tasks",
            data=json.dumps({"task": "Test task"}),
            content_type="application/json",
        )
        task_id = json.loads(create_response.data)["id"]

        # Then delete it
        delete_response = self.app.delete(f"/tasks/{task_id}")
        self.assertEqual(delete_response.status_code, 200)

        # Verify it's deleted
        get_response = self.app.get(f"/tasks/{task_id}")
        self.assertEqual(get_response.status_code, 404)

    def test_delete_nonexistent_task(self):
        """Test deleting a task that doesn't exist."""
        response = self.app.delete("/tasks/9999")
        self.assertEqual(response.status_code, 404)

    def test_delete_invalid_task_id(self):
        """Test deleting a task with invalid ID."""
        response = self.app.delete("/tasks/0")
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
