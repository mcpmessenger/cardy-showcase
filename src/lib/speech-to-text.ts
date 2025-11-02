/**
 * Speech-to-Text service using OpenAI Whisper API
 * Handles audio recording and transcription
 */

interface SpeechToTextOptions {
  apiKey: string;
  language?: string;
  model?: string;
}

export class SpeechToTextService {
  private apiKey: string;
  private language: string;
  private model: string;
  private mediaRecorder: MediaRecorder | null = null;
  private audioChunks: Blob[] = [];

  constructor(options: SpeechToTextOptions) {
    this.apiKey = options.apiKey;
    this.language = options.language || 'en';
    this.model = options.model || 'whisper-1';
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
   * Transcribe audio using OpenAI Whisper API
   */
  async transcribe(audioBlob: Blob): Promise<string> {
    try {
      // Convert audio blob to the format OpenAI expects
      const formData = new FormData();
      formData.append('file', audioBlob, 'audio.webm');
      formData.append('model', this.model);
      if (this.language) {
        formData.append('language', this.language);
      }

      const response = await fetch('https://api.openai.com/v1/audio/transcriptions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error?.message || `API error: ${response.status}`);
      }

      const data = await response.json();
      return data.text.trim();
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
 * Create a singleton instance (will be initialized with API key from env)
 */
export function createSpeechToTextService(apiKey: string): SpeechToTextService {
  return new SpeechToTextService({ apiKey });
}

