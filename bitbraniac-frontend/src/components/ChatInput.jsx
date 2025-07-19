import React, { useState } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { cn } from '@/lib/utils';

export const ChatInput = ({ onSendMessage, disabled = false, placeholder = "Type your message..." }) => {
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (message.trim() && !isLoading && !disabled) {
      setIsLoading(true);
      await onSendMessage(message.trim());
      setMessage('');
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2 p-4 bg-background border-t border-border">
      <div className="flex-1 relative">
        <Textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={isLoading || disabled}
          className={cn(
            "min-h-[60px] max-h-[200px] resize-none pr-12",
            "focus:ring-2 focus:ring-primary focus:border-primary",
            "placeholder:text-muted-foreground"
          )}
          rows={2}
        />
        <Button
          type="submit"
          size="sm"
          disabled={!message.trim() || isLoading || disabled}
          className={cn(
            "absolute right-2 bottom-2 h-8 w-8 p-0",
            "hover:bg-primary/90 focus:ring-2 focus:ring-primary focus:ring-offset-2"
          )}
        >
          {isLoading ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <Send size={16} />
          )}
        </Button>
      </div>
    </form>
  );
};

