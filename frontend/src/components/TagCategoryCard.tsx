"use client";

import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { ConfidenceRing } from "@/components/ConfidenceRing";
import type { PartialTagResult } from "@/lib/types";
import { cn } from "@/lib/utils";

/** Color for left border by category (matches filter design). */
const CATEGORY_BORDER_COLORS: Record<string, string> = {
  season: "border-l-amber-500",
  theme: "border-l-violet-500",
  objects: "border-l-emerald-500",
  dominant_colors: "border-l-rose-500",
  design_elements: "border-l-sky-500",
  occasion: "border-l-orange-500",
  mood: "border-l-pink-500",
  product_type: "border-l-cyan-500",
};

function formatTagLabel(value: string): string {
  return value
    .split("_")
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
    .join(" ");
}

interface TagCategoryCardProps {
  result: PartialTagResult;
  className?: string;
}

export function TagCategoryCard({ result, className }: TagCategoryCardProps) {
  const { category, tags, confidence_scores } = result;
  const borderClass =
    CATEGORY_BORDER_COLORS[category] ?? "border-l-muted-foreground/50";
  const title =
    category === "dominant_colors"
      ? "Dominant Colors"
      : formatTagLabel(category);

  return (
    <Card
      className={cn(
        "border-l-4",
        borderClass,
        className
      )}
    >
      <CardHeader className="pb-2">
        <h3 className="text-sm font-semibold uppercase tracking-wide text-muted-foreground">
          {title}
        </h3>
      </CardHeader>
      <CardContent className="pt-0">
        {tags.length === 0 ? (
          <p className="text-sm text-muted-foreground">No tags</p>
        ) : (
          <ul className="flex flex-wrap items-center gap-3">
            {tags.map((tag) => (
              <li
                key={tag}
                className="flex items-center gap-2 rounded-md bg-muted/60 px-2 py-1.5"
              >
                <ConfidenceRing
                  confidence={confidence_scores[tag] ?? 0}
                  size={24}
                  strokeWidth={2}
                />
                <span className="text-sm font-medium">
                  {formatTagLabel(tag)}
                </span>
              </li>
            ))}
          </ul>
        )}
      </CardContent>
    </Card>
  );
}
