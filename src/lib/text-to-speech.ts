/**
 * Text-to-Speech service using backend TTS endpoint
 */

import { API_BASE_URL } from "@/lib/config";

interface TextToSpeechOptions {
  voiceId?: string;
}

export class TextToSpeechService {
  private voiceId?: string;

  constructor(options?: TextToSpeechOptions) {
    this.voiceId = options?.voiceId;
  }

  /**
   * Set voice ID
   */
  setVoiceId(voiceId: string): void {
    this.voiceId = voiceId;
  }

  /**
   * Get current voice ID
   */
  getVoiceId(): string | undefined {
    return this.voiceId;
  }

  /**
   * Synthesize text into speech using backend TTS endpoint
   */
  async synthesize(text: string): Promise<string> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/tts/synthesize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text,
          voice_id: this.voiceId,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `TTS API error: ${response.status}`);
      }

      const data = await response.json();
      
      // Return audio URL if provided, otherwise we'll need to handle base64 audio_data
      if (data.audio_url) {
        return data.audio_url;
      } else if (data.audio_data) {
        // Convert base64 to blob URL
        const audioBlob = this.base64ToBlob(data.audio_data, 'audio/mpeg');
        return URL.createObjectURL(audioBlob);
      } else {
        throw new Error('No audio data returned from TTS service');
      }
    } catch (error) {
      console.error('Error synthesizing speech:', error);
      throw error;
    }
  }

  /**
   * Play audio from URL or blob
   */
  async playAudio(audioUrl: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const audio = new Audio(audioUrl);
      audio.onended = () => resolve();
      audio.onerror = (error) => reject(error);
      audio.play().catch(reject);
    });
  }

  /**
   * Synthesize and play in one call
   */
  async synthesizeAndPlay(text: string): Promise<void> {
    const audioUrl = await this.synthesize(text);
    await this.playAudio(audioUrl);
  }

  /**
   * Convert base64 string to Blob
   */
  private base64ToBlob(base64: string, mimeType: string): Blob {
    const byteCharacters = atob(base64);
    const byteNumbers = new Array(byteCharacters.length);
    for (let i = 0; i < byteCharacters.length; i++) {
      byteNumbers[i] = byteCharacters.charCodeAt(i);
    }
    const byteArray = new Uint8Array(byteNumbers);
    return new Blob([byteArray], { type: mimeType });
  }

  /**
   * Check if browser supports audio playback
   */
  static isSupported(): boolean {
    return typeof Audio !== 'undefined';
  }
}

/**
 * Create a singleton instance
 */
export function createTextToSpeechService(voiceId?: string): TextToSpeechService {
  return new TextToSpeechService({ voiceId });
}

