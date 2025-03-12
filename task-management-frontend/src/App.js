import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [tasks, setTasks] = useState([]);
  const [newTask, setNewTask] = useState('');
  const [editTaskId, setEditTaskId] = useState(null);
  const [editTaskText, setEditTaskText] = useState('');
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  // Check if the user is already logged in
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setIsLoggedIn(true);
      fetchTasks();
    }
  }, []);

  // Fetch tasks from the backend
  const fetchTasks = () => {
    fetch('http://127.0.0.1:5000/tasks', {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to fetch tasks');
        }
        return response.json();
      })
      .then(data => setTasks(data))
      .catch(error => console.error('Error fetching tasks:', error));
  };

  // User Registration
  const register = () => {
    fetch('http://127.0.0.1:5000/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Registration failed');
        }
        return response.json();
      })
      .then(data => {
        setError('');
        alert('Registration successful. Please login.');
      })
      .catch(error => setError(error.message));
  };

  // User Login
  const login = () => {
    fetch('http://127.0.0.1:5000/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Login failed');
        }
        return response.json();
      })
      .then(data => {
        localStorage.setItem('token', data.access_token);
        setIsLoggedIn(true);
        setError('');
        fetchTasks();
      })
      .catch(error => setError(error.message));
  };

  // Add a new task
  const addTask = () => {
    fetch('http://127.0.0.1:5000/tasks', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({ task: newTask }),
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to add task');
        }
        return response.json();
      })
      .then(data => {
        setTasks([...tasks, data]);
        setNewTask('');
      })
      .catch(error => console.error('Error adding task:', error));
  };

  // Update a task
  const updateTask = (id) => {
    fetch(`http://127.0.0.1:5000/tasks/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
      body: JSON.stringify({ task: editTaskText }),
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to update task');
        }
        return response.json();
      })
      .then(data => {
        const updatedTasks = tasks.map((task, index) =>
          index === id ? data : task
        );
        setTasks(updatedTasks);
        setEditTaskId(null);
        setEditTaskText('');
      })
      .catch(error => console.error('Error updating task:', error));
  };

  // Delete a task
  const deleteTask = (id) => {
    fetch(`http://127.0.0.1:5000/tasks/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`,
      },
    })
      .then(response => {
        if (!response.ok) {
          throw new Error('Failed to delete task');
        }
        setTasks(tasks.filter((task, index) => index !== id));
      })
      .catch(error => console.error('Error deleting task:', error));
  };

  // Logout
  const logout = () => {
    localStorage.removeItem('token');
    setIsLoggedIn(false);
    setTasks([]);
  };

  return (
    <div className="App">
      <h1>Task Management App</h1>
      {!isLoggedIn ? (
        <div>
          <h2>Login / Register</h2>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button onClick={login}>Login</button>
          <button onClick={register}>Register</button>
          {error && <p style={{ color: 'red' }}>{error}</p>}
        </div>
      ) : (
        <div>
          <button onClick={logout}>Logout</button>
          <div>
            <input
              type="text"
              value={newTask}
              onChange={(e) => setNewTask(e.target.value)}
              placeholder="Add a new task"
            />
            <button onClick={addTask}>Add Task</button>
          </div>
          <ul>
            {tasks.map((task, index) => (
              <li key={index}>
                {editTaskId === index ? (
                  <>
                    <input
                      type="text"
                      value={editTaskText}
                      onChange={(e) => setEditTaskText(e.target.value)}
                    />
                    <button onClick={() => updateTask(index)}>Save</button>
                  </>
                ) : (
                  <>
                    {task.task}
                    <button onClick={() => { setEditTaskId(index); setEditTaskText(task.task); }}>Edit</button>
                    <button onClick={() => deleteTask(index)}>Delete</button>
                  </>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default App;