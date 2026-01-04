import React, { useState } from 'react';
import { Button } from "@/components/ui/button";
import { format } from 'date-fns';
import { 
  Calendar, 
  CheckSquare, 
  Settings, 
  Menu, 
  Plus, 
  Inbox,
  LayoutGrid,
  Search,
  Book,
  Loader2,
  ChevronLeft
} from 'lucide-react';
import { cn } from "@/lib/utils";

const SidebarItem = ({ icon: Icon, label, active, count }) => (
  <button
    className={cn(
      "w-full flex items-center justify-between px-3 py-2 rounded-lg text-sm transition-colors",
      active 
        ? "bg-secondary text-foreground font-medium" 
        : "text-muted-foreground hover:bg-secondary/50 hover:text-foreground"
    )}
  >
    <div className="flex items-center gap-3">
      <Icon className="w-4 h-4" />
      <span>{label}</span>
    </div>
    {count && (
      <span className="text-xs bg-muted px-1.5 py-0.5 rounded text-muted-foreground">
        {count}
      </span>
    )}
  </button>
);

const SidebarSection = ({ title, children, action }) => (
  <div className="mb-6">
    <div className="flex items-center justify-between px-3 mb-2">
      <h3 className="text-xs font-semibold text-muted-foreground uppercase tracking-wider">
        {title}
      </h3>
      {action && (
        <button className="text-muted-foreground hover:text-foreground">
          <Plus className="w-3 h-3" />
        </button>
      )}
    </div>
    <div className="space-y-0.5">
      {children}
    </div>
  </div>
);

import { useTasks } from "@/contexts/TasksContext";

export function Sidebar({ className }) {
  const [searchValue, setSearchValue] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [messages, setMessages] = useState([]); // Local chat state
  const { smartAdd } = useTasks();

  const handleSmartAdd = async (e) => {
    if (e.key === 'Enter' && !e.shiftKey && searchValue.trim()) {
        e.preventDefault(); // Prevent newline
        const text = searchValue;
        try {
            setMessages(prev => [...prev, { role: 'user', content: text }]);
            setSearchValue("");
            setIsProcessing(true);
            
            const result = await smartAdd(text);
            
            let responseContent = "";
            if (Array.isArray(result)) {
                const count = result.length;
                const titles = result.map(t => `"${t.title}"`).join(", ");
                responseContent = `Created ${count} tasks: ${titles}`;
            } else {
                responseContent = `Created task: "${result.title}" due ${result.due_date ? format(new Date(result.due_date), 'MMM d, h:mm a') : 'someday'}`;
            }

            setMessages(prev => [...prev, { 
                role: 'assistant', 
                content: responseContent
            }]);
        } catch (error) {
            console.error(error);
            setMessages(prev => [...prev, { role: 'assistant', content: "Sorry, I couldn't understand that." }]);
        } finally {
            setIsProcessing(false);
        }
    }
  };

  return (
    <div 
        className={cn(
            "bg-card border-r border-border h-screen flex flex-col transition-all duration-300 ease-in-out relative group/sidebar", 
            isCollapsed ? "w-16" : "w-80",
            className
        )}
    >
      <Button 
        variant="ghost" 
        size="icon" 
        className={cn(
            "absolute -right-3 top-6 h-6 w-6 rounded-full border shadow-md bg-background z-50 opacity-0 group-hover/sidebar:opacity-100 transition-opacity",
            isCollapsed && "opacity-100"
        )}
        onClick={() => setIsCollapsed(!isCollapsed)}
      >
        {isCollapsed ? <Menu className="h-3 w-3" /> : <ChevronLeft className="h-3 w-3" />}
      </Button>

      {/* Header */}
      <div className={cn("p-4 flex items-center gap-2 mb-4 overflow-hidden whitespace-nowrap", isCollapsed && "justify-center px-2")}>
        <div className="w-8 h-8 min-w-[32px] bg-primary rounded-lg flex items-center justify-center">
          <CheckSquare className="w-5 h-5 text-white" />
        </div>
        {!isCollapsed && (
            <span className="font-bold text-lg tracking-tight transition-opacity duration-300">AI Todo</span>
        )}
      </div>

      {/* AI Chat / Smart Add Section */}
      {!isCollapsed ? (
          <div className="px-4 flex-1 flex flex-col transition-opacity duration-300 opacity-100 min-h-0">
              <div className="bg-secondary/30 rounded-xl p-4 flex-1 mb-4 border border-border/50 flex flex-col overflow-hidden">
                 {/* Chat History */}
                 <div className="flex-1 overflow-y-auto space-y-4 mb-2 pr-2 scrollbar-hide">
                    {/* Welcome Message */}
                    <div className="flex gap-3">
                         <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
                             <CheckSquare className="w-4 h-4 text-primary" />
                         </div>
                         <div className="bg-muted p-3 rounded-2xl rounded-tl-sm text-sm">
                             <p>Hi! I'm your AI assistant. Tell me what needs to be done.</p>
                             <p className="opacity-70 text-xs mt-1">Try: "Book flight for Friday at 5pm"</p>
                         </div>
                    </div>

                    {/* User & AI Messages would go here. For now, let's fake a dynamic feel or add real functionality in next step if data provided. 
                        Since I don't have message persistence yet, I'll update it to show the input as a "User Message" after submission via local state. 
                    */}
                 </div>
              </div>
              
              <div className="relative group mb-4 shrink-0">
                {isProcessing ? (
                    <Loader2 className="w-5 h-5 absolute left-4 top-4 text-primary animate-spin" />
                ) : (
                    <Plus className="w-5 h-5 absolute left-4 top-4 text-muted-foreground group-focus-within:text-primary transition-colors" />
                )}
                <textarea 
                    value={searchValue}
                    onChange={(e) => setSearchValue(e.target.value)}
                    onKeyDown={handleSmartAdd}
                    placeholder="Type 'Design meeting at 2pm'..." 
                    className="w-full bg-secondary text-sm rounded-xl pl-12 pr-4 py-4 min-h-[80px] outline-none focus:ring-1 focus:ring-ring placeholder:text-muted-foreground/70 transition-all resize-none"
                />
                <div className="absolute right-3 bottom-3 flex gap-0.5 opacity-50">
                    <kbd className="text-[10px] bg-background/50 px-1 rounded text-muted-foreground">Enter</kbd>
                </div>
            </div>
          </div>
      ) : (
          <div className="flex-1 flex flex-col items-center py-4 gap-4">
                <Button variant="ghost" size="icon" className="h-10 w-10" onClick={() => setIsCollapsed(false)}>
                    <Plus className="w-5 h-5" />
                </Button>
          </div>
      )}
    </div>
  );
}
