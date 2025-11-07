const DEFAULT_API_BASE_URL = 'https://3rouiqfd1f.execute-api.us-east-1.amazonaws.com';

function normalizeBaseUrl(url: string): string {
  return url.endsWith('/') ? url.slice(0, -1) : url;
}

export const API_BASE_URL = normalizeBaseUrl(
  import.meta.env.VITE_API_BASE_URL?.trim() || DEFAULT_API_BASE_URL,
);



