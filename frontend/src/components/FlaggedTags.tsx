"use client";

import { useState } from "react";
import { ChevronDown, ChevronRight, AlertTriangle } from "lucide-react";
import { cn } from "@/lib/utils";
import type { FlaggedTag as FlaggedTagType } from "@/lib/types";

function formatLabel(s: string): string {
  return s
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(" ");
}

interface FlaggedTagsProps {
  flagged: FlaggedTagType[];
  className?: string;
}

export function FlaggedTags({ flagged, className }: FlaggedTagsProps) {
  const [open, setOpen] = useState(true);
  if (flagged.length === 0) return null;

  return (
    <div className={cn("rounded-lg border border-amber-500/40 bg-amber-500/5", className)}>
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="flex w-full items-center gap-2 px-4 py-3 text-left font-medium text-amber-800 dark:text-amber-200"
      >
        {open ? (
          <ChevronDown className="h-4 w-4" />
        ) : (
          <ChevronRight className="h-4 w-4" />
        )}
        <AlertTriangle className="h-4 w-4" />
        <span>{flagged.length} tag(s) need review</span>
      </button>
      {open && (
        <ul className="border-t border-amber-500/20 px-4 py-3">
          {flagged.map((f, i) => (
            <li
              key={`${f.category}-${f.value}-${i}`}
              className="flex flex-wrap items-center gap-2 text-sm text-muted-foreground"
            >
              <span className="font-medium text-foreground">{formatLabel(f.category)}</span>
              <span className="text-amber-700 dark:text-amber-300">→</span>
              <span>{formatLabel(f.value)}</span>
              <span className="rounded bg-muted px-1.5 py-0.5 text-xs">
                {Math.round(f.confidence * 100)}%
              </span>
              <span className="text-xs italic">{f.reason.replace("_", " ")}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
