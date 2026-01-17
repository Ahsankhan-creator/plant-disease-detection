from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
import base64
from PIL import Image
import io

# Load environment variables from .env file (for local development)
from pathlib import Path
env_path = Path('.') / '.env'
if env_path.exists():
    with open(env_path) as f:
        for line in f:
            if line.strip() and not line.startswith('#'):
                key, value = line.strip().split('=', 1)
                os.environ.setdefault(key, value)

# Set environment variables for minimal torch
os.environ['TRANSFORMERS_CACHE'] = '/tmp/transformers_cache'
os.environ['TORCH_HOME'] = '/tmp/torch_cache'

import torch
from torchvision import transforms
from transformers import AutoImageProcessor, AutoModelForImageClassification
import requests
from groq import Groq

# Force CPU mode to reduce memory
torch.set_num_threads(1)

app = Flask(__name__)
CORS(app)

# Load API keys from environment variables (secure for deployment)
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is required")
groq_client = Groq(api_key=GROQ_API_KEY)

# Weather API Configuration
WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
if not WEATHER_API_KEY:
    raise ValueError("WEATHER_API_KEY environment variable is required")
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

# ElevenLabs API Key
ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY')
if not ELEVENLABS_API_KEY:
    raise ValueError("ELEVENLABS_API_KEY environment variable is required")

# Configuration
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load the model (cached for performance)
MODEL_PATH = "./agri-plant-disease-resnet50"
print("🌱 Loading plant disease detection model...")
try:
    with torch.no_grad():
        processor = AutoImageProcessor.from_pretrained(MODEL_PATH)
        model = AutoModelForImageClassification.from_pretrained(
            MODEL_PATH,
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True
        )
        model.eval()
        # Optimize for inference
        torch.set_grad_enabled(False)
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    print("⚠️ Attempting to download model from Hugging Face...")
    with torch.no_grad():
        processor = AutoImageProcessor.from_pretrained("mesabo/agri-plant-disease-resnet50")
        model = AutoModelForImageClassification.from_pretrained(
            "mesabo/agri-plant-disease-resnet50",
            torch_dtype=torch.float32,
            low_cpu_mem_usage=True
        )
        model.eval()
        torch.set_grad_enabled(False)
    print("✅ Model downloaded and loaded!")

def generate_treatment_with_groq(disease_name, display_name, confidence, is_healthy):
    """Generate treatment information using Groq AI"""
    try:
        prompt = f"""You are a plant pathology expert. Provide treatment information for this plant diagnosis:

Disease: {display_name}
Confidence: {confidence:.1f}%
Status: {'Healthy' if is_healthy else 'Disease Detected'}

Provide a JSON response with EXACTLY these three fields (keep each under 80-150 words):
1. "cause": Brief explanation of what causes this condition
2. "treatment": Specific treatment steps and recommendations
3. "prevention": How to prevent this in the future

Be concise, practical, and specific. Use simple language."""

        response = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a plant disease expert. Always respond in valid JSON format with cause, treatment, and prevention fields."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=400
        )
        
        # Parse the AI response
        ai_response = response.choices[0].message.content.strip()
        
        # Try to extract JSON from response
        import json
        import re
        
        # Find JSON in response
        json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
        if json_match:
            treatment_data = json.loads(json_match.group())
            return {
                'cause': treatment_data.get('cause', 'Plant condition detected'),
                'treatment': treatment_data.get('treatment', 'Consult with agricultural expert'),
                'prevention': treatment_data.get('prevention', 'Maintain good plant health')
            }
        else:
            raise ValueError("No JSON found in response")
            
    except Exception as e:
        print(f"Groq treatment generation error: {e}")
        # Fallback to basic response
        if is_healthy:
            return {
                'cause': 'No disease detected',
                'treatment': 'Your plant appears healthy. Continue regular care and monitoring.',
                'prevention': 'Maintain consistent watering, proper nutrition, and good air circulation.'
            }
        else:
            return {
                'cause': 'Plant disease or stress condition',
                'treatment': 'Remove affected parts, improve growing conditions, and consult agricultural expert if symptoms persist.',
                'prevention': 'Ensure proper spacing, avoid overhead watering, practice crop rotation, and maintain plant health.'
            }

