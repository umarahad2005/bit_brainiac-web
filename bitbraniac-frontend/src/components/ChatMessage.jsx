import React from 'react';
import { Bot, User } from 'lucide-react';
import { cn } from '@/lib/utils';

export const ChatMessage = ({ type, content, timestamp }) => {
  const isBot = type === 'assistant';
  
  return (
    <div className={cn(
      "flex gap-3 p-4 rounded-lg mb-4 max-w-4xl",
      isBot 
        ? "bg-muted/50 border border-border" 
        : "bg-primary/5 border border-primary/20 ml-auto"
    )}>
      <div className={cn(
        "w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0",
        isBot 
          ? "bg-primary text-primary-foreground" 
          : "bg-secondary text-secondary-foreground"
      )}>
        {isBot ? <Bot className="w-4 h-4" /> : <User className="w-4 h-4" />}
      </div>
      
      <div className="flex-1 space-y-2">
        <div className="prose prose-sm max-w-none dark:prose-invert">
          {content.split('\n').map((line, index) => (
            <p key={index} className="mb-2 last:mb-0">
              {line}
            </p>
          ))}
        </div>
        
        {timestamp && (
          <div className="text-xs text-muted-foreground">
            {new Date(timestamp).toLocaleTimeString()}
          </div>
        )}
      </div>
    </div>
  );
};

