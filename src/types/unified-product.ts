/**
 * Unified Product Master List Schema
 * This schema is designed to serve both the website and Alexa skill
 */
export interface UnifiedProduct {
  product_id: string;
  name: string;
  short_name?: string;
  description: string;
  voice_description?: string;
  price: number;
  currency: string;
  affiliate_url: string;
  image_url: string;
  category: string;
  is_available: boolean;
  rating?: number;
  reviews?: number;
  subcategory?: string;
  badge?: string;
  local_images?: string[];
  local_videos?: string[];
  image_count?: number;
  video_count?: number;
}

