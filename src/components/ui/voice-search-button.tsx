"use client";

import { useState, useEffect, useRef } from "react";
import { Mic, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { createSpeechToTextService, SpeechToTextService } from "@/lib/speech-to-text";
import { toast } from "sonner";

interface VoiceSearchButtonProps {
  onTranscription: (text: string) => void;
  className?: string;
}

export function VoiceSearchButton({ onTranscription, className }: VoiceSearchButtonProps) {
  const [isRecording, setIsRecording] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const speechServiceRef = useRef<SpeechToTextService | null>(null);
  const [recordingTime, setRecordingTime] = useState(0);

  useEffect(() => {
    speechServiceRef.current = createSpeechToTextService();
    return () => {
      speechServiceRef.current = null;
    };
  }, []);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isRecording) {
      interval = setInterval(() => {
        setRecordingTime((prev) => prev + 1);
      }, 1000);
    } else {
      setRecordingTime(0);
    }
    return () => clearInterval(interval);
  }, [isRecording]);

  const handleStartRecording = async () => {
    if (!speechServiceRef.current) {
      toast.error('Voice search is not available right now. Please try again later.');
      return;
    }

    if (!SpeechToTextService.isSupported()) {
      toast.error('Your browser does not support audio recording');
      return;
    }

    try {
      setIsRecording(true);
      await speechServiceRef.current.startRecording();
    } catch (error: any) {
      setIsRecording(false);
      toast.error(error.message || 'Failed to start recording');
    }
  };

  const handleStopRecording = async () => {
    if (!speechServiceRef.current) {
      return;
    }

    try {
      setIsRecording(false);
      setIsProcessing(true);

      const audioBlob = await speechServiceRef.current.stopRecording();
      const transcription = await speechServiceRef.current.transcribe(audioBlob);

      if (transcription) {
        onTranscription(transcription);
        toast.success('Voice search successful!');
      } else {
        toast.error('No speech detected. Please try again.');
      }
    } catch (error: any) {
      console.error('Error in voice search:', error);
      toast.error(error.message || 'Failed to process voice input');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleClick = () => {
    if (isProcessing) return;
    
    if (isRecording) {
      handleStopRecording();
    } else {
      handleStartRecording();
    }
  };

  const formatTime = (seconds: number) => {
    return `${seconds}s`;
  };

  return (
    <div className={`flex items-center gap-2 ${className}`}>
      {isRecording && (
        <span className="text-xs text-muted-foreground">
          {formatTime(recordingTime)}
        </span>
      )}
      <Button
        type="button"
        variant="ghost"
        size="icon"
        onClick={handleClick}
        disabled={isProcessing || !speechServiceRef.current}
        className={`relative ${isRecording ? 'text-red-500 animate-pulse' : ''}`}
      >
        {isProcessing ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <Mic className="h-4 w-4" />
        )}
      </Button>
    </div>
  );
}

