import { AIVoiceInput } from "@/components/ui/ai-voice-input";
import { useState } from "react";

export function AIVoiceInputDemo() {
  const [recordings, setRecordings] = useState<{ duration: number; timestamp: Date }[]>([]);

  const handleStop = (duration: number) => {
    setRecordings(prev => [...prev.slice(-4), { duration, timestamp: new Date() }]);
  };

  return (
    <div className="space-y-8">
      <div className="space-y-4">
        <h2 className="text-2xl font-bold">AI Voice Input Demo</h2>
        <p className="text-muted-foreground">
          This is a standalone demo of the voice input component.
        </p>
        
        <AIVoiceInput 
          onStart={() => console.log('Recording started')}
          onStop={handleStop}
        />
        
        {recordings.length > 0 && (
          <div className="space-y-2">
            <h3 className="font-semibold">Recent Recordings:</h3>
            {recordings.map((rec, idx) => (
              <div key={idx} className="text-sm text-muted-foreground">
                {rec.timestamp.toLocaleTimeString()} - {rec.duration}s
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

