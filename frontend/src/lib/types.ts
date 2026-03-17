export interface AnalyzeImageResponse {
  image_url: string;
  image_id: string;
  vision_description: string;
  vision_raw_tags: Record<string, unknown>;
}
