import React from 'react';
import { Sidebar } from './components/Sidebar';
import { StickyBoard } from './components/StickyBoard';
import { MiniCalendar } from './components/MiniCalendar';
import { TasksProvider } from './contexts/TasksContext';

function App() {
  return (
    <TasksProvider>
      <div className="flex h-screen bg-background text-foreground overflow-hidden font-sans">
        <Sidebar className="shrink-0" />
        <main className="flex-1 h-full overflow-hidden relative border-r border-border">
          <StickyBoard />
        </main>
        <MiniCalendar />
      </div>
    </TasksProvider>
  );
}

export default App;
