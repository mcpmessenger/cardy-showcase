/**
 * Available voice options for TTS
 */

export interface Voice {
  id: string;
  name: string;
  description: string;
  gender?: 'male' | 'female' | 'neutral';
  language?: string;
  elevenLabsVoiceId?: string; // Eleven Labs voice ID for direct API calls
}

export const AVAILABLE_VOICES: Voice[] = [
  {
    id: 'default',
    name: 'Default Voice',
    description: 'Default tubbyAI voice',
    gender: 'neutral',
    language: 'en-US',
    elevenLabsVoiceId: '21m00Tcm4TlvDq8ikWAM' // Default Eleven Labs voice
  },
  {
    id: 'rachel',
    name: 'Rachel',
    description: 'Warm, friendly female voice',
    gender: 'female',
    language: 'en-US',
    elevenLabsVoiceId: '21m00Tcm4TlvDq8ikWAM' // Rachel
  },
  {
    id: 'domi',
    name: 'Domi',
    description: 'Strong, confident female voice',
    gender: 'female',
    language: 'en-US',
    elevenLabsVoiceId: 'AZnzlk1XvdvUeBnXmlld' // Domi
  },
  {
    id: 'bella',
    name: 'Bella',
    description: 'Soft, calming female voice',
    gender: 'female',
    language: 'en-US',
    elevenLabsVoiceId: 'EXAVITQu4vr4xnSDxMaL' // Bella
  },
  {
    id: 'antoni',
    name: 'Antoni',
    description: 'Clear, professional male voice',
    gender: 'male',
    language: 'en-US',
    elevenLabsVoiceId: 'ErXwobaYiN019lkyVLvD' // Antoni
  },
  {
    id: 'elli',
    name: 'Elli',
    description: 'Young, energetic female voice',
    gender: 'female',
    language: 'en-US',
    elevenLabsVoiceId: 'MF3mGyEYCl7XYWbV9V6O' // Elli
  },
  {
    id: 'josh',
    name: 'Josh',
    description: 'Deep, authoritative male voice',
    gender: 'male',
    language: 'en-US',
    elevenLabsVoiceId: 'TxGEqnHWrfWFTfGW9XjX' // Josh
  },
  {
    id: 'arnold',
    name: 'Arnold',
    description: 'Bold, commanding male voice',
    gender: 'male',
    language: 'en-US',
    elevenLabsVoiceId: 'VR6AewLTigWG4xSOukaG' // Arnold
  },
  {
    id: 'adam',
    name: 'Adam',
    description: 'Friendly, conversational male voice',
    gender: 'male',
    language: 'en-US',
    elevenLabsVoiceId: 'pNInz6obpgDQGcFmaJgB' // Adam
  },
  {
    id: 'sam',
    name: 'Sam',
    description: 'Casual, approachable male voice',
    gender: 'male',
    language: 'en-US',
    elevenLabsVoiceId: 'yoZ06aMxZJJ28mfd3POQ' // Sam
  }
];

export const DEFAULT_VOICE_ID = 'rachel';

/**
 * Get voice by ID
 */
export function getVoiceById(id: string): Voice | undefined {
  return AVAILABLE_VOICES.find(voice => voice.id === id);
}

/**
 * Get default voice
 */
export function getDefaultVoice(): Voice {
  return AVAILABLE_VOICES.find(v => v.id === DEFAULT_VOICE_ID) || AVAILABLE_VOICES[0];
}

/**
 * Get Eleven Labs voice ID for a voice name
 */
export function getElevenLabsVoiceId(voiceId: string): string | undefined {
  const voice = getVoiceById(voiceId);
  return voice?.elevenLabsVoiceId;
}

