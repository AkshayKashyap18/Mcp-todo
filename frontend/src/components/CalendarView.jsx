import { useState, useEffect } from 'react';
import { format, addDays, startOfWeek, addWeeks, subWeeks, isSameDay } from 'date-fns';
import { ChevronLeft, ChevronRight, Calendar as CalendarIcon, Clock } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { useTasks } from "@/contexts/TasksContext";
import { cn } from "@/lib/utils";

const TimeGrid = ({ tasks }) => {
  const hours = Array.from({ length: 24 }, (_, i) => i); // Full 24 hours

  return (
    <div className="flex-1 relative mt-4 overflow-y-auto">
      {hours.map(hour => (
        <div key={hour} className="flex relative h-20 group">
          <div className="w-16 pr-4 text-xs text-muted-foreground text-right pt-2 font-medium">
            {hour === 0 ? '12 AM' : hour === 12 ? '12 PM' : hour > 12 ? `${hour - 12} PM` : `${hour} AM`}
          </div>
          <div className="flex-1 border-t border-border group-last:border-b relative">
            {/* Render Tasks for this hour */}
            {tasks.map(task => {
                const taskDate = task.due_date ? new Date(task.due_date) : null;
                if (!taskDate) return null;

                const taskHour = taskDate.getHours();
                if (taskHour !== hour) return null;

                // Simple positioning
                const dayIndex = (taskDate.getDay() + 6) % 7; // Shift Sun(0) to 6, Mon(1) to 0
                
                return (
                    <div 
                        key={task.id}
                        style={{ 
                            left: `${(dayIndex / 7) * 100}%`,
                            width: `${100 / 7}%`
                        }}
                        className={cn(
                            "absolute top-1 bottom-1 rounded-md p-2 text-xs shadow-sm cursor-pointer border transition-all hover:scale-[1.01] overflow-hidden group/task",
                            task.priority === 'high' 
                                ? "bg-rose-500/10 border-rose-500/20 text-rose-200" 
                                : task.priority === 'medium'
                                    ? "bg-purple-500/10 border-purple-500/20 text-purple-200"
                                    : "bg-emerald-500/10 border-emerald-500/20 text-emerald-200"
                        )}
                    >
                        <span className={cn(
                            "font-semibold block truncate",
                             task.priority === 'high' ? "text-rose-100" : task.priority === 'medium' ? "text-purple-100" : "text-emerald-100"
                        )}>
                            {task.title}
                        </span>
                        <div className="flex items-center gap-2 opacity-80 text-[10px]">
                            {format(taskDate, 'h:mm a')}
                        </div>
                    </div>
                );
            })}

            {/* Current Time Indicator */}
            {hour === new Date().getHours() && (
               <div 
                 className="absolute w-full h-0.5 bg-red-500 z-10 flex items-center pointer-events-none"
                 style={{ top: `${(new Date().getMinutes() / 60) * 100}%` }}
               >
                 <div className="w-2 h-2 bg-red-500 rounded-full -ml-1"></div>
               </div>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export function CalendarView() {
  const [currentDate, setCurrentDate] = useState(new Date());
  const { tasks, loading } = useTasks();

  const weekStart = startOfWeek(currentDate, { weekStartsOn: 1 });
  const weekDays = Array.from({ length: 7 }, (_, i) => addDays(weekStart, i));
  const weekEnd = addDays(weekDays[6], 1); // Start of next week (exclusive upper bound)

  // Filter tasks for the visible week and only those with due dates
  const visibleTasks = tasks.filter(task => {
    if (!task.due_date) return false;
    const taskDate = new Date(task.due_date);
    // Be generous with the bounds to match the displayed days
    return taskDate >= weekDays[0] && taskDate <= addDays(weekDays[6], 1); 
  });

  return (
    <div className="flex flex-col h-full bg-background">
      {/* Calendar Header */}
      <div className="flex items-center justify-between px-8 py-6 border-b border-border/50">
        <div className="flex items-center gap-6">
          <div className="flex items-baseline gap-2">
            <h2 className="text-3xl font-bold tracking-tight">
                {format(currentDate, 'MMMM')}
            </h2>
            <span className="text-3xl font-light text-muted-foreground">
                {format(currentDate, 'yyyy')}
            </span>
            <span className="ml-2 text-sm font-medium text-muted-foreground bg-secondary px-2 py-0.5 rounded-full">
                W{format(currentDate, 'w')}
            </span>
          </div>
          
          <div className="flex items-center gap-1">
            <Button 
                variant="ghost" 
                size="icon" 
                onClick={() => setCurrentDate(subWeeks(currentDate, 1))}
            >
              <ChevronLeft className="w-5 h-5" />
            </Button>
            <Button 
                variant="ghost" 
                size="icon"
                onClick={() => setCurrentDate(addWeeks(currentDate, 1))}
            >
              <ChevronRight className="w-5 h-5" />
            </Button>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Button variant="outline" className="h-9" onClick={() => setCurrentDate(new Date())}>
            Today
          </Button>
          <Button className="h-9 bg-primary text-primary-foreground hover:bg-primary/90 shadow-lg shadow-primary/20">
            Share
          </Button>
        </div>
      </div>

      {/* Days Header */}
      <div className="flex pl-16 pr-4 py-4 border-b border-border/50">
        {weekDays.map((date, i) => {
            const isToday = isSameDay(date, new Date());
            return (
                <div key={i} className="flex-1 flex flex-col items-center">
                    <span className={cn(
                        "text-xs font-semibold uppercase tracking-wider mb-1",
                        isToday ? "text-primary" : "text-muted-foreground"
                    )}>
                        {format(date, 'EEE')}
                    </span>
                    <div className={cn(
                        "w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all",
                        isToday 
                            ? "bg-primary text-primary-foreground shadow-md shadow-primary/30 scale-110" 
                            : "text-foreground hover:bg-secondary"
                    )}>
                        {format(date, 'd')}
                    </div>
                </div>
            )
        })}
      </div>

      {/* Time Grid with Tasks */}
      <TimeGrid tasks={visibleTasks} />
    </div>
  );
}
