# ElevenLabs Voice Integration Guide

## 🔊 Adding Voice to PlantGuard AI

This guide explains how to integrate ElevenLabs text-to-speech for natural voice responses.

## 🎯 Why Voice?

- **Accessibility**: Helps users with visual impairments
- **Hands-free**: Listen while working in garden
- **Natural**: Human-like voice guidance
- **Professional**: Enhances user experience

## 📝 Quick Setup

### 1. Get API Key (Free Tier)

1. Visit https://elevenlabs.io
2. Sign up for free account
3. Go to Profile → API Keys
4. Copy your API key

**Free Tier Limits:**
- 10,000 characters/month
- ~20-30 diagnoses/month
- Perfect for personal use

### 2. Configure API Key

**Option A: Environment Variable (Recommended)**

Windows PowerShell:
```powershell
$env:ELEVENLABS_API_KEY="your_api_key_here"
```

Linux/Mac:
```bash
export ELEVENLABS_API_KEY="your_api_key_here"
```

**Option B: .env File**

Create `.env` file:
```
ELEVENLABS_API_KEY=your_api_key_here
```

Then modify `app.py`:
```python
from dotenv import load_dotenv
load_dotenv()

ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY', '')
```

**Option C: Direct in Code (Not Recommended for Production)**

Edit `app.py`:
```python
ELEVENLABS_API_KEY = "your_api_key_here"
```

### 3. Verify Integration

Start server and upload an image. You should see:
- 🔊 "Listen to advice" button
- Audio plays when clicked
- Natural voice reading the diagnosis

## 🎭 Voice Options

### Available Voices (Free Tier)

Current voice: **Rachel** (Female, American)
- Clear pronunciation
- Warm, professional tone
- Great for instructions

### Change Voice

Edit `app.py`, line ~120:
```python
# Current
url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"

# Options:
# Rachel (Female, American): 21m00Tcm4TlvDq8ikWAM
# Domi (Female, American): AZnzlk1XvdvUeBnXmlld
# Bella (Female, American): EXAVITQu4vr4xnSDxMaL
# Antoni (Male, American): ErXwobaYiN019PkySvjV
# Elli (Female, American): MF3mGyEYCl7XYWbV9V6O
# Josh (Male, American): TxGEqnHWrfWFTfGW9XjX
```

Example:
```python
url = "https://api.elevenlabs.io/v1/text-to-speech/TxGEqnHWrfWFTfGW9XjX"  # Josh
```

## 🎨 Voice Settings

Customize voice characteristics:

```python
"voice_settings": {
    "stability": 0.5,        # 0-1: Lower = more expressive
    "similarity_boost": 0.5  # 0-1: Higher = more similar to original
}
```

**Recommended Presets:**

**Professional (Current)**
```python
"stability": 0.5,
"similarity_boost": 0.5
```

**Friendly & Casual**
```python
"stability": 0.3,
"similarity_boost": 0.7
```

**Calm & Soothing**
```python
"stability": 0.7,
"similarity_boost": 0.4
```

## 🔧 Advanced Features

### 1. Optimize Response Text

Current implementation generates voice for:
- Disease detection results
- Treatment advice
- Chat responses

Optimize for voice by editing `app.py`:

```python
# Add pauses for better pacing
response_text = f"I've identified {display_name} with {confidence:.1f}% confidence. ... {treatment['treatment']}"

# Use SSML tags (if voice supports)
response_text = f"<speak>I've identified <emphasis level='strong'>{display_name}</emphasis></speak>"
```

### 2. Cache Audio Responses

For common responses, cache audio to save API calls:

```python
import hashlib
import os

AUDIO_CACHE_DIR = 'audio_cache'
os.makedirs(AUDIO_CACHE_DIR, exist_ok=True)

def generate_voice_response(text):
    # Generate cache key
    cache_key = hashlib.md5(text.encode()).hexdigest()
    cache_file = os.path.join(AUDIO_CACHE_DIR, f"{cache_key}.mp3")
    
    # Check cache
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            audio_bytes = f.read()
            return base64.b64encode(audio_bytes).decode('utf-8')
    
    # Generate new
    audio_base64 = generate_voice_from_api(text)
    
    # Save to cache
    if audio_base64:
        audio_bytes = base64.b64decode(audio_base64)
        with open(cache_file, 'wb') as f:
            f.write(audio_bytes)
    
    return audio_base64
```

