"use client";

import { useEffect, useState } from "react";
import { Github, Moon, Sun, Activity, Circle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type HealthState = "unknown" | "healthy" | "degraded" | "down";

export function Header() {
  const [theme, setTheme] = useState<"light" | "dark">("dark");
  const [health, setHealth] = useState<HealthState>("unknown");

  useEffect(() => {
    const stored = window.localStorage.getItem("theme");
    const next = (stored as "light" | "dark" | null) ?? "dark";
    setTheme(next);
    document.documentElement.classList.toggle("dark", next === "dark");
  }, []);

  useEffect(() => {
    let cancelled = false;
    async function probe() {
      try {
        const res = await fetch("/api/health", { cache: "no-store" });
        if (cancelled) return;
        if (!res.ok) {
          setHealth("degraded");
          return;
        }
        const json: { status?: string; services?: Record<string, unknown> } =
          await res.json();
        setHealth(json?.status === "healthy" ? "healthy" : "degraded");
      } catch {
        if (!cancelled) setHealth("down");
      }
    }
    probe();
    const t = setInterval(probe, 30_000);
    return () => {
      cancelled = true;
      clearInterval(t);
    };
  }, []);

  function toggleTheme() {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    window.localStorage.setItem("theme", next);
    document.documentElement.classList.toggle("dark", next === "dark");
  }

  const healthLabel: Record<HealthState, string> = {
    unknown: "Connecting…",
    healthy: "All systems nominal",
    degraded: "Degraded",
    down: "Backend unreachable",
  };
  const healthColor: Record<HealthState, string> = {
    unknown: "text-muted-foreground",
    healthy: "text-emerald-500",
    degraded: "text-amber-500",
    down: "text-destructive",
  };

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border/60 bg-background/80 backdrop-blur">
      <div className="mx-auto flex h-14 max-w-6xl items-center justify-between px-4 md:px-6">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
            <Activity className="h-4 w-4" />
          </div>
          <div className="flex flex-col leading-tight">
            <span className="text-sm font-semibold">Agentic RAG Platform</span>
            <span className="text-[11px] text-muted-foreground">
              ArXiv research assistant · LangGraph · OpenSearch · Ollama/OpenAI
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <div
            className={cn(
              "hidden items-center gap-1.5 rounded-full border border-border px-2.5 py-1 text-[11px] font-medium sm:flex",
              healthColor[health],
            )}
            title={healthLabel[health]}
          >
            <Circle className="h-2 w-2 fill-current" />
            {healthLabel[health]}
          </div>
          <Button
            variant="ghost"
            size="icon"
            aria-label="Toggle theme"
            onClick={toggleTheme}
          >
            {theme === "dark" ? (
              <Sun className="h-4 w-4" />
            ) : (
              <Moon className="h-4 w-4" />
            )}
          </Button>
          <Button
            variant="ghost"
            size="icon"
            aria-label="GitHub"
            onClick={() =>
              window.open(
                "https://github.com/jamwithai/production-agentic-rag-course",
                "_blank",
                "noreferrer",
              )
            }
          >
            <Github className="h-4 w-4" />
          </Button>
        </div>
      </div>
    </header>
  );
}
