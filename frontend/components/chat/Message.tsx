"use client";

import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Bot, ThumbsDown, ThumbsUp, User } from "lucide-react";
import type { ChatMessage } from "@/lib/api";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { SourceCard } from "./SourceCard";
import { ReasoningTrace } from "./ReasoningTrace";

interface MessageProps {
  message: ChatMessage;
  onFeedback?: (score: 1 | -1) => void;
  feedbackGiven?: 1 | -1 | null;
}

export function MessageBubble({
  message,
  onFeedback,
  feedbackGiven,
}: MessageProps) {
  const isUser = message.role === "user";
  const isError = Boolean(message.error);

  return (
    <div
      className={cn(
        "group flex w-full animate-fade-in gap-3 px-4 py-6 md:px-8",
        isUser ? "bg-background" : "bg-muted/30",
      )}
    >
      <div
        className={cn(
          "flex h-8 w-8 flex-none items-center justify-center rounded-full border border-border text-xs font-semibold",
          isUser
            ? "bg-primary text-primary-foreground"
            : "bg-background text-primary",
        )}
      >
        {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
      </div>

      <div className="min-w-0 flex-1 space-y-3">
        <div className="flex items-center gap-2 text-xs text-muted-foreground">
          <span className="font-medium text-foreground">
            {isUser ? "You" : "Agentic RAG"}
          </span>
          {!isUser && message.searchMode && (
            <Badge variant="secondary">{message.searchMode}</Badge>
          )}
          {!isUser && message.chunksUsed != null && message.chunksUsed > 0 && (
            <Badge variant="secondary">
              {message.chunksUsed} chunk{message.chunksUsed === 1 ? "" : "s"}
            </Badge>
          )}
          {isError && <Badge variant="destructive">error</Badge>}
        </div>

        {isError ? (
          <p className="text-sm text-destructive">{message.error}</p>
        ) : (
          <div className="prose-chat max-w-none">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content || (isUser ? "" : "…")}
            </ReactMarkdown>
          </div>
        )}

        {!isUser && message.sources && message.sources.length > 0 && (
          <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
            {message.sources.slice(0, 6).map((src, i) => (
              <SourceCard key={`${message.id}-src-${i}`} source={src} index={i} />
            ))}
          </div>
        )}

        {!isUser &&
          message.reasoningSteps &&
          message.reasoningSteps.length > 0 && (
            <ReasoningTrace
              steps={message.reasoningSteps}
              retrievalAttempts={message.chunksUsed}
            />
          )}

        {!isUser && onFeedback && message.traceId && (
          <div className="flex items-center gap-2 pt-1 opacity-0 transition-opacity group-hover:opacity-100">
            <Button
              variant={feedbackGiven === 1 ? "default" : "ghost"}
              size="icon"
              aria-label="Good response"
              onClick={() => onFeedback(1)}
            >
              <ThumbsUp className="h-4 w-4" />
            </Button>
            <Button
              variant={feedbackGiven === -1 ? "destructive" : "ghost"}
              size="icon"
              aria-label="Bad response"
              onClick={() => onFeedback(-1)}
            >
              <ThumbsDown className="h-4 w-4" />
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}

export function ThinkingBubble() {
  return (
    <div className="flex w-full animate-fade-in gap-3 px-4 py-6 md:px-8 bg-muted/30">
      <div className="flex h-8 w-8 flex-none items-center justify-center rounded-full border border-border bg-background text-primary">
        <Bot className="h-4 w-4" />
      </div>
      <div className="flex items-center gap-2 text-sm text-muted-foreground">
        <span>Thinking</span>
        <span className="flex items-center gap-0.5">
          <span className="h-1.5 w-1.5 animate-pulse-dot rounded-full bg-primary/60" />
          <span
            className="h-1.5 w-1.5 animate-pulse-dot rounded-full bg-primary/60"
            style={{ animationDelay: "0.2s" }}
          />
          <span
            className="h-1.5 w-1.5 animate-pulse-dot rounded-full bg-primary/60"
            style={{ animationDelay: "0.4s" }}
          />
        </span>
      </div>
    </div>
  );
}