def predict_disease(image):
    """Run inference on the uploaded image"""
    # Preprocess image
    inputs = processor(images=image, return_tensors="pt")
    
    # Get predictions
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.nn.functional.softmax(logits, dim=-1)
        confidence, predicted_idx = torch.max(probabilities, 1)
    
    # Get label
    predicted_label = model.config.id2label[predicted_idx.item()]
    confidence_score = confidence.item() * 100
    
    return predicted_label, confidence_score

# Conversation context storage (simple in-memory for now)
conversation_context = {}

def generate_voice_response(text):
    """Generate voice response using ElevenLabs API"""
    if not ELEVENLABS_API_KEY:
        return None
    
    try:
        url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"  # Rachel voice
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            audio_base64 = base64.b64encode(response.content).decode('utf-8')
            return audio_base64
        return None
    except Exception as e:
        print(f"Error generating voice: {e}")
        return None

def get_weather_data(city=None, lat=None, lon=None):
    """Fetch weather data from OpenWeatherMap API"""
    try:
        params = {
            'appid': WEATHER_API_KEY,
            'units': 'metric'  # Use Celsius
        }
        
        if city:
            params['q'] = city
        elif lat and lon:
            params['lat'] = lat
            params['lon'] = lon
        else:
            # Default to a major city if no location provided
            params['q'] = 'karachi'
        
        response = requests.get(WEATHER_API_URL, params=params, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'temperature': round(data['main']['temp'], 1),
                'feels_like': round(data['main']['feels_like'], 1),
                'humidity': data['main']['humidity'],
                'description': data['weather'][0]['description'].title(),
                'icon': data['weather'][0]['icon'],
                'wind_speed': round(data['wind']['speed'] * 3.6, 1),  # Convert m/s to km/h
                'city': data['name'],
                'country': data['sys']['country'],
                'pressure': data['main']['pressure'],
                'visibility': data.get('visibility', 0) / 1000  # Convert to km
            }
        else:
            return None
    except Exception as e:
        print(f"Weather API error: {e}")
        return None

