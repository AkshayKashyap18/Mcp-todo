import React, { useState } from 'react';
import { useTasks } from "@/contexts/TasksContext";
import { format } from 'date-fns';
import { cn } from "@/lib/utils";
import { Pin, Calendar as CalendarIcon, Tag, Trash2, CheckCircle2, RotateCcw, CheckCircle, Flame } from 'lucide-react';
import { Button } from "@/components/ui/button";
import confetti from 'canvas-confetti';

const StickyNote = ({ task, isCompletedView }) => {
  const { deleteTask, updateTask } = useTasks();
  const [description, setDescription] = useState(task.description || "");
  const [isEditing, setIsEditing] = useState(false);

  const isHighPriority = task.priority === 'high';
  const category = (task.category || "").toLowerCase();

  // Varied rotation for "sticky" feel
  const rotation = isCompletedView ? 0 : Math.random() * 2 - 1; 
  
  // Theme logic
  let themeClass = "";
  if (isCompletedView) {
      themeClass = "bg-muted/50 text-muted-foreground border-border opacity-75";
  } else if (isHighPriority) {
      themeClass = "bg-rose-50 text-rose-950 border-rose-500 dark:bg-rose-900/20 dark:text-rose-100 ring-4 ring-rose-500/10 paper-grain";
  } else if (category === 'work') {
      themeClass = "paper-graph bg-slate-50 text-slate-900 border-slate-200 dark:bg-slate-900/30 dark:text-slate-100 dark:border-slate-800 paper-grain";
  } else {
      // Default / Personal = Yellow Lined
      themeClass = "paper-lined paper-margin bg-yellow-50 text-yellow-950 border-yellow-200 dark:bg-yellow-900/20 dark:text-yellow-100 paper-grain";
  }

  const handleBlur = () => {
      setIsEditing(false);
      if (description !== task.description) {
          updateTask(task.id, { description });
      }
  };

  const toggleStatus = (e) => {
      if (task.status !== 'completed') {
          const rect = e.target.getBoundingClientRect();
          confetti({
              particleCount: 100,
              spread: 70,
              origin: {
                  x: rect.x / window.innerWidth,
                  y: rect.y / window.innerHeight
              }
          });
      }
      
      const newStatus = task.status === 'completed' ? 'pending' : 'completed';
      updateTask(task.id, { status: newStatus });
  };

  const togglePriority = (e) => {
      e.stopPropagation();
      const newPriority = isHighPriority ? 'medium' : 'high';
      updateTask(task.id, { priority: newPriority });
  };

  return (
    <div 
        className={cn(
            "p-6 rounded-sm shadow-sm border relative group transition-all hover:scale-105 hover:shadow-md hover:z-10 aspect-square flex flex-col overflow-hidden", 
            themeClass
        )}
        style={{ transform: `rotate(${rotation}deg)` }}
    >
        {/* High Priority Hanging Ribbon */}
        <div 
            className={cn(
                "absolute top-0 right-4 w-8 h-12 z-20 cursor-pointer shadow-sm transition-all duration-300 origin-top flex items-center justify-center pt-2",
                isHighPriority 
                    ? "bg-rose-500 translate-y-0" 
                    : "bg-slate-300/50 -translate-y-8 group-hover:translate-y-0"
            )}
            style={{ clipPath: 'polygon(0 0, 100% 0, 100% 100%, 50% 80%, 0% 100%)' }}
            onClick={togglePriority}
            title={isHighPriority ? "Remove High Priority" : "Mark as High Priority"}
        >
            <Flame className={cn("w-4 h-4 text-white transition-opacity", isHighPriority ? "opacity-100" : "opacity-50")} />
        </div>

        {/* Action Buttons - Moved to Top Left for visibility and to avoid ribbon/tag overlap */}
        <div className="absolute top-2 left-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1 z-30">
             <button 
                onClick={toggleStatus}
                className="p-1.5 rounded-full bg-white/20 hover:bg-white/40 text-muted-foreground hover:text-primary transition-colors shadow-sm backdrop-blur-[2px]"
                title={isCompletedView ? "Restore" : "Complete"}
             >
                {isCompletedView ? <RotateCcw className="w-3.5 h-3.5" /> : <CheckCircle2 className="w-3.5 h-3.5" />}
             </button>
             <button 
                onClick={(e) => { e.stopPropagation(); deleteTask(task.id); }}
                className="p-1.5 rounded-full bg-white/20 hover:bg-white/40 text-muted-foreground hover:text-destructive transition-colors shadow-sm backdrop-blur-[2px]"
                title="Delete"
             >
                <Trash2 className="w-3.5 h-3.5" />
             </button>
        </div>
        
        {isCompletedView ? (
             <CheckCircle className="w-12 h-12 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-primary opacity-10 pointer-events-none" />
        ) : (
             <Pin className="w-4 h-4 absolute -top-2 left-1/2 -translate-x-1/2 text-muted-foreground/50 opacity-0 group-hover:opacity-100 transition-opacity" />
        )}
        
        <div className="flex-1 overflow-y-auto scrollbar-hide relative z-10 pt-4"> 
             <h3 className={cn("font-bold text-lg leading-tight mb-2 font-handwriting pr-8", isCompletedView && "line-through opacity-70")}>
                {task.title}
             </h3>
             
             {isEditing && !isCompletedView ? (
                 <textarea
                    className="w-full bg-transparent border-none outline-none resize-none text-sm font-handwriting h-full"
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    onBlur={handleBlur}
                    autoFocus
                 />
             ) : (
                 <p 
                    className={cn("text-sm opacity-80 whitespace-pre-wrap min-h-[50px]", !isCompletedView && "cursor-text")}
                    onClick={() => !isCompletedView && setIsEditing(true)}
                 >
                    {description || (!isCompletedView && <span className="opacity-50 italic cursor-text">Click to add description...</span>)}
                 </p>
             )}
        </div>

        <div className="mt-4 pt-4 border-t border-black/5 dark:border-white/5 flex items-center justify-between text-xs opacity-60 relative z-10">
            <div className="flex items-center gap-1">
                <CalendarIcon className="w-3 h-3" />
                <span>{task.due_date ? format(new Date(task.due_date), 'MMM d') : 'No date'}</span>
            </div>
            
            {task.category && (
                <div className="flex items-center gap-1 uppercase tracking-wider font-semibold opacity-70">
                    <Tag className="w-3 h-3" />
                    <span>{task.category}</span>
                </div>
            )}
        </div>
    </div>
  );
};

