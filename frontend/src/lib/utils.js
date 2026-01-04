import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

export const API_BASE_URL = "http://localhost:8000";

export async function fetchTasks() {
    const response = await fetch(`${API_BASE_URL}/tasks`);
    if (!response.ok) throw new Error('Failed to fetch tasks');
    return response.json();
}

export async function createTask(task) {
    const response = await fetch(`${API_BASE_URL}/tasks`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(task),
    });
    if (!response.ok) throw new Error('Failed to create task');
    return response.json();
}

export async function updateTask(taskId, updates) {
    const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
        method: 'PATCH',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(updates),
    });
    if (!response.ok) throw new Error('Failed to update task');
    return response.json();
}

export async function deleteTask(taskId) {
    const response = await fetch(`${API_BASE_URL}/tasks/${taskId}`, {
        method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete task');
    return response.json(); // Assuming backend returns success message or deleted task
}

export async function smartAdd(text) {
    const response = await fetch(`${API_BASE_URL}/ai/smart-add`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            text,
            current_time: new Date().toLocaleString('en-US', { 
                weekday: 'long', 
                year: 'numeric', 
                month: 'long', 
                day: 'numeric', 
                hour: 'numeric', 
                minute: 'numeric', 
                second: 'numeric',
                timeZoneName: 'short' 
            }) 
        }),
    });
    if (!response.ok) throw new Error('Failed to create task with AI');
    return response.json();
}
