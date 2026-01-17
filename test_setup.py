"""
Test script to verify PlantGuard AI setup
"""

import sys
import os

def check_dependencies():
    """Check if all required packages are installed"""
    print("🔍 Checking dependencies...")
    required_packages = [
        'flask',
        'torch',
        'transformers',
        'PIL',
        'requests'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} - NOT FOUND")
            missing.append(package)
    
    return len(missing) == 0

def check_model_files():
    """Check if model files exist"""
    print("\n🔍 Checking model files...")
    model_dir = "agri-plant-disease-resnet50"
    
    if not os.path.exists(model_dir):
        print(f"  ❌ Model directory not found: {model_dir}")
        return False
    
    required_files = ['config.json', 'model.safetensors', 'preprocessor_config.json']
    all_found = True
    
    for file in required_files:
        path = os.path.join(model_dir, file)
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"  ✅ {file} ({size:,} bytes)")
        else:
            print(f"  ❌ {file} - NOT FOUND")
            all_found = False
    
    return all_found

def check_project_structure():
    """Check if all project files exist"""
    print("\n🔍 Checking project structure...")
    required_files = [
        'app.py',
        'templates/index.html',
        'requirements.txt',
        'README.md'
    ]
    
    all_found = True
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - NOT FOUND")
            all_found = False
    
    return all_found

def test_model_loading():
    """Test if model can be loaded"""
    print("\n🔍 Testing model loading...")
    try:
        from transformers import AutoImageProcessor, AutoModelForImageClassification
        
        model_path = "./agri-plant-disease-resnet50"
        print(f"  Loading from {model_path}...")
        
        processor = AutoImageProcessor.from_pretrained(model_path)
        print("  ✅ Processor loaded")
        
        model = AutoModelForImageClassification.from_pretrained(model_path)
        print("  ✅ Model loaded")
        
        # Check model configuration
        num_labels = model.config.num_labels
        print(f"  ℹ️  Model can detect {num_labels} different plant conditions")
        
        return True
    except Exception as e:
        print(f"  ❌ Error loading model: {e}")
        return False

def main():
    print("="*60)
    print("  PlantGuard AI - Setup Verification")
    print("="*60)
    
    checks = [
        ("Dependencies", check_dependencies),
        ("Project Structure", check_project_structure),
        ("Model Files", check_model_files),
        ("Model Loading", test_model_loading)
    ]
    
    results = []
    for name, check_func in checks:
        result = check_func()
        results.append((name, result))
    
    print("\n" + "="*60)
    print("  Summary")
    print("="*60)
    
    all_passed = True
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {name}")
        if not result:
            all_passed = False
    
    print("\n" + "="*60)
    
    if all_passed:
        print("✅ All checks passed! Ready to run PlantGuard AI")
        print("\nTo start the server, run:")
        print("  python app.py")
        print("\nOr use the startup script:")
        print("  Windows: start.bat")
        print("  Linux/Mac: ./start.sh")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Clone model: git clone https://huggingface.co/mesabo/agri-plant-disease-resnet50")
    
    print("="*60)

if __name__ == '__main__':
    main()