export function StickyBoard() {
  const { tasks } = useTasks();
  const [showCompleted, setShowCompleted] = useState(false);

  // Sorting Logic: High priority first, then by date created (newer first)
  const sortTasks = (taskList) => {
      return [...taskList].sort((a, b) => {
          if (a.priority === 'high' && b.priority !== 'high') return -1;
          if (a.priority !== 'high' && b.priority === 'high') return 1;
          return new Date(b.created_at) - new Date(a.created_at);
      });
  };

  const activeTasks = sortTasks(tasks.filter(t => t.status !== 'completed'));
  const completedTasks = sortTasks(tasks.filter(t => t.status === 'completed'));
  
  const displayTasks = showCompleted ? completedTasks : activeTasks;

  return (
    <div className="flex flex-col h-full bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] bg-fixed">
        <div className="sticky top-0 z-10 bg-background/50 backdrop-blur-sm border-b border-black/5">
            {/* View Toggle */}
            <div className="p-4 flex justify-center gap-2">
                <Button 
                    variant={!showCompleted ? "secondary" : "ghost"}
                    onClick={() => setShowCompleted(false)}
                    className="w-32"
                >
                    Active ({activeTasks.length})
                </Button>
                <Button 
                    variant={showCompleted ? "secondary" : "ghost"}
                    onClick={() => setShowCompleted(true)}
                    className="w-32"
                >
                    Completed ({completedTasks.length})
                </Button>
            </div>
        </div>

        <div className="p-8 overflow-y-auto flex-1">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {displayTasks.map(task => (
                    <StickyNote 
                        key={task.id} 
                        task={task} 
                        isCompletedView={showCompleted} 
                    />
                ))}
                
                {/* Empty States */}
                {displayTasks.length === 0 && (
                    <div className="col-span-full flex flex-col items-center justify-center h-96 text-muted-foreground">
                        {showCompleted ? (
                            <>
                                <CheckCircle className="w-12 h-12 mb-4 opacity-20" />
                                <p className="text-xl">No completed tasks yet</p>
                            </>
                        ) : (
                            <>
                                <p className="text-xl">No tasks...</p>
                                <p className="text-sm">Create a task to get started!</p>
                            </>
                        )}
                    </div>
                )}
            </div>
        </div>
    </div>
  );
}
