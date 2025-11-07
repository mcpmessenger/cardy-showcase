/**
 * Chat service for communicating with backend chat endpoint
 */

import { API_BASE_URL } from "@/lib/config";

export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp?: Date;
  products?: any[];  // Product data when products are found
}

export interface ChatResponse {
  text: string;
  conversation_id?: string;
  tools_used?: string[];
  products?: any[];  // Product data when products are found
}

/**
 * Send a chat message to the backend
 */
export async function sendChatMessage(
  message: string,
  conversationId?: string,
  history?: ChatMessage[]
): Promise<ChatResponse> {
  try {
    // Convert history format if provided
    const historyPayload = history?.map(msg => ({
      role: msg.role,
      content: msg.content,
    }));

    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        conversation_id: conversationId,
        history: historyPayload,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || `Chat API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error sending chat message:', error);
    throw error;
  }
}

/**
 * Search products directly (for testing/debugging)
 */
export async function searchProducts(
  query: string,
  maxPrice?: number,
  category?: string
): Promise<{ products: any[]; count: number }> {
  try {
    const params = new URLSearchParams({ query });
    if (maxPrice) params.append('max_price', maxPrice.toString());
    if (category) params.append('category', category);

    const response = await fetch(`${API_BASE_URL}/api/products/search?${params}`);

    if (!response.ok) {
      throw new Error(`Product search error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Error searching products:', error);
    throw error;
  }
}

