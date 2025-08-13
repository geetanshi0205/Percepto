# 👁️ Percepto - AI Vision for Accessibility

**An AI-powered accessibility app that transforms visual content into detailed descriptions and audio, making images accessible for visually impaired users.**

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![Claude AI](https://img.shields.io/badge/Claude-AI-purple.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📖 About The Project

Percepto is a streamlined, single-file accessibility application that leverages Claude AI's vision capabilities to provide comprehensive image descriptions and audio output. Designed specifically for accessibility, it transforms visual content into clear, descriptive text optimized for screen readers and includes text-to-speech functionality.

### 🎯 **Key Goals:**
- **Accessibility First**: Designed specifically for visually impaired users
- **AI-Powered**: Uses Claude's advanced vision models for accurate descriptions
- **Audio Ready**: Automatic text-to-speech for hands-free operation
- **Simple & Fast**: Single-file deployment with minimal dependencies

## ✨ Features

### 🤖 **AI Vision Analysis**
- **Advanced Image Understanding**: Powered by Claude 3.5 Sonnet and Haiku models
- **Detailed Descriptions**: Comprehensive analysis of scenes, objects, people, colors, and spatial relationships
- **Text Recognition**: Automatically identifies and reads any text in images
- **Smart Compression**: Automatically optimizes images for API processing

### 🔊 **Audio Accessibility**
- **Text-to-Speech**: High-quality audio generation using gTTS and pyttsx3
- **Screen Reader Optimized**: Descriptions formatted for assistive technologies
- **Multiple TTS Engines**: Online (gTTS) and offline (pyttsx3) fallbacks

### 🎨 **User Interface**
- **Dark Theme**: Professional, eye-friendly interface
- **Mobile Responsive**: Works seamlessly on all devices
- **Clean Design**: Distraction-free, accessibility-focused layout
- **Intuitive Controls**: Simple upload, analyze, and listen workflow

### 🛡️ **Smart File Handling**
- **10MB Upload Limit**: Clear error messages for oversized files
- **Multiple Formats**: Supports PNG, JPG, JPEG, BMP, WEBP
- **Camera Integration**: Take photos directly in the app
- **File Size Display**: Shows exact file size in upload confirmations

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Anthropic API key ([Get yours here](https://console.anthropic.com/))

### Installation

1. **Clone or download the project**
   ```bash
   # Download the files or clone the repository
   # You only need: app.py, requirements.txt, and this README.md
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your API key**
   
   Create a `.env` file in the project directory:
   ```env
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```
   
   Or set it as an environment variable:
   ```bash
   export ANTHROPIC_API_KEY=your_anthropic_api_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Open your browser**
   
   The app will automatically open at `http://localhost:8501`

## 📋 Dependencies

```
streamlit>=1.28.1      # Web app framework
anthropic>=0.63.0      # Claude AI API client
pillow>=10.0.1         # Image processing
gtts>=2.4.0           # Google Text-to-Speech
pyttsx3>=2.90         # Offline Text-to-Speech
python-dotenv>=1.0.0  # Environment variable management
```

## 🎮 How to Use

### 1. **Upload an Image**
   - Click "📁 Upload File" to select an image from your device
   - Or use "📷 Take Photo" to capture an image with your camera
   - Maximum file size: 10MB

### 2. **Analyze the Image**
   - Click the "🔍 Analyze Image" button
   - Wait for AI processing (usually 3-10 seconds)

### 3. **Get Results**
   - **Description**: Read the detailed text description
   - **Audio**: Listen to the text-to-speech audio output
   - **Tips**: Follow helpful accessibility suggestions

### 4. **Accessibility Features**
   - Use with screen readers for full accessibility
   - Audio descriptions work with headphones or speakers
   - All interface elements are keyboard accessible

## 🏗️ Architecture

### **Single-File Design**
Percepto is built as a single Python file (`app.py`) containing:
- **AI Engine**: Claude API integration with model fallbacks
- **Image Processing**: Smart compression and format handling
- **UI Components**: Complete Streamlit interface
- **Audio Generation**: TTS with multiple engine support
- **Error Handling**: Robust fallback mechanisms

### **Key Components**
```python
PerceptoAI()              # Main AI analysis class
render_header()           # App header and branding
render_sidebar()          # Feature information
render_upload_section()   # File upload with size validation
render_results_section()  # Description and audio display
render_footer()           # Developer attribution
```

## 🎯 Use Cases

### **For Visually Impaired Users**
- **Photo descriptions** for social media images
- **Document reading** for scanned text
- **Scene understanding** for navigation assistance
- **Art and media** accessibility

### **For Developers & Organizations**
- **Accessibility compliance** for websites and apps
- **Content moderation** and image analysis
- **Educational tools** for accessibility awareness
- **Integration** into larger accessibility systems

## 🔧 Configuration

### **Environment Variables**
```env
ANTHROPIC_API_KEY=sk-ant-...    # Required: Your Claude API key
```

### **Model Fallbacks**
The app automatically tries multiple Claude models:
1. `claude-3-5-sonnet-20241022` (Best quality)
2. `claude-3-5-haiku-20241022` (Fast alternative)
3. `claude-3-sonnet-20240229` (Stable backup)
4. `claude-3-haiku-20240307` (Final fallback)

### **File Size Limits**
- **Upload Limit**: 10MB maximum per file
- **API Processing**: Automatically compressed to under 5MB
- **Supported Formats**: PNG, JPG, JPEG, BMP, WEBP

## 🚀 Deployment

### **Streamlit Cloud**
1. Upload `app.py`, `requirements.txt`, and `README.md`
2. Set `ANTHROPIC_API_KEY` in Streamlit secrets
3. Deploy with one click

### **Local Development**
```bash
streamlit run app.py --server.port 8501
```

### **Docker (Optional)**
```dockerfile
FROM python:3.9-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

## 🤝 Contributing

Contributions are welcome! This project focuses on accessibility, so please ensure any changes maintain or improve accessibility features.

### **Areas for Improvement**
- Additional language support for TTS
- More image format support
- Enhanced error handling
- Performance optimizations

## 📄 License

This project is licensed under the MIT License - feel free to use it in your own projects.

## 🙋‍♀️ Support

If you encounter any issues:
1. Check that your `ANTHROPIC_API_KEY` is set correctly
2. Ensure your image is under 10MB
3. Verify your internet connection for API calls
4. Try a different image format if upload fails

## 👩‍💻 Developer

**Created with ❤️ by [Geetanshi Goel](https://github.com/geetanshi0205)**

- **GitHub**: [@geetanshi0205](https://github.com/geetanshi0205)
- **LinkedIn**: [Geetanshi Goel](https://www.linkedin.com/in/geetanshi-goel-49ba5832b/)
- **Portfolio**: [View Projects](https://github.com/geetanshi0205?tab=repositories)

---

<div align="center">
  <p><strong>Making visual content accessible through AI-powered technology</strong></p>
  <p>⭐ Star this repo if it helped you!</p>
</div>