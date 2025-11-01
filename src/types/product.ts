export interface Product {
  name: string;
  price: number;
  asin: string;
  url: string;
  image_url: string;
  rating: number;
  reviews: number;
  description: string;
  category: string;
  subcategory: string;
  badge?: string;
  local_images?: string[];
  local_videos?: string[];
  image_count?: number;
  video_count?: number;
}

