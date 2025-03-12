import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import App from '../src/App';

// Mock the fetch function
global.fetch = jest.fn();

describe('App Component', () => {
    beforeEach(() => {
        // Clear all mocks before each test
        fetch.mockClear();
    });

    test('renders task list and form', () => {
        render(<App />);
        
        // Check if main elements are rendered
        expect(screen.getByPlaceholderText(/Enter a new task/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /add task/i })).toBeInTheDocument();
    });

    test('loads and displays tasks', async () => {
        const mockTasks = [
            { id: 1, task: 'Test task 1' },
            { id: 2, task: 'Test task 2' }
        ];

        // Mock the fetch response for GET tasks
        fetch.mockImplementationOnce(() =>
            Promise.resolve({
                ok: true,
                json: () => Promise.resolve(mockTasks)
            })
        );

        render(<App />);

        // Wait for tasks to be displayed
        await waitFor(() => {
            expect(screen.getByText('Test task 1')).toBeInTheDocument();
            expect(screen.getByText('Test task 2')).toBeInTheDocument();
        });
    });

    test('adds a new task', async () => {
        const newTask = { id: 1, task: 'New test task' };

        // Mock the fetch response for POST task
        fetch.mockImplementationOnce(() =>
            Promise.resolve({
                ok: true,
                json: () => Promise.resolve(newTask)
            })
        );

        render(<App />);

        // Get input and button
        const input = screen.getByPlaceholderText(/Enter a new task/i);
        const addButton = screen.getByRole('button', { name: /add task/i });

        // Type in the input and click add
        fireEvent.change(input, { target: { value: 'New test task' } });
        fireEvent.click(addButton);

        // Wait for the new task to be displayed
        await waitFor(() => {
            expect(screen.getByText('New test task')).toBeInTheDocument();
        });
    });

    test('updates a task', async () => {
        const updatedTask = { id: 1, task: 'Updated task' };

        // Mock the fetch response for PUT task
        fetch.mockImplementationOnce(() =>
            Promise.resolve({
                ok: true,
                json: () => Promise.resolve(updatedTask)
            })
        );

        render(<App />);

        // Simulate clicking edit button and updating task
        const editButton = screen.getByRole('button', { name: /edit/i });
        fireEvent.click(editButton);

        const input = screen.getByDisplayValue(/test task/i);
        fireEvent.change(input, { target: { value: 'Updated task' } });

        const saveButton = screen.getByRole('button', { name: /save/i });
        fireEvent.click(saveButton);

        // Wait for the updated task to be displayed
        await waitFor(() => {
            expect(screen.getByText('Updated task')).toBeInTheDocument();
        });
    });

    test('deletes a task', async () => {
        // Mock the fetch response for DELETE task
        fetch.mockImplementationOnce(() =>
            Promise.resolve({
                ok: true,
                json: () => Promise.resolve({})
            })
        );

        render(<App />);

        // Click delete button
        const deleteButton = screen.getByRole('button', { name: /delete/i });
        fireEvent.click(deleteButton);

        // Wait for the task to be removed
        await waitFor(() => {
            expect(screen.queryByText('Test task')).not.toBeInTheDocument();
        });
    });

    test('handles API errors', async () => {
        // Mock a failed API call
        fetch.mockImplementationOnce(() =>
            Promise.resolve({
                ok: false,
                status: 500,
                json: () => Promise.resolve({ error: 'Server error' })
            })
        );

        render(<App />);

        // Wait for error message
        await waitFor(() => {
            expect(screen.getByText(/error/i)).toBeInTheDocument();
        });
    });

    test('validates task input', () => {
        render(<App />);

        const addButton = screen.getByRole('button', { name: /add task/i });
        fireEvent.click(addButton);

        // Check if validation message appears
        expect(screen.getByText(/task cannot be empty/i)).toBeInTheDocument();
    });
}); 