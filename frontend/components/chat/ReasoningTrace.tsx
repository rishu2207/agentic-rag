"use client";

import { useState } from "react";
import { ChevronDown, Workflow } from "lucide-react";
import { cn } from "@/lib/utils";
import type { ReasoningStep } from "@/lib/api";

interface ReasoningTraceProps {
  steps: ReasoningStep[];
  retrievalAttempts?: number;
}

export function ReasoningTrace({
  steps,
  retrievalAttempts,
}: ReasoningTraceProps) {
  const [open, setOpen] = useState(false);
  if (!steps || steps.length === 0) return null;

  return (
    <div className="mt-3 rounded-lg border border-dashed border-border bg-background/50">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between gap-2 px-3 py-2 text-xs font-medium text-muted-foreground transition-colors hover:text-foreground"
      >
        <span className="flex items-center gap-2">
          <Workflow className="h-3.5 w-3.5" />
          Agent reasoning
          <span className="rounded-full bg-muted px-1.5 py-0.5 text-[10px]">
            {steps.length} steps
          </span>
          {retrievalAttempts != null && retrievalAttempts > 0 && (
            <span className="rounded-full bg-muted px-1.5 py-0.5 text-[10px]">
              {retrievalAttempts} retrieval{retrievalAttempts === 1 ? "" : "s"}
            </span>
          )}
        </span>
        <ChevronDown
          className={cn(
            "h-3.5 w-3.5 transition-transform",
            open && "rotate-180",
          )}
        />
      </button>
      {open && (
        <ol className="divide-y divide-border border-t border-border">
          {steps.map((step, i) => (
            <li
              key={`${step.node}-${i}`}
              className="grid grid-cols-[auto,1fr] gap-3 px-3 py-2 text-xs"
            >
              <span className="mt-0.5 font-mono text-[10px] text-muted-foreground">
                {String(i + 1).padStart(2, "0")}
              </span>
              <div>
                <div className="font-mono text-[11px] font-medium uppercase tracking-wide text-primary">
                  {step.node}
                </div>
                {step.summary && (
                  <p className="text-muted-foreground">{step.summary}</p>
                )}
                {step.output && (
                  <pre className="mt-1 whitespace-pre-wrap break-words rounded bg-muted p-2 text-[10px] text-muted-foreground">
                    {step.output}
                  </pre>
                )}
              </div>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
