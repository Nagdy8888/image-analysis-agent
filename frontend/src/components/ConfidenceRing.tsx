"use client";

import { cn } from "@/lib/utils";

/** Ring showing confidence 0–1 (e.g. 0.85 = 85% filled). */
interface ConfidenceRingProps {
  confidence: number;
  size?: number;
  strokeWidth?: number;
  className?: string;
}

export function ConfidenceRing({
  confidence,
  size = 32,
  strokeWidth = 3,
  className,
}: ConfidenceRingProps) {
  const clamped = Math.min(1, Math.max(0, confidence));
  const r = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * r;
  const offset = circumference * (1 - clamped);

  return (
    <svg
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      className={cn("shrink-0 -rotate-90", className)}
      aria-label={`Confidence ${Math.round(clamped * 100)}%`}
    >
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        stroke="currentColor"
        strokeWidth={strokeWidth}
        className="text-muted opacity-30"
      />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        stroke="currentColor"
        strokeWidth={strokeWidth}
        strokeDasharray={circumference}
        strokeDashoffset={offset}
        strokeLinecap="round"
        className="text-primary transition-[stroke-dashoffset] duration-500"
      />
    </svg>
  );
}