def format_weather_for_groq(weather_data):
    """Format weather data for Groq context"""
    if not weather_data:
        return ""
    
    return f"""\n🌤️ CURRENT WEATHER DATA:
- Location: {weather_data['city']}, {weather_data['country']}
- Temperature: {weather_data['temperature']}°C (Feels like {weather_data['feels_like']}°C)
- Conditions: {weather_data['description']}
- Humidity: {weather_data['humidity']}%
- Wind Speed: {weather_data['wind_speed']} km/h

Consider these weather conditions when providing plant care advice:
- High humidity may increase fungal disease risk
- Hot weather requires more frequent watering
- Strong winds can damage plants
- Cold temperatures may stress plants"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/detect', methods=['POST'])
def detect_disease():
    try:
        # Get session ID for context tracking
        session_id = request.form.get('session_id', 'default')
        
        # Get image from request
        if 'image' not in request.files:
            return jsonify({'error': 'No image provided'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No image selected'}), 400
        
        # Validate file type
        allowed_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.webp'}
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in allowed_extensions:
            return jsonify({'error': f'Invalid file type. Please upload an image file ({', '.join(allowed_extensions)})'}), 400
        
        # Read and process image
        image_bytes = file.read()
        
        # Validate image can be opened
        try:
            image = Image.open(io.BytesIO(image_bytes))
            image.verify()  # Verify it's a valid image
            image = Image.open(io.BytesIO(image_bytes)).convert('RGB')  # Reopen after verify
        except Exception as img_error:
            return jsonify({'error': 'Invalid or corrupted image file. Please upload a clear photo of plant leaves.'}), 400
        
        # Check image dimensions (too small = likely not a proper photo)
        width, height = image.size
        if width < 50 or height < 50:
            return jsonify({'error': 'Image is too small. Please upload a clear, high-quality photo of your plant.'}), 400
        
        # Get prediction
        disease_name, confidence = predict_disease(image)
        
        # Validate confidence - reject images that don't look like plants
        # If confidence is very low, the image is likely not a plant
        if confidence < 15.0:
            return jsonify({
                'error': 'This doesn\'t appear to be a plant image. Please upload a clear photo of plant leaves for disease detection.',
                'suggestion': 'Make sure your photo shows plant leaves clearly with good lighting.'
            }), 400
        
        # Format disease name for display
        display_name = disease_name.replace('___', ' - ').replace('_', ' ')
        plant_type = disease_name.split('___')[0] if '___' in disease_name else 'Unknown'
        is_healthy = 'healthy' in disease_name.lower()
        
        # Generate treatment info using Groq AI
        treatment = generate_treatment_with_groq(disease_name, display_name, confidence, is_healthy)
        
        # Create response text
        if is_healthy:
            response_text = f"Great news! Your plant appears healthy with {confidence:.1f}% confidence. {treatment['treatment']}"
        else:
            response_text = f"Detection complete. I've identified {display_name} with {confidence:.1f}% confidence. {treatment['treatment']}"
        
        # Generate voice response
        audio_data = generate_voice_response(response_text)
        
        # Store context for follow-up questions
        conversation_context[session_id] = {
            'disease': display_name,
            'confidence': round(confidence, 2),
            'cause': treatment['cause'],
            'treatment': treatment['treatment'],
            'prevention': treatment['prevention'],
            'plant_type': plant_type,
            'is_healthy': 'healthy' in disease_name.lower()
        }
        
        return jsonify({
            'disease': display_name,
            'confidence': round(confidence, 2),
            'cause': treatment['cause'],
            'treatment': treatment['treatment'],
            'prevention': treatment['prevention'],
            'message': response_text,
            'audio': audio_data,
            'session_id': session_id
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle text-based chat queries with Groq AI - context-aware for uploaded images"""
    try:
        data = request.json
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', 'default')
        location = data.get('location', None)  # Optional location from user
        
        if not user_message:
            return jsonify({'error': 'Empty message'}), 400
        
        # Get weather data for context
        weather_data = None
        if location:
            weather_data = get_weather_data(city=location)
        else:
            # Try to get default weather data
            weather_data = get_weather_data()
        
        # Check if user has uploaded an image (has context)
        has_context = session_id in conversation_context
        context_info = conversation_context.get(session_id, {})
        
        # Use Groq for intelligent responses
        try:
            # Build context-aware system prompt
            system_prompt = """You are PlantGuard AI, an expert plant disease detection assistant with deep knowledge of plant pathology, agriculture, and plant care. 

Your responsibilities:
- Answer questions about plant diseases, symptoms, causes, and treatments
- Provide advice on plant care, prevention, and maintenance
- Guide users on how to use the disease detection system
- Explain agricultural best practices
- Be friendly, helpful, and concise

Key information about this system:
- You can detect diseases in tomatoes (10 conditions) and potatoes (3 conditions)
- The AI uses ResNet50 with 95%+ accuracy
- Users upload images for instant analysis (2-3 seconds)
- Voice responses are available via ElevenLabs
- The interface is ChatGPT-style for easy use

Guidelines:
- Keep responses under 150-200 words unless detailed explanation is needed
- Use simple, clear language
- Include emojis sparingly for friendliness (🌱 🍅 🥔 ✅)
- If you don't know something, say so honestly
- Always encourage users to upload images for accurate diagnosis"""
            
            # Add context if image was uploaded
            if has_context:
                system_prompt += f"""

🎯 IMPORTANT - User has uploaded an image:
- Detected: {context_info.get('disease', 'Unknown')}
- Confidence: {context_info.get('confidence', 0)}%
- Plant Type: {context_info.get('plant_type', 'Unknown')}
- Status: {'Healthy' if context_info.get('is_healthy') else 'Disease detected'}
- Cause: {context_info.get('cause', 'N/A')}
- Treatment: {context_info.get('treatment', 'N/A')}
- Prevention: {context_info.get('prevention', 'N/A')}

When user asks questions, assume they're asking about THIS specific detection result. 
Answer questions about this plant, this disease, this treatment, etc.
Be specific and reference the detection results when relevant."""
            
            # Add weather context
            if weather_data:
                system_prompt += format_weather_for_groq(weather_data)
            
            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_message
                    }
                ],
                model="llama-3.3-70b-versatile",  # Fast and intelligent
                temperature=0.7,
                max_tokens=500,
                top_p=0.9
            )
            
            response = chat_completion.choices[0].message.content.strip()
            
        except Exception as groq_error:
            # Fallback to basic responses if Groq fails
            print(f"Groq API error: {groq_error}")
            response = get_fallback_response(user_message.lower())
        
        # Generate voice for response
        audio_data = generate_voice_response(response)
        
        return jsonify({
            'response': response,
            'audio': audio_data
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_fallback_response(user_message):
    """Fallback responses if Groq API fails"""
    if 'hello' in user_message or 'hi' in user_message:
        return "Hello! I'm PlantGuard AI, your intelligent plant disease detection assistant. 👋 Upload a photo of your plant's leaves, and I'll help identify any diseases!"
    elif 'help' in user_message:
        return "I can help you detect plant diseases! 🌿 Just upload a clear photo of your plant's leaves using the 📎 Upload button, and I'll provide detailed analysis and treatment recommendations."
    elif 'upload' in user_message:
        return "To upload an image, click the 📎 Upload button below. Make sure your photo is clear, well-lit, and shows the affected leaves for best results!"
    else:
        return "I'm here to help with plant disease detection! 🌱 Upload a photo of your plant for instant AI-powered analysis, or ask me any questions about plant diseases and care."

@app.route('/api/weather', methods=['GET', 'POST'])
def get_weather():
    """Get weather data for a location"""
    try:
        if request.method == 'POST':
            data = request.json
            location = data.get('location', '')
            lat = data.get('lat')
            lon = data.get('lon')
        else:
            location = request.args.get('location', '')
            lat = request.args.get('lat')
            lon = request.args.get('lon')
        
        # Priority: coordinates > city name > default
        if lat and lon:
            try:
                weather_data = get_weather_data(lat=float(lat), lon=float(lon))
            except (ValueError, TypeError):
                weather_data = None
        elif location:
            weather_data = get_weather_data(city=location)
        else:
            # Fallback to default location
            weather_data = get_weather_data(city='London')
        
        if weather_data:
            # Add plant care recommendations based on weather
            recommendations = []
            
            if weather_data['temperature'] > 30:
                recommendations.append("🌡️ High temperature: Water plants more frequently and provide shade")
            elif weather_data['temperature'] < 10:
                recommendations.append("❄️ Low temperature: Protect sensitive plants from cold")
            
            if weather_data['humidity'] > 80:
                recommendations.append("💧 High humidity: Watch for fungal diseases, ensure good air circulation")
            elif weather_data['humidity'] < 30:
                recommendations.append("🌵 Low humidity: Increase watering frequency")
            
            if weather_data['wind_speed'] > 30:
                recommendations.append("💨 Strong winds: Stake tall plants and protect from wind damage")
            
            weather_data['plant_care_tips'] = recommendations
            
            return jsonify(weather_data)
        else:
            return jsonify({'error': 'Unable to fetch weather data'}), 400
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🌱 PlantGuard AI is starting...")
    print("Model loaded successfully!")
    print("Server running on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
