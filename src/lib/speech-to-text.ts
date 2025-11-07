/**
 * Speech-to-Text service using backend STT endpoint (MCP-STT/Whisper)
 * Handles audio recording and transcription
 */

import { API_BASE_URL } from "@/lib/config";

interface SpeechToTextOptions {
  language?: string;
}

export class SpeechToTextService {
  private language: string;
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];

  constructor(options?: SpeechToTextOptions) {
    this.language = options?.language || 'en';
  }

  /**
   * Start recording audio from user's microphone
   */
  async startRecording(): Promise<void> {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      this.mediaRecorder = new MediaRecorder(stream);

      this.audioChunks = [];
      
      this.mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          this.audioChunks.push(event.data);
        }
      };

      this.mediaRecorder.start();
    } catch (error) {
      console.error('Error starting recording:', error);
      throw new Error('Failed to start audio recording. Please check microphone permissions.');
    }
  }

  /**
   * Stop recording and return audio blob
   */
  async stopRecording(): Promise<Blob> {
    return new Promise((resolve, reject) => {
      if (!this.mediaRecorder) {
        reject(new Error('No active recording'));
        return;
      }

      this.mediaRecorder.onstop = () => {
        const audioBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
        this.mediaRecorder?.stream.getTracks().forEach(track => track.stop());
        resolve(audioBlob);
      };

      this.mediaRecorder.onerror = (error) => {
        reject(error);
      };

      this.mediaRecorder.stop();
    });
  }

  /**
   * Transcribe audio using backend STT endpoint
   */
  async transcribe(audioBlob: Blob): Promise<string> {
    try {
      const formData = new FormData();
      formData.append('audio_file', audioBlob, 'audio.webm');

      const response = await fetch(`${API_BASE_URL}/api/stt/transcribe`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `STT API error: ${response.status}`);
      }

      const data = await response.json();
      const transcript = data.text.trim();
      
      // Validate transcript - warn if it's suspiciously short
      if (transcript.length === 0) {
        throw new Error('No transcription received. Please try speaking again.');
      }
      
      // Check if transcript is just punctuation (likely error)
      if (transcript.length === 1 && /[.,!?;:]/.test(transcript)) {
        console.warn('Transcription may be incorrect - received only punctuation:', transcript);
        throw new Error('Transcription failed - detected only punctuation. Please speak more clearly and try again.');
      }
      
      return transcript;
    } catch (error) {
      console.error('Error transcribing audio:', error);
      throw error;
    }
  }

  /**
   * Record and transcribe in one call
   */
  async recordAndTranscribe(onProgress?: (progress: string) => void): Promise<string> {
    try {
      onProgress?.('Starting recording...');
      await this.startRecording();

      onProgress?.('Recording...');
      await new Promise(resolve => setTimeout(resolve, 1000)); // Record for at least 1 second

      onProgress?.('Stopping recording...');
      const audioBlob = await this.stopRecording();

      onProgress?.('Transcribing...');
      const transcription = await this.transcribe(audioBlob);

      onProgress?.('Done!');
      return transcription;
    } catch (error) {
      onProgress?.('Error occurred');
      throw error;
    }
  }

  /**
   * Check if browser supports audio recording
   */
  static isSupported(): boolean {
    return !!(
      navigator.mediaDevices &&
      navigator.mediaDevices.getUserMedia &&
      window.MediaRecorder
    );
  }
}

/**
 * Create a singleton instance
 */
export function createSpeechToTextService(options?: SpeechToTextOptions): SpeechToTextService {
  return new SpeechToTextService(options);
}

