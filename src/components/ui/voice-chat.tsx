"use client";

import { useState, useRef, useEffect } from "react";
import { Mic, Send, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { AIVoiceInput } from "./ai-voice-input";
import { VoiceSelector } from "./voice-selector";
import { SpeechToTextService } from "@/lib/speech-to-text";
import { TextToSpeechService } from "@/lib/text-to-speech";
import { sendChatMessage, type ChatMessage } from "@/lib/chat";
import { DEFAULT_VOICE_ID, getElevenLabsVoiceId } from "@/lib/voices";
import { cn } from "@/lib/utils";
import { getProductImageUrl } from "@/lib/image-utils";

interface VoiceChatProps {
  className?: string;
}

export function VoiceChat({ className }: VoiceChatProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [conversationId, setConversationId] = useState<string | undefined>();
  const [textInput, setTextInput] = useState("");
  const [selectedVoiceId, setSelectedVoiceId] = useState<string>(DEFAULT_VOICE_ID);
  
  const sttService = useRef(new SpeechToTextService()).current;
  const ttsService = useRef(new TextToSpeechService({ voiceId: DEFAULT_VOICE_ID })).current;
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const sanitizeAssistantContent = (content: string) => {
    if (!content) return content;

    let sanitized = content;
    sanitized = sanitized.replace(/\[!\[[^\]]*\]\([^\)]+\)\]\([^\)]+\)/g, "");
    sanitized = sanitized.replace(/!\[[^\]]*\]\([^\)]+\)/g, "");
    sanitized = sanitized.replace(/\[([^\]]+)\]\(([^\)]+)\)/g, "$1");
    sanitized = sanitized.replace(/\s{2,}/g, " ");
    return sanitized.trim();
  };

  // Update TTS service when voice changes
  useEffect(() => {
    ttsService.setVoiceId(selectedVoiceId);
  }, [selectedVoiceId, ttsService]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleVoiceInput = async (audioBlob: Blob) => {
    if (isProcessing) return;

    setIsProcessing(true);
    try {
      // 1. Transcribe audio
      let transcript: string;
      try {
        transcript = await sttService.transcribe(audioBlob);
        
        // Validate transcription
        if (!transcript || transcript.trim().length === 0) {
          throw new Error('No transcription received. Please try speaking again.');
        }
        
        // Check for suspiciously short or punctuation-only transcripts
        const trimmed = transcript.trim();
        if (trimmed.length === 1 && /[.,!?;:]/.test(trimmed)) {
          throw new Error('Transcription appears incorrect. Please speak more clearly or try a longer phrase.');
        }
        
        // Log successful transcription
        console.log('✅ Transcribed:', transcript);
      } catch (sttError) {
        console.error('❌ Transcription error:', sttError);
        const errorMessage: ChatMessage = {
          role: 'assistant',
          content: sttError instanceof Error 
            ? `Sorry, I couldn't understand what you said. ${sttError.message}. Please try speaking more clearly or use text input.`
            : 'Sorry, I encountered an error transcribing your voice. Please try again or use text input.',
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, errorMessage]);
        setIsProcessing(false);
        return;
      }
      
      // Add user message with validated transcript
      const userMessage: ChatMessage = {
        role: 'user',
        content: transcript,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, userMessage]);
      
      console.log('📤 Sending to chat:', transcript);

      // 2. Send to chat endpoint
      const response = await sendChatMessage(
        transcript,
        conversationId,
        messages
      );

      // Update conversation ID if provided
      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      // Add assistant message
      const assistantContent = sanitizeAssistantContent(response.text);

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: assistantContent,
        timestamp: new Date(),
        products: response.products,
      };
      setMessages(prev => [...prev, assistantMessage]);

      // 3. Synthesize and play speech
      try {
        // Get Eleven Labs voice ID for selected voice
        const elevenLabsVoiceId = getElevenLabsVoiceId(selectedVoiceId);
        if (elevenLabsVoiceId) {
          ttsService.setVoiceId(elevenLabsVoiceId);
        }
        await ttsService.synthesizeAndPlay(assistantContent);
      } catch (ttsError) {
        console.warn('TTS playback failed:', ttsError);
        // Continue even if TTS fails
      }

    } catch (error) {
      console.error('Voice chat error:', error);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleTextSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!textInput.trim() || isProcessing) return;

    setIsProcessing(true);
    try {
      const userMessage: ChatMessage = {
        role: 'user',
        content: textInput.trim(),
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, userMessage]);
      setTextInput("");

      const response = await sendChatMessage(
        userMessage.content,
        conversationId,
        messages
      );

      if (response.conversation_id) {
        setConversationId(response.conversation_id);
      }

      const assistantContent = sanitizeAssistantContent(response.text);

      const assistantMessage: ChatMessage = {
        role: 'assistant',
        content: assistantContent,
        timestamp: new Date(),
        products: response.products,
      };
      setMessages(prev => [...prev, assistantMessage]);

      // Optional: Also play TTS for text messages
      try {
        // Get Eleven Labs voice ID for selected voice
        const elevenLabsVoiceId = getElevenLabsVoiceId(selectedVoiceId);
        if (elevenLabsVoiceId) {
          ttsService.setVoiceId(elevenLabsVoiceId);
        }
        await ttsService.synthesizeAndPlay(assistantContent);
      } catch (ttsError) {
        console.warn('TTS playback failed:', ttsError);
      }

    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: ChatMessage = {
        role: 'assistant',
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsProcessing(false);
    }
  };

  const formatTime = (date?: Date) => {
    if (!date) return "";
    return new Intl.DateTimeFormat('en-US', {
      hour: 'numeric',
      minute: '2-digit',
    }).format(date);
  };

  return (
    <div className={cn("flex flex-col h-full max-w-4xl mx-auto", className)}>
      {/* Header with Voice Selector */}
      <div className="border-b p-4 flex justify-between items-center">
        <h2 className="text-lg font-semibold">tubbyAI Assistant</h2>
        <VoiceSelector 
          selectedVoiceId={selectedVoiceId} 
          onVoiceChange={setSelectedVoiceId}
        />
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-muted-foreground mt-8">
            <p className="text-lg font-medium">Start a conversation</p>
            <p className="text-sm">Use voice or text to chat with tubbyAI</p>
          </div>
        )}
        
        {messages.map((message, index) => (
          <div
            key={index}
            className={cn(
              "flex",
              message.role === 'user' ? "justify-end" : "justify-start"
            )}
          >
            <div
              className={cn(
                "max-w-[80%] rounded-lg px-4 py-2",
                message.role === 'user'
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted"
              )}
            >
              <p className="text-sm whitespace-pre-wrap">{message.content}</p>
              
              {/* Display product images if available */}
              {message.products && message.products.length > 0 && (
                <div className="mt-3 space-y-2">
                  {message.products.map((product, idx) => {
                    const productLink =
                      product.affiliate_url ||
                      product.product_url ||
                      product.external_url ||
                      product.url ||
                      product.link ||
                      '#';

                    return (
                      <a
                        key={product.product_id || idx}
                        href={productLink}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex gap-3 items-start border rounded-lg p-2 bg-background transition-colors hover:bg-muted"
                        onClick={(event) => {
                          if (productLink === '#') {
                            event.preventDefault();
                          }
                        }}
                      >
                      <img
                        src={getProductImageUrl(product)}
                        alt={product.name || product.short_name || 'Product'}
                        className="w-20 h-20 object-cover rounded"
                        onError={(e) => {
                          (e.target as HTMLImageElement).src = '/placeholder.png';
                        }}
                      />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium truncate underline-offset-2 group-hover:underline">
                          {product.name || product.short_name || 'View product'}
                        </p>
                        <p className="text-xs text-muted-foreground">${product.price?.toFixed(2)}</p>
                        {product.rating && (
                          <p className="text-xs text-muted-foreground">
                            ⭐ {product.rating} ({product.reviews} reviews)
                          </p>
                        )}
                      </div>
                      </a>
                    );
                  })}
                </div>
              )}
              
              {message.timestamp && (
                <p className="text-xs opacity-70 mt-1">
                  {formatTime(message.timestamp)}
                </p>
              )}
            </div>
          </div>
        ))}
        
        {isProcessing && (
          <div className="flex justify-start">
            <div className="bg-muted rounded-lg px-4 py-2">
              <Loader2 className="w-4 h-4 animate-spin" />
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Voice Input */}
      <div className="border-t p-4">
        <AIVoiceInput
          onStart={() => setIsRecording(true)}
          onStop={(duration, audioBlob) => {
            setIsRecording(false);
            if (audioBlob) {
              handleVoiceInput(audioBlob);
            }
          }}
        />
      </div>

      {/* Text Input */}
      <form onSubmit={handleTextSubmit} className="border-t p-4">
        <div className="flex gap-2">
          <input
            type="text"
            value={textInput}
            onChange={(e) => setTextInput(e.target.value)}
            placeholder="Type a message..."
            className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
            disabled={isProcessing}
          />
          <Button
            type="submit"
            disabled={!textInput.trim() || isProcessing}
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </form>
    </div>
  );
}

