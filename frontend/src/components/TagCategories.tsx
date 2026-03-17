"use client";

import { useMemo } from "react";
import { TagCategoryCard } from "@/components/TagCategoryCard";
import type { PartialTagResult } from "@/lib/types";

const CATEGORY_ORDER = [
  "season",
  "theme",
  "objects",
  "dominant_colors",
  "design_elements",
  "occasion",
  "mood",
  "product_type",
];

interface TagCategoriesProps {
  /** Category -> list of { value, confidence } */
  tagsByCategory: Record<string, { value: string; confidence: number }[]>;
  className?: string;
}

/** Converts tags_by_category to PartialTagResult[] and renders a grid of TagCategoryCards. */
export function TagCategories({ tagsByCategory, className }: TagCategoriesProps) {
  const results = useMemo(() => {
    return CATEGORY_ORDER.map((category) => {
      const list = tagsByCategory[category] ?? [];
      const tags = list.map((t) => t.value);
      const confidence_scores = Object.fromEntries(list.map((t) => [t.value, t.confidence]));
      return {
        category,
        tags,
        confidence_scores,
      } as PartialTagResult;
    });
  }, [tagsByCategory]);

  return (
    <div className={className}>
      <h2 className="mb-4 text-lg font-semibold">Tags by category</h2>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {results.map((result) => (
          <TagCategoryCard key={result.category} result={result} />
        ))}
      </div>
    </div>
  );
}
