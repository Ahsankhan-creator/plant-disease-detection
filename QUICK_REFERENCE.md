# PlantGuard AI - Quick Reference Card

## 🚀 Quick Commands

### Start Server
```bash
# Quick start (all platforms)
python app.py

# Or use scripts
start.bat          # Windows
./start.sh         # Linux/Mac
```

### Test Setup
```bash
python test_setup.py
```

### Install Dependencies
```bash
pip install -r requirements.txt
```

## 📡 API Endpoints

### Disease Detection
```bash
POST /api/detect
Content-Type: multipart/form-data
Body: image=<file>

Response:
{
  "disease": "Tomato - Late Blight",
  "confidence": 87.5,
  "cause": "Fungal infection",
  "treatment": "Apply fungicide...",
  "prevention": "Ensure good air...",
  "message": "Detection complete...",
  "audio": "base64_encoded_audio"
}
```

### Chat
```bash
POST /api/chat
Content-Type: application/json
Body: {"message": "How do I use this?"}

Response:
{
  "response": "I can help...",
  "audio": "base64_encoded_audio"
}
```

## 🔧 Configuration

### Server Settings (app.py)
```python
# Port
app.run(port=5000)

# Debug mode
app.run(debug=True)

# Host
app.run(host='0.0.0.0')  # All interfaces
```

### Model Path
```python
MODEL_PATH = "./agri-plant-disease-resnet50"
```

### ElevenLabs
```python
ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY', '')
```

## 🎨 UI Customization

### Colors (index.html)
```css
/* Primary color (green accent) */
background: #10b981;

/* User message bubble */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Background */
background: #f7f7f8;
```

### Fonts
```css
font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
```

## 📊 Project Structure Map

```
📦 Project Root
├── 🐍 app.py                    Backend server
├── 📋 requirements.txt          Dependencies
├── 📖 README.md                 Overview
├── 📘 SETUP_GUIDE.md           Complete guide
├── 🔊 ELEVENLABS_GUIDE.md      Voice integration
├── ✅ test_setup.py             Verification
│
├── 📁 templates/
│   └── 🌐 index.html           ChatGPT-style UI
│
├── 🤖 agri-plant-disease-resnet50/
│   ├── config.json
│   ├── model.safetensors        (194 MB)
│   └── preprocessor_config.json
│
├── 📁 AgriGenius/              Reference code
├── 📁 .venv/                   Python environment
└── 📁 uploads/                 Temp images
```

## 🔍 Common Tasks

### Add New Disease Treatment
Edit `app.py`, line ~25:
```python
DISEASE_TREATMENTS = {
    "Plant___Disease_Name": {
        "cause": "What causes it",
        "treatment": "How to treat",
        "prevention": "How to prevent"
    }
}
```

### Change Voice
Edit `app.py`, line ~120:
```python
url = "https://api.elevenlabs.io/v1/text-to-speech/VOICE_ID"
```

### Modify Welcome Message
Edit `index.html`, line ~450:
```html
<h2 class="welcome-title">Your Title</h2>
<p class="welcome-text">Your text...</p>
```

### Add New Chat Response
Edit `app.py`, line ~180:
```python
@app.route('/api/chat', methods=['POST'])
def chat():
    if 'your_keyword' in user_message:
        response = "Your custom response"
```

## 🐛 Debug Checklist

### Server won't start
- [ ] Check port 5000 is free
- [ ] Verify Python 3.8+
- [ ] Check all dependencies installed
- [ ] Look for syntax errors

### Model not loading
- [ ] Verify model files exist
- [ ] Check Git LFS installed
- [ ] Run `git lfs pull`
- [ ] Verify disk space (need ~500MB)

### No predictions
- [ ] Check image format (JPG/PNG)
- [ ] Verify image not corrupted
- [ ] Check console for errors
- [ ] Test with sample image

### Voice not working
- [ ] Verify API key set
- [ ] Check internet connection
- [ ] Verify API quota not exceeded
- [ ] Check browser console

## 📈 Performance Tips

### Optimize Model Loading
```python
# Load model once at startup (already done)
# Don't reload per request
```

### Image Optimization
```python
# Resize large images before processing
max_size = (800, 800)
image.thumbnail(max_size, Image.LANCZOS)
```

### Caching Responses
```python
# Cache common responses
from functools import lru_cache

@lru_cache(maxsize=100)
def get_treatment_info(disease_name):
    return DISEASE_TREATMENTS.get(disease_name)
```

## 🔐 Security Notes

### For Production
- [ ] Remove debug mode: `debug=False`
- [ ] Add authentication
- [ ] Implement rate limiting
- [ ] Use HTTPS
- [ ] Sanitize file uploads
- [ ] Add CORS restrictions
- [ ] Use environment variables
- [ ] Add request validation

### Current Security (Development Only)
⚠️ **This is for local development only**
- CORS enabled for all origins
- No authentication
- No rate limiting
- Debug mode enabled

## 📱 Testing Workflow

### 1. Unit Test
```bash
python test_setup.py
```

### 2. Manual Test
1. Start server
2. Open http://localhost:5000
3. Type "hello"
4. Upload test image
5. Check voice button
6. Test mobile view

### 3. Browser Console
Press F12 → Console → Check for errors

## 📞 URLs & Resources

| Resource | URL |
|----------|-----|
| Local App | http://localhost:5000 |
| Model Repo | https://huggingface.co/mesabo/agri-plant-disease-resnet50 |
| Reference | https://github.com/jayeshbhandarkar/AgriGenius |
| ElevenLabs | https://elevenlabs.io |
| Flask Docs | https://flask.palletsprojects.com |

## 🎯 Development Roadmap

### Current (v1.0 - MVP)
- ✅ ChatGPT-style UI
- ✅ Image upload
- ✅ Disease detection
- ✅ Voice responses
- ✅ Mobile responsive

### Next (v1.1)
- [ ] User accounts
- [ ] History
- [ ] Dark mode
- [ ] Export reports

### Future (v2.0)
- [ ] Mobile app
- [ ] Offline mode
- [ ] More plants
- [ ] Growth tracking

## 💡 Pro Tips

1. **Keep responses concise** for better voice experience
2. **Use clear images** for better detection accuracy
3. **Test on mobile** regularly for responsive design
4. **Monitor API usage** to stay within free tier
5. **Cache audio** to reduce API calls
6. **Add error logging** for debugging
7. **Version control** your changes with git
8. **Backup** before major changes

## 📚 Learning Resources

- Python Flask: Official docs
- PyTorch: pytorch.org/tutorials
- Transformers: huggingface.co/docs
- HTML/CSS: MDN Web Docs
- JavaScript: javascript.info

## 🎓 Key Concepts

### ResNet50
- 50-layer deep convolutional neural network
- Pre-trained on ImageNet
- Fine-tuned for plant diseases

### Transfer Learning
- Use pre-trained model
- Fine-tune on specific dataset
- Faster training, better results

### Text-to-Speech
- Convert text to natural speech
- ElevenLabs uses AI voices
- Customizable voice characteristics

### REST API
- HTTP endpoints
- JSON responses
- Stateless communication

---

**Keep this card handy for quick reference! 📌**
