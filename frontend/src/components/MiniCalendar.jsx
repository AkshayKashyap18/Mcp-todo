import React, { useState } from 'react';
import { format, startOfMonth, endOfMonth, eachDayOfInterval, isSameMonth, isSameDay, addMonths, subMonths } from 'date-fns';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useTasks } from "@/contexts/TasksContext";

export function MiniCalendar() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(new Date());
  const { tasks } = useTasks();

  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(currentDate);
  const days = eachDayOfInterval({ start: monthStart, end: monthEnd });

  const startParam = startOfMonth(currentDate).getDay(); 
  const paddingDays = Array.from({ length: startParam === 0 ? 6 : startParam - 1 }); 

  const selectedDateTasks = tasks.filter(t => t.due_date && isSameDay(new Date(t.due_date), selectedDate))
                                 .sort((a,b) => new Date(a.due_date) - new Date(b.due_date));

  return (
    <div className="w-80 border-l border-border bg-card h-full flex flex-col p-4 shrink-0 transition-all duration-300">
      <div className="flex items-center justify-between mb-4">
        <h2 className="font-semibold text-sm">
            {format(currentDate, 'MMMM yyyy')}
        </h2>
        <div className="flex gap-1">
             <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => setCurrentDate(subMonths(currentDate, 1))}>
                <ChevronLeft className="w-3 h-3" />
             </Button>
             <Button variant="ghost" size="icon" className="h-6 w-6" onClick={() => setCurrentDate(addMonths(currentDate, 1))}>
                <ChevronRight className="w-3 h-3" />
             </Button>
        </div>
      </div>

      <div className="grid grid-cols-7 gap-1 text-center text-xs mb-2 text-muted-foreground">
        {['M','T','W','T','F','S','S'].map(d => <div key={d}>{d}</div>)}
      </div>

      <div className="grid grid-cols-7 gap-1">
         {paddingDays.map((_, i) => <div key={`pad-${i}`} />)}

         {days.map(day => {
             const dayTasks = tasks.filter(t => t.due_date && isSameDay(new Date(t.due_date), day));
             const hasTasks = dayTasks.length > 0;
             const isSelected = isSameDay(day, selectedDate);
             const isToday = isSameDay(day, new Date());

             return (
                 <div 
                    key={day.toString()} 
                    onClick={() => setSelectedDate(day)}
                    className={cn(
                        "aspect-square flex items-center justify-center text-xs rounded-md relative group cursor-pointer transition-colors",
                        isSelected ? "bg-primary text-primary-foreground font-bold shadow-md scale-105 z-10" : "hover:bg-secondary",
                        !isSelected && isToday && "text-primary font-bold border border-primary/50",
                        !isSelected && !isToday && !isSameMonth(day, currentDate) && "text-muted-foreground opacity-50"
                    )}
                 >
                    {format(day, 'd')}
                    {hasTasks && !isSelected && (
                        <div className="absolute bottom-1 left-1/2 -translate-x-1/2 flex gap-0.5">
                            {dayTasks.slice(0,3).map(t => (
                                <div key={t.id} className={cn(
                                    "w-1 h-1 rounded-full",
                                    t.priority === 'high' ? "bg-rose-500" : "bg-blue-500"
                                )} />
                            ))}
                        </div>
                    )}
                 </div>
             )
         })}
      </div>

      {/* Selected Day Agenda */}
      <div className="mt-6 flex-1 flex flex-col min-h-0 border-t border-border pt-4">
         <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold">
                {isSameDay(selectedDate, new Date()) ? "Today, " : ""}{format(selectedDate, 'MMM do')}
            </h3>
            <span className="text-xs text-muted-foreground">{selectedDateTasks.length} tasks</span>
         </div>
         
         <div className="space-y-2 overflow-y-auto pr-2 scrollbar-hide flex-1">
            {selectedDateTasks.length > 0 ? (
                selectedDateTasks.map(task => (
                    <div key={task.id} className="text-xs p-3 rounded-lg border bg-secondary/30 flex flex-col gap-1 transition-all hover:bg-secondary/50 group">
                        <div className="flex items-start justify-between gap-2">
                            <span className={cn("font-medium break-words leading-tight", task.status === 'completed' && "line-through opacity-50")}>
                                {task.title}
                            </span>
                            <div className={cn("w-1.5 h-1.5 rounded-full mt-1 shrink-0", 
                                task.priority === 'high' ? "bg-rose-500" : task.priority === 'medium' ? "bg-yellow-500" : "bg-emerald-500"
                            )} />
                        </div>
                        <span className="text-muted-foreground">{format(new Date(task.due_date), 'h:mm a')}</span>
                    </div>
                ))
            ) : (
                <div className="text-center py-8 text-muted-foreground opacity-60">
                    <p className="text-sm">No tasks scheduled</p>
                    <p className="text-xs">Enjoy your free time!</p>
                </div>
            )}
         </div>
      </div>
    </div>
  );
}
