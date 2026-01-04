import React, { createContext, useContext, useState, useEffect } from 'react';
import { fetchTasks, createTask, updateTask, deleteTask, smartAdd } from "@/lib/utils";

const TasksContext = createContext();

export function TasksProvider({ children }) {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  // Initial load
  useEffect(() => {
    refreshTasks();
  }, []);

  async function refreshTasks() {
    try {
      setLoading(true);
      const data = await fetchTasks();
      setTasks(data);
    } catch (error) {
      console.error("Failed to fetch tasks:", error);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateTask(taskData) {
    try {
      const newTask = await createTask(taskData);
      setTasks(prev => [newTask, ...prev]);
      return newTask;
    } catch (error) {
      console.error("Failed to create task:", error);
      throw error;
    }
  }

  async function handleSmartAdd(text) {
    try {
      console.log("🚀 Starting smart add for:", text);
      const result = await smartAdd(text);
      console.log("✅ Smart add result received:", result);
      
      // Backend might return a single task or an array of tasks
      if (result) {
          if (Array.isArray(result)) {
              console.log(`📝 Adding ${result.length} tasks to state`);
              setTasks(prev => [...result, ...prev]);
          } else {
              console.log("📝 Adding 1 task to state");
              setTasks(prev => [result, ...prev]);
          }
      }
      return result;
    } catch (error) {
      console.error("❌ Failed to smart add task:", error);
      throw error;
    }
  }

  async function handleUpdateTask(taskId, updates) {
    try {
        // Optimistic update
        setTasks(prev => prev.map(t => t.id === taskId ? { ...t, ...updates } : t));
        
        const updatedTask = await updateTask(taskId, updates);
        
        // Reconcile with server response
        setTasks(prev => prev.map(t => t.id === taskId ? updatedTask : t));
        return updatedTask;
    } catch (error) {
        console.error("Failed to update task:", error);
        // Revert on error (would need previous state tracking in a real app)
        await refreshTasks(); 
        throw error;
    }
  }

  async function handleDeleteTask(taskId) {
    try {
        // Optimistic update
        setTasks(prev => prev.filter(t => t.id !== taskId));
        await deleteTask(taskId);
    } catch (error) {
        console.error("Failed to delete task:", error);
        await refreshTasks();
        throw error;
    }
  }

  return (
    <TasksContext.Provider value={{
      tasks,
      loading,
      refreshTasks,
      createTask: handleCreateTask,
      smartAdd: handleSmartAdd,
      updateTask: handleUpdateTask,
      deleteTask: handleDeleteTask
    }}>
      {children}
    </TasksContext.Provider>
  );
}

export function useTasks() {
  const context = useContext(TasksContext);
  if (!context) {
    throw new Error("useTasks must be used within a TasksProvider");
  }
  return context;
}
