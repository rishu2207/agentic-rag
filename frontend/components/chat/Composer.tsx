"use client";

import { KeyboardEvent, useRef, useState } from "react";
import { ArrowUp, Loader2, Sliders } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export interface ComposerSettings {
  topK: number;
  useHybrid: boolean;
}

interface ComposerProps {
  disabled?: boolean;
  onSubmit: (input: string, settings: ComposerSettings) => void;
  settings: ComposerSettings;
  onSettingsChange: (next: ComposerSettings) => void;
}

export function Composer({
  disabled,
  onSubmit,
  settings,
  onSettingsChange,
}: ComposerProps) {
  const [value, setValue] = useState("");
  const [showSettings, setShowSettings] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  function handleSubmit() {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSubmit(trimmed, settings);
    setValue("");
    textareaRef.current?.focus();
  }

  function handleKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }

  return (
    <div className="mx-auto w-full max-w-4xl px-4 pb-6 md:px-8">
      <div
        className={cn(
          "relative flex flex-col gap-2 rounded-2xl border border-border bg-card/80 p-2 shadow-lg shadow-primary/5 backdrop-blur transition-colors",
          "focus-within:border-primary/40",
        )}
      >
        {showSettings && (
          <div className="flex flex-wrap items-center gap-4 border-b border-border/70 px-3 py-3 text-xs text-muted-foreground">
            <label className="flex items-center gap-2">
              <span className="font-medium text-foreground">top-k</span>
              <input
                type="range"
                min={1}
                max={10}
                value={settings.topK}
                onChange={(e) =>
                  onSettingsChange({
                    ...settings,
                    topK: Number(e.target.value),
                  })
                }
                className="h-1 w-32 cursor-pointer appearance-none rounded-full bg-muted accent-primary"
              />
              <Badge variant="secondary">{settings.topK}</Badge>
            </label>
            <label className="flex cursor-pointer items-center gap-2">
              <input
                type="checkbox"
                checked={settings.useHybrid}
                onChange={(e) =>
                  onSettingsChange({
                    ...settings,
                    useHybrid: e.target.checked,
                  })
                }
                className="h-3.5 w-3.5 cursor-pointer accent-primary"
              />
              <span className="font-medium text-foreground">hybrid search</span>
              <span className="text-muted-foreground">
                (BM25 + dense vectors via RRF)
              </span>
            </label>
          </div>
        )}
        <Textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          rows={2}
          placeholder="Ask about an ArXiv paper, a concept, or a recent AI result…"
          className="max-h-40 min-h-[56px] resize-none border-0 bg-transparent px-3 text-sm shadow-none focus-visible:ring-0"
        />
        <div className="flex items-center justify-between px-2 pb-1">
          <div className="flex items-center gap-2">
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => setShowSettings((v) => !v)}
              className="gap-1.5"
            >
              <Sliders className="h-3.5 w-3.5" />
              <span className="text-xs">Settings</span>
            </Button>
            <span className="hidden text-[11px] text-muted-foreground sm:inline">
              ⏎ to send · ⇧⏎ for newline
            </span>
          </div>
          <Button
            type="button"
            size="icon"
            disabled={disabled || value.trim().length === 0}
            onClick={handleSubmit}
            aria-label="Send message"
          >
            {disabled ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <ArrowUp className="h-4 w-4" />
            )}
          </Button>
        </div>
      </div>
      <p className="mt-3 text-center text-[11px] text-muted-foreground">
        Retrieval-augmented answers over ArXiv cs.AI papers — the agent runs a
        guardrail, hybrid retrieval, document grading, optional query rewriting,
        and grounded generation.
      </p>
    </div>
  );
}
