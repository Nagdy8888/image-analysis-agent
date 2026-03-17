/** Single category output from a tagger node (e.g. season). */
export interface PartialTagResult {
  category: string;
  tags: string[];
  confidence_scores: Record<string, number>;
}

export interface AnalyzeImageResponse {
  image_url: string;
  image_id: string;
  vision_description: string;
  vision_raw_tags: Record<string, unknown>;
  /** Pipeline tagger results (e.g. season). */
  partial_tags?: PartialTagResult[];
}
