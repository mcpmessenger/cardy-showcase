"use client";

import { Mic } from "lucide-react";
import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";

interface AIVoiceInputProps {
  onStart?: () => void;
  onStop?: (duration: number, audioBlob?: Blob) => void;
  visualizerBars?: number;
  demoMode?: boolean;
  demoInterval?: number;
  className?: string;
}

export function AIVoiceInput({
  onStart,
  onStop,
  visualizerBars = 48,
  demoMode = false,
  demoInterval = 3000,
  className
}: AIVoiceInputProps) {
  const [submitted, setSubmitted] = useState(false);
  const [time, setTime] = useState(0);
  const [isClient, setIsClient] = useState(false);
  const [isDemo, setIsDemo] = useState(demoMode);
  const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
  const [audioChunks, setAudioChunks] = useState<Blob[]>([]);

  useEffect(() => {
    setIsClient(true);
    
    // Check microphone availability on mount
    if (typeof window !== 'undefined') {
      const checkMicrophone = async () => {
        // Check if we're on a secure context (HTTPS or localhost or private IP)
        const isPrivateIP = (hostname: string) => {
          // Check for localhost variants
          if (hostname === 'localhost' || hostname === '127.0.0.1') return true;
          // Check for private IP ranges (10.x.x.x, 172.16.x.x-172.31.x.x, 192.168.x.x)
          const parts = hostname.split('.').map(Number);
          if (parts.length === 4 && parts.every(p => !isNaN(p))) {
            const [a, b, c, d] = parts;
            if (a === 10) return true; // 10.0.0.0/8
            if (a === 172 && b >= 16 && b <= 31) return true; // 172.16.0.0/12
            if (a === 192 && b === 168) return true; // 192.168.0.0/16
            if (a === 127) return true; // 127.0.0.0/8 (loopback)
          }
          return false;
        };
        
        const isSecureContext = window.isSecureContext || 
          location.protocol === 'https:' || 
          isPrivateIP(location.hostname);
        
        if (!isSecureContext) {
          console.warn('Page is not in a secure context. Microphone requires HTTPS or localhost.');
        }
        
        // Check for mediaDevices API
        if (!navigator.mediaDevices) {
          console.warn('navigator.mediaDevices is not available');
          
          // Try legacy API as fallback
          if (navigator.getUserMedia) {
            console.info('Legacy getUserMedia API available');
          } else {
            console.error('No microphone API available');
          }
        } else if (!navigator.mediaDevices.getUserMedia) {
          console.warn('getUserMedia not available on mediaDevices');
        } else {
          console.info('Microphone API is available');
        }
      };
      
      checkMicrophone();
    }
  }, []);

  useEffect(() => {
    let intervalId: NodeJS.Timeout;

    if (submitted) {
      onStart?.();
      intervalId = setInterval(() => {
        setTime((t) => t + 1);
      }, 1000);
    } else {
      // Stop recording and create blob
      if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
      }
      setTime(0);
    }

    return () => clearInterval(intervalId);
  }, [submitted, time, onStart, onStop, mediaRecorder]);

  // Handle recording setup
  useEffect(() => {
    if (!submitted) return;

    let recorder: MediaRecorder;
    const chunks: Blob[] = [];

    const startRecording = async () => {
      try {
        // Check secure context (allow private IPs)
        const isPrivateIP = (hostname: string) => {
          if (hostname === 'localhost' || hostname === '127.0.0.1') return true;
          const parts = hostname.split('.').map(Number);
          if (parts.length === 4 && parts.every(p => !isNaN(p))) {
            const [a, b] = parts;
            if (a === 10) return true; // 10.0.0.0/8
            if (a === 172 && b >= 16 && b <= 31) return true; // 172.16.0.0/12
            if (a === 192 && b === 168) return true; // 192.168.0.0/16
            if (a === 127) return true; // 127.0.0.0/8
          }
          return false;
        };
        
        const isSecureContext = window.isSecureContext || 
          location.protocol === 'https:' || 
          isPrivateIP(location.hostname);
        
        if (!isSecureContext) {
          throw new Error(
            'Page must be served over HTTPS, localhost, or private IP. ' +
            `Current URL: ${location.protocol}//${location.hostname}. ` +
            'Try using http://localhost:8080 instead.'
          );
        }
        
        // Try modern API first
        let getUserMedia: (constraints: MediaStreamConstraints) => Promise<MediaStream>;
        
        if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
          getUserMedia = navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);
        } else if (navigator.getUserMedia) {
          // Legacy API fallback
          getUserMedia = (constraints: MediaStreamConstraints) => {
            return new Promise((resolve, reject) => {
              navigator.getUserMedia(constraints, resolve, reject);
            });
          };
        } else {
          throw new Error(
            'Microphone API not available. ' +
            'Please use a modern browser (Chrome, Firefox, Edge) and ensure you are on HTTPS or localhost.'
          );
        }

        const stream = await getUserMedia({ audio: true });
        recorder = new MediaRecorder(stream);
        setMediaRecorder(recorder);

        recorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            chunks.push(event.data);
          }
        };

        recorder.onstop = () => {
          const audioBlob = new Blob(chunks, { type: 'audio/webm' });
          setAudioChunks([]);
          
          // Check audio blob size - warn if suspiciously small
          if (audioBlob.size < 1000) { // Less than 1KB
            console.warn('Audio blob is very small:', audioBlob.size, 'bytes. Recording may be too short.');
          }
          
          recorder.stream.getTracks().forEach(track => track.stop());
          onStop?.(time, audioBlob);
        };

        // Start recording with small timeslice to capture more data
        recorder.start(100); // Capture data every 100ms
      } catch (error) {
        console.error('Error starting recording:', error);
        const errorMsg = error instanceof Error 
          ? error.message 
          : 'Failed to access microphone. Please check browser permissions.';
        alert(`Microphone Error: ${errorMsg}`);
        setSubmitted(false);
      }
    };

    startRecording();

    return () => {
      if (recorder && recorder.state !== 'inactive') {
        recorder.stop();
      }
    };
  }, [submitted]);

  useEffect(() => {
    if (!isDemo) return;

    let timeoutId: NodeJS.Timeout;

    const runAnimation = () => {
      setSubmitted(true);
      timeoutId = setTimeout(() => {
        setSubmitted(false);
        timeoutId = setTimeout(runAnimation, 1000);
      }, demoInterval);
    };

    const initialTimeout = setTimeout(runAnimation, 100);

    return () => {
      clearTimeout(timeoutId);
      clearTimeout(initialTimeout);
    };
  }, [isDemo, demoInterval]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  const handleClick = () => {
    if (isDemo) {
      setIsDemo(false);
      setSubmitted(false);
    } else {
      setSubmitted((prev) => !prev);
    }
  };

  return (
    <div className={cn("w-full py-4", className)}>
      <div className="relative max-w-xl w-full mx-auto flex items-center flex-col gap-2">
        <button
          className={cn(
            "group w-16 h-16 rounded-xl flex items-center justify-center transition-colors",
            submitted
              ? "bg-none"
              : "bg-none hover:bg-black/10 dark:hover:bg-white/10"
          )}
          type="button"
          onClick={handleClick}
        >
          {submitted ? (
            <div
              className="w-6 h-6 rounded-sm animate-spin bg-black dark:bg-white cursor-pointer pointer-events-auto"
              style={{ animationDuration: "3s" }}
            />
          ) : (
            <Mic className="w-6 h-6 text-black/70 dark:text-white/70" />
          )}
        </button>

        <span
          className={cn(
            "font-mono text-sm transition-opacity duration-300",
            submitted
              ? "text-black/70 dark:text-white/70"
              : "text-black/30 dark:text-white/30"
          )}
        >
          {formatTime(time)}
        </span>

        <div className="h-4 w-64 flex items-center justify-center gap-0.5">
          {[...Array(visualizerBars)].map((_, i) => (
            <div
              key={i}
              className={cn(
                "w-0.5 rounded-full transition-all duration-300",
                submitted
                  ? "bg-black/50 dark:bg-white/50 animate-pulse"
                  : "bg-black/10 dark:text-white/10 h-1"
              )}
              style={
                submitted && isClient
                  ? {
                      height: `${20 + Math.random() * 80}%`,
                      animationDelay: `${i * 0.05}s`,
                    }
                  : undefined
              }
            />
          ))}
        </div>

        <p className="h-4 text-xs text-black/70 dark:text-white/70">
          {submitted ? "Listening..." : "Click to speak"}
        </p>
      </div>
    </div>
  );
}

