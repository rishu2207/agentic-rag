"use client";

import type { ReactNode } from "react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { MessageBubble, ThinkingBubble } from "./Message";
import { Composer, type ComposerSettings } from "./Composer";
import { Header } from "./Header";
import {
  makeId,
  type AskResponse,
  type ChatMessage,
  type ReasoningStep,
} from "@/lib/api";
import { Sparkles, BookOpen, FlaskConical, Workflow } from "lucide-react";

const SAMPLE_PROMPTS: { title: string; prompt: string; icon: ReactNode }[] = [
  {
    title: "Retrieval-augmented generation",
    prompt:
      "What is retrieval-augmented generation and when is it a better choice than fine-tuning?",
    icon: <BookOpen className="h-4 w-4" />,
  },
  {
    title: "Hybrid search internals",
    prompt:
      "How does reciprocal rank fusion combine BM25 and dense-vector scores, and what are its limits?",
    icon: <Workflow className="h-4 w-4" />,
  },
  {
    title: "Latest agentic RAG trends",
    prompt:
      "Summarise recent research on self-correcting or agentic RAG workflows and cite the papers.",
    icon: <FlaskConical className="h-4 w-4" />,
  },
  {
    title: "Evaluation methodology",
    prompt:
      "What are the standard ways to evaluate retrieval quality and faithfulness of a RAG system?",
    icon: <Sparkles className="h-4 w-4" />,
  },
];

export function Chat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [pending, setPending] = useState(false);
  const [feedback, setFeedback] = useState<Record<string, 1 | -1>>({});
  const [settings, setSettings] = useState<ComposerSettings>({
    topK: 5,
    useHybrid: true,
  });
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, pending]);

  const submit = useCallback(
    async (input: string, s: ComposerSettings) => {
      const userMsg: ChatMessage = {
        id: makeId("u"),
        role: "user",
        content: input,
        createdAt: Date.now(),
      };
      setMessages((prev) => [...prev, userMsg]);
      setPending(true);

      try {
        const res = await fetch("/api/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            query: input,
            top_k: s.topK,
            use_hybrid: s.useHybrid,
          }),
        });
        const data = (await res.json()) as AskResponse & {
          error?: string;
          detail?: string;
        };

        if (!res.ok || data.error) {
          setMessages((prev) => [
            ...prev,
            {
              id: makeId("e"),
              role: "assistant",
              content: "",
              createdAt: Date.now(),
              error:
                data.error ??
                data.detail ??
                `Request failed with status ${res.status}`,
            },
          ]);
          return;
        }

        const reasoning: ReasoningStep[] = Array.isArray(data.reasoning_steps)
          ? (data.reasoning_steps as ReasoningStep[])
          : [];

        setMessages((prev) => [
          ...prev,
          {
            id: makeId("a"),
            role: "assistant",
            content: data.answer ?? "",
            createdAt: Date.now(),
            sources: data.sources ?? [],
            chunksUsed: data.chunks_used,
            searchMode: data.search_mode,
            traceId: data.trace_id ?? null,
            reasoningSteps: reasoning,
          },
        ]);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Unknown error";
        setMessages((prev) => [
          ...prev,
          {
            id: makeId("e"),
            role: "assistant",
            content: "",
            createdAt: Date.now(),
            error: `Network error: ${message}`,
          },
        ]);
      } finally {
        setPending(false);
      }
    },
    [],
  );

  const sendFeedback = useCallback(
    async (messageId: string, traceId: string, score: 1 | -1) => {
      setFeedback((prev) => ({ ...prev, [messageId]: score }));
      try {
        await fetch("/api/feedback", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ trace_id: traceId, score }),
        });
      } catch {
        // swallow — UI already reflects the choice
      }
    },
    [],
  );

  const empty = messages.length === 0 && !pending;

  const content = useMemo(() => {
    if (empty) {
      return (
        <div className="mx-auto flex max-w-3xl flex-1 flex-col items-center justify-center px-6 py-20 text-center">
          <div className="mb-6 flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 text-primary">
            <Sparkles className="h-7 w-7" />
          </div>
          <h1 className="text-3xl font-semibold tracking-tight">
            Ask the ArXiv research agent
          </h1>
          <p className="mt-3 max-w-xl text-sm text-muted-foreground">
            Grounded answers over a hybrid (BM25 + dense vector) index of
            ArXiv cs.AI papers, with a LangGraph agent that validates the
            query, grades retrieved documents, and rewrites when evidence is
            weak.
          </p>
          <div className="mt-10 grid w-full gap-3 sm:grid-cols-2">
            {SAMPLE_PROMPTS.map((p) => (
              <button
                key={p.title}
                type="button"
                onClick={() => submit(p.prompt, settings)}
                className="group flex items-start gap-3 rounded-xl border border-border bg-card/60 p-4 text-left transition-all hover:-translate-y-0.5 hover:border-primary/40 hover:bg-card"
              >
                <span className="mt-0.5 flex h-8 w-8 items-center justify-center rounded-lg bg-primary/10 text-primary">
                  {p.icon}
                </span>
                <span>
                  <span className="block text-sm font-medium">{p.title}</span>
                  <span className="mt-1 block text-xs text-muted-foreground">
                    {p.prompt}
                  </span>
                </span>
              </button>
            ))}
          </div>
        </div>
      );
    }

    return (
      <div className="mx-auto w-full max-w-4xl flex-1">
        {messages.map((m) => (
          <MessageBubble
            key={m.id}
            message={m}
            feedbackGiven={feedback[m.id] ?? null}
            onFeedback={
              m.traceId
                ? (score) => sendFeedback(m.id, m.traceId as string, score)
                : undefined
            }
          />
        ))}
        {pending && <ThinkingBubble />}
        <div ref={bottomRef} />
      </div>
    );
  }, [empty, messages, pending, settings, submit, feedback, sendFeedback]);

  return (
    <div className="flex min-h-screen flex-col">
      <Header />
      <main className="flex flex-1 flex-col overflow-hidden">
        <div className="flex-1 overflow-y-auto pb-4">{content}</div>
        <Composer
          disabled={pending}
          onSubmit={submit}
          settings={settings}
          onSettingsChange={setSettings}
        />
      </main>
    </div>
  );
}
