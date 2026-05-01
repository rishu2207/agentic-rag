"use client";

import type { SourceItem } from "@/lib/api";
import { truncate } from "@/lib/utils";
import { ExternalLink, Sparkles } from "lucide-react";
import { Badge } from "@/components/ui/badge";

interface SourceCardProps {
  source: SourceItem;
  index: number;
}

export function SourceCard({ source, index }: SourceCardProps) {
  const title = source.title ?? source.arxiv_id ?? `Source ${index + 1}`;
  const authors =
    Array.isArray(source.authors) && source.authors.length > 0
      ? source.authors.slice(0, 3).join(", ") +
        (source.authors.length > 3 ? ", et al." : "")
      : null;

  const href =
    source.pdf_url ??
    (source.arxiv_id
      ? `https://arxiv.org/abs/${source.arxiv_id.split("v")[0]}`
      : null);

  return (
    <a
      href={href ?? "#"}
      target={href ? "_blank" : undefined}
      rel={href ? "noreferrer" : undefined}
      className="group flex h-full flex-col justify-between rounded-lg border border-border bg-card/60 p-3 text-left transition-all hover:border-primary/40 hover:bg-card"
    >
      <div className="space-y-1.5">
        <div className="flex items-center gap-2">
          <Badge variant="secondary" className="font-mono">
            [{index + 1}]
          </Badge>
          {source.score != null && (
            <Badge variant="default">
              <Sparkles className="h-3 w-3" />
              {source.score.toFixed(3)}
            </Badge>
          )}
        </div>
        <h4 className="line-clamp-2 text-sm font-medium leading-snug text-foreground">
          {truncate(title, 160)}
        </h4>
        {authors && (
          <p className="line-clamp-1 text-xs text-muted-foreground">
            {authors}
          </p>
        )}
        {source.section_name && (
          <p className="text-[10px] uppercase tracking-wide text-muted-foreground">
            § {source.section_name}
          </p>
        )}
      </div>
      {href && (
        <div className="mt-3 flex items-center gap-1 text-[11px] font-medium text-primary opacity-0 transition-opacity group-hover:opacity-100">
          Open paper <ExternalLink className="h-3 w-3" />
        </div>
      )}
    </a>
  );
}
