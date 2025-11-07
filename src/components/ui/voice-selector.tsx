"use client";

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { AVAILABLE_VOICES, type Voice, DEFAULT_VOICE_ID } from "@/lib/voices";
import { Settings } from "lucide-react";

interface VoiceSelectorProps {
  selectedVoiceId: string;
  onVoiceChange: (voiceId: string) => void;
  className?: string;
}

export function VoiceSelector({ selectedVoiceId, onVoiceChange, className }: VoiceSelectorProps) {
  const selectedVoice = AVAILABLE_VOICES.find(v => v.id === selectedVoiceId) || AVAILABLE_VOICES[0];
  
  return (
    <div className={`flex items-center gap-2 ${className || ''}`}>
      <Settings className="w-4 h-4 text-muted-foreground" />
      <Select value={selectedVoiceId} onValueChange={onVoiceChange}>
        <SelectTrigger className="w-[220px]">
          <SelectValue>
            <span className="font-medium">{selectedVoice.name}</span>
          </SelectValue>
        </SelectTrigger>
        <SelectContent>
          {AVAILABLE_VOICES.map((voice) => (
            <SelectItem key={voice.id} value={voice.id}>
              <div className="flex flex-col py-1">
                <span className="font-medium">{voice.name}</span>
                <span className="text-xs text-muted-foreground">{voice.description}</span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
    </div>
  );
}

