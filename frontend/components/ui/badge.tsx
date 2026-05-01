"use client";

import * as React from "react";
import { cn } from "@/lib/utils";

export interface BadgeProps extends React.HTMLAttributes<HTMLSpanElement> {
  variant?: "default" | "secondary" | "success" | "warning" | "destructive";
}

const variantClasses: Record<NonNullable<BadgeProps["variant"]>, string> = {
  default: "bg-primary/10 text-primary border-primary/30",
  secondary: "bg-muted text-muted-foreground border-border",
  success: "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 border-emerald-500/30",
  warning: "bg-amber-500/10 text-amber-600 dark:text-amber-400 border-amber-500/30",
  destructive: "bg-destructive/10 text-destructive border-destructive/30",
};

export function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-medium uppercase tracking-wide",
        variantClasses[variant],
        className,
      )}
      {...props}
    />
  );
}
