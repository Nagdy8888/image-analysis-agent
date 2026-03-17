"use client";

import { useState, useRef, useEffect } from "react";
import { ImageUploader } from "@/components/ImageUploader";
import { ProcessingOverlay } from "@/components/ProcessingOverlay";
import { VisionResults } from "@/components/VisionResults";
import { TagCategories } from "@/components/TagCategories";
import { FlaggedTags } from "@/components/FlaggedTags";
import { JsonViewer } from "@/components/JsonViewer";
import { Button } from "@/components/ui/button";
import { API_BASE_URL } from "@/lib/constants";
import type { AnalyzeImageResponse } from "@/lib/types";

const MAX_STEP = 6;

export default function Home() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const [analysisResult, setAnalysisResult] = useState<AnalyzeImageResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const stepTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (!isProcessing) return;
    stepTimerRef.current = setInterval(() => {
      setCurrentStep((s) => (s < MAX_STEP - 1 ? s + 1 : s));
    }, 3500);
    return () => {
      if (stepTimerRef.current) clearInterval(stepTimerRef.current);
    };
  }, [isProcessing]);

  async function handleAnalyze(file: File) {
    setError(null);
    setIsProcessing(true);
    setCurrentStep(1);

    const formData = new FormData();
    formData.append("file", file);
    setCurrentStep(2);

    try {
      const res = await fetch(`${API_BASE_URL}/api/analyze-image`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(err.detail || "Analysis failed");
      }

      const data: AnalyzeImageResponse = await res.json();
      setCurrentStep(MAX_STEP);
      await new Promise((r) => setTimeout(r, 500));
      setAnalysisResult(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setIsProcessing(false);
    }
  }

  function handleReset() {
    setAnalysisResult(null);
    setError(null);
    setCurrentStep(1);
  }

  return (
    <main className="container flex min-h-[calc(100vh-3.5rem)] flex-col py-8">
      <div className="mx-auto w-full max-w-3xl space-y-8">
        <div className="text-center">
          <h1 className="text-3xl font-semibold tracking-tight">Image Analysis Agent</h1>
          <p className="mt-2 text-muted-foreground">
            Upload an image to analyze and tag with AI.
          </p>
        </div>

        <ImageUploader onAnalyze={handleAnalyze} disabled={isProcessing} />

        {error && (
          <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-sm text-destructive">
            {error}
          </div>
        )}

        {analysisResult && (
          <div className="space-y-6">
            <VisionResults data={analysisResult} />
            {analysisResult.tags_by_category && Object.keys(analysisResult.tags_by_category).length > 0 && (
              <TagCategories tagsByCategory={analysisResult.tags_by_category} />
            )}
            {analysisResult.flagged_tags && analysisResult.flagged_tags.length > 0 && (
              <FlaggedTags flagged={analysisResult.flagged_tags} />
            )}
            <JsonViewer
              data={
                analysisResult.tag_record ?? analysisResult.vision_raw_tags
              }
            />
            <Button variant="outline" onClick={handleReset}>
              Analyze New Image
            </Button>
          </div>
        )}
      </div>

      <ProcessingOverlay isVisible={isProcessing} currentStep={currentStep} />
    </main>
  );
}
