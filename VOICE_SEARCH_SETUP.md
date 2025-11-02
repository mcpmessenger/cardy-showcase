# Voice Search Integration Guide

## Overview
This guide explains how to set up and use the AI-powered voice search feature in the AIPro Store. The feature uses OpenAI's Whisper API for high-quality speech-to-text transcription.

## Features
- ✅ Real-time audio recording from user's microphone
- ✅ OpenAI Whisper API for accurate transcription
- ✅ Visual feedback during recording (timer, status)
- ✅ Error handling with user-friendly messages
- ✅ Integrated directly into search bar

## Setup Instructions

### 1. Get OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in or create an account
3. Create a new API key
4. Copy the key (starts with `sk-`)

### 2. Configure Environment Variables

#### Local Development
Create a `.env` file in the project root:
```bash
VITE_OPENAI_API_KEY=sk-your-actual-api-key-here
```

**Important:** Never commit your `.env` file to git. It's already in `.gitignore`.

#### Production Deployment (AWS Amplify)

1. Go to your AWS Amplify Console
2. Select your app
3. Navigate to **Environment variables**
4. Click **Manage variables**
5. Add a new variable:
   - Key: `VITE_OPENAI_API_KEY`
   - Value: Your OpenAI API key

### 3. Build and Deploy

The environment variable is automatically loaded during build:

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

## Component Architecture

### Components Created

1. **`ai-voice-input.tsx`** - Base voice input component with visualizer
2. **`voice-search-button.tsx`** - Button integrated into search
3. **`speech-to-text.ts`** - Service layer for OpenAI integration

### Integration Points

- **Products Page** (`src/pages/Products.tsx`): Main search bar with voice button
- **Hero Section** (`src/components/Hero.tsx`): Can be extended for homepage search

## Usage

### For Users
1. Click the microphone icon in the search bar
2. Browser will request microphone permission
3. Speak your search query
4. Click again to stop recording
5. Text will automatically populate and search

### For Developers

```tsx
import { VoiceSearchButton } from "@/components/ui/voice-search-button";

function MyComponent() {
  const handleTranscription = (text: string) => {
    console.log("User said:", text);
    // Use transcribed text
  };

  return (
    <VoiceSearchButton onTranscription={handleTranscription} />
  );
}
```

## API Costs

OpenAI Whisper pricing (as of 2024):
- $0.006 per minute of audio
- Average search query: 2-5 seconds
- Cost per query: ~$0.0002 - $0.0005

**Example monthly costs:**
- 1,000 searches: ~$0.50
- 10,000 searches: ~$5.00
- 100,000 searches: ~$50.00

## Browser Support

✅ **Supported:**
- Chrome 47+
- Edge 12+
- Firefox 29+
- Safari 11+

❌ **Not Supported:**
- Internet Explorer
- Older browsers without MediaRecorder API

## Security

1. **API Key Protection**
   - Stored in environment variables
   - Never exposed in client-side code
   - Using Vite's prefix `VITE_` for client-side access

2. **User Privacy**
   - Audio processed by OpenAI
   - No audio stored locally
   - HTTPS required for microphone access

3. **Rate Limiting**
   - Consider implementing rate limiting
   - Monitor API usage in OpenAI dashboard

## Troubleshooting

### "Voice search is not available"
- Check that `VITE_OPENAI_API_KEY` is set correctly
- Verify API key is valid
- Check browser console for errors

### "Failed to start recording"
- Check microphone permissions in browser
- Ensure HTTPS (required for microphone)
- Try different browser

### "No speech detected"
- Speak clearly and wait 1+ seconds
- Check microphone is working
- Reduce background noise

### High latency
- Check internet connection
- Consider using a closer OpenAI region
- Large audio files take longer to process

## Future Enhancements

Potential improvements:
- [ ] Offline speech recognition with Web Speech API fallback
- [ ] Support for multiple languages
- [ ] Voice command recognition (e.g., "show me headphones")
- [ ] Mobile-specific optimizations
- [ ] Rate limiting and usage analytics
- [ ] Progressive Web App support

## Support

For issues or questions:
1. Check browser console for errors
2. Verify API key is valid
3. Check OpenAI status page
4. Review this documentation

## License

This integration uses OpenAI's Whisper API. Please review OpenAI's terms of service and usage policies.

