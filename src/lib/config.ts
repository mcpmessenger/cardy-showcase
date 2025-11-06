const DEFAULT_API_BASE_URL = 'https://tubbyai-production.eba-pcqnhqe4.us-east-1.elasticbeanstalk.com';

function normalizeBaseUrl(url: string): string {
  return url.endsWith('/') ? url.slice(0, -1) : url;
}

export const API_BASE_URL = normalizeBaseUrl(
  import.meta.env.VITE_API_BASE_URL?.trim() || DEFAULT_API_BASE_URL,
);