### 3. Background Voice Generation

Generate voice asynchronously:

```python
import threading

def generate_voice_async(text, callback):
    def worker():
        audio = generate_voice_response(text)
        callback(audio)
    
    thread = threading.Thread(target=worker)
    thread.start()
```

### 4. Multiple Languages

ElevenLabs supports multiple languages:

```python
# Add language parameter
data = {
    "text": text,
    "model_id": "eleven_multilingual_v2",  # Use multilingual model
    "voice_settings": {
        "stability": 0.5,
        "similarity_boost": 0.5
    }
}
```

Supported languages:
- English, Spanish, French, German
- Italian, Polish, Portuguese
- Hindi, + more

## 📊 Monitoring Usage

Track your API usage:

```python
def log_voice_usage(text):
    char_count = len(text)
    with open('voice_usage.log', 'a') as f:
        f.write(f"{datetime.now()}: {char_count} characters\n")
```

Check remaining quota:
```bash
# View usage at https://elevenlabs.io/usage
```

## 🚫 Error Handling

Current implementation handles:
- Missing API key → No voice (silent failure)
- API errors → No voice (silent failure)
- Network issues → No voice (silent failure)

Improve error handling:

```python
def generate_voice_response(text):
    if not ELEVENLABS_API_KEY:
        print("⚠️  ElevenLabs API key not set")
        return None
    
    try:
        response = requests.post(url, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return base64.b64encode(response.content).decode('utf-8')
        elif response.status_code == 401:
            print("❌ Invalid API key")
        elif response.status_code == 429:
            print("⚠️  Rate limit exceeded")
        else:
            print(f"⚠️  API error: {response.status_code}")
        
        return None
    except requests.Timeout:
        print("⚠️  Request timeout")
        return None
    except Exception as e:
        print(f"❌ Voice generation error: {e}")
        return None
```

## 🎯 Best Practices

### 1. Character Optimization

Reduce character usage:

```python
# Before (verbose)
"Your plant has been diagnosed with Late Blight disease with a confidence level of 87.5%. This is a fungal infection. Treatment involves applying fungicide immediately."

# After (concise)
"Late Blight detected at 87% confidence. Fungal infection. Apply fungicide immediately."
```

### 2. User Preference

Let users toggle voice:

```javascript
// In index.html
let voiceEnabled = localStorage.getItem('voiceEnabled') !== 'false';

function toggleVoice() {
    voiceEnabled = !voiceEnabled;
    localStorage.setItem('voiceEnabled', voiceEnabled);
}

// Only show voice button if enabled
if (voiceEnabled && data.audio) {
    // Show button
}
```

### 3. Autoplay Option

```javascript
// Autoplay voice response
if (voiceEnabled && data.audio) {
    playAudio(data.audio);
}
```

## 💰 Pricing Tiers

**Free Tier**
- 10,000 characters/month
- Personal projects
- All voices

**Starter: $5/month**
- 30,000 characters/month
- Voice cloning
- Commercial use

**Creator: $22/month**
- 100,000 characters/month
- Professional projects

**Pro: $99/month**
- 500,000 characters/month
- Enterprise features

## ✅ Testing Checklist

- [ ] API key configured
- [ ] Server restarts successfully
- [ ] Upload test image
- [ ] "Listen" button appears
- [ ] Audio plays correctly
- [ ] Voice is clear and natural
- [ ] No console errors

## 🐛 Troubleshooting

**No voice button appears**
- Check API key is set
- Check console for errors
- Verify internet connection

**Audio doesn't play**
- Check browser audio is not muted
- Try different browser
- Check browser console for errors

**Poor voice quality**
- Adjust voice settings
- Try different voice
- Check internet speed

**Rate limit errors**
- Implement caching
- Reduce text length
- Upgrade plan

## 🔗 Resources

- [ElevenLabs Docs](https://docs.elevenlabs.io)
- [Voice Library](https://elevenlabs.io/voice-library)
- [API Reference](https://elevenlabs.io/docs/api-reference)
- [Pricing](https://elevenlabs.io/pricing)

## 🎉 Next Steps

1. ✅ Set up API key
2. ✅ Test voice generation
3. ✅ Customize voice settings
4. ✅ Implement caching
5. ✅ Add user preferences
6. ✅ Monitor usage

---

**Enjoy natural voice guidance in PlantGuard AI! 🔊🌱**
