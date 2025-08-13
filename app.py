#!/usr/bin/env python3
import streamlit as st
import os
import io
from PIL import Image
from gtts import gTTS
import pyttsx3
import tempfile

# =============================================================================
# CONFIGURATION
# =============================================================================

# Load API key from environment or .env file
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
if not ANTHROPIC_API_KEY:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    except ImportError:
        pass

# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================

def initialize_session_state():
    """Initialize all session state variables"""
    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None

# =============================================================================
# AI ANALYSIS ENGINE
# =============================================================================

class PerceptoAI:
    """Consolidated AI analysis engine using Claude vision"""
    
    def __init__(self):
        if not ANTHROPIC_API_KEY:
            raise ValueError("ANTHROPIC_API_KEY is not set. Please check your .env file.")
        
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
            self.vision_models = [
                "claude-3-5-sonnet-20241022",
                "claude-3-5-haiku-20241022", 
                "claude-3-sonnet-20240229",
                "claude-3-haiku-20240307"
            ]
            self.model = self.vision_models[0]
        except Exception as e:
            print(f"Error initializing Claude client: {e}")
            self.client = None
    
    def _image_to_base64(self, image):
        """Convert PIL image to base64 with compression to stay under 5MB limit"""
        import base64
        
        # Convert to RGB if needed
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        
        # Resize image if too large (max dimension 1920px)
        max_size = 1920
        if image.width > max_size or image.height > max_size:
            image.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        # Try different quality levels to stay under 5MB
        max_size_bytes = 5 * 1024 * 1024  # 5MB
        
        for quality in [85, 70, 50, 30]:
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=quality, optimize=True)
            image_bytes = buffer.getvalue()
            
            if len(image_bytes) < max_size_bytes:
                return base64.b64encode(image_bytes).decode('utf-8'), 'jpeg'
        
        # If still too large, resize more aggressively
        for max_dim in [1280, 960, 640]:
            if image.width > max_dim or image.height > max_dim:
                image.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
                buffer = io.BytesIO()
                image.save(buffer, format='JPEG', quality=50, optimize=True)
                image_bytes = buffer.getvalue()
                
                if len(image_bytes) < max_size_bytes:
                    return base64.b64encode(image_bytes).decode('utf-8'), 'jpeg'
        
        # Final fallback - very small image
        image.thumbnail((480, 480), Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        image.save(buffer, format='JPEG', quality=30, optimize=True)
        image_bytes = buffer.getvalue()
        return base64.b64encode(image_bytes).decode('utf-8'), 'jpeg'
    
    def analyze_image(self, uploaded_file):
        """Analyze image using Claude vision API"""
        if not self.client:
            return {"error": "Claude client not initialized"}
        
        try:
            # Load image
            image = Image.open(uploaded_file)
            image_data, image_format = self._image_to_base64(image)
            
            # Prepare message for Claude
            message_content = [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": f"image/{image_format}",
                        "data": image_data
                    }
                },
                {
                    "type": "text",
                    "text": """Please provide a detailed, accessible description of this image. Focus on:

1. Overall scene and setting
2. People, objects, and their positions
3. Colors, lighting, and visual details
4. Any text visible in the image
5. Spatial relationships (left, right, center, background, foreground)

Write in clear, descriptive language that would be helpful for someone who cannot see the image. Be specific about locations, colors, and what's happening in the scene."""
                }
            ]
            
            # Try each model until one works
            for model in self.vision_models:
                try:
                    response = self.client.messages.create(
                        model=model,
                        max_tokens=1000,
                        messages=[{"role": "user", "content": message_content}]
                    )
                    
                    description = response.content[0].text
                    
                    # Generate audio
                    audio_file = self._generate_audio(description)
                    
                    return {
                        'description': description,
                        'audio_file': audio_file,
                        'model_used': model
                    }
                    
                except Exception as e:
                    print(f"Model {model} failed: {e}")
                    continue
            
            return {"error": "All models failed. Please try again later."}
            
        except Exception as e:
            return {"error": f"Analysis failed: {str(e)}"}
    
    def _generate_audio(self, text):
        """Generate audio from text using TTS"""
        try:
            # Try gTTS first (better quality)
            tts = gTTS(text=text, lang='en', slow=False)
            audio_buffer = io.BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            return audio_buffer.getvalue()
        except:
            try:
                # Fallback to pyttsx3 (offline)
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
                engine.setProperty('volume', 0.9)
                
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    engine.save_to_file(text, tmp_file.name)
                    engine.runAndWait()
                    
                    with open(tmp_file.name, 'rb') as f:
                        audio_data = f.read()
                    
                    os.unlink(tmp_file.name)
                    return audio_data
            except:
                return None

# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_header():
    """Render the main header with dark theme"""
    st.markdown("""
    <div style='text-align: center; padding: 20px; margin-bottom: 20px; background: linear-gradient(135deg, #1e1e1e 0%, #2d2d2d 100%); border-radius: 10px;'>
        <h1 style='color: #64b5f6; margin: 0 0 5px 0; font-size: 2.5rem; font-weight: 600;'>👁️ Percepto</h1>
        <p style='color: #b0bec5; margin: 0; font-size: 16px;'>AI Vision for Accessibility</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Render the sidebar with app information"""
    st.markdown("""
    <div style='background: #2d3748; padding: 15px; border-radius: 8px; margin-bottom: 15px;'>
        <h4 style='color: #81c784; margin: 0 0 8px 0; text-align: center;'>🔍 Accessibility Mode</h4>
        <p style='color: #e0e0e0; text-align: center; margin: 0; font-size: 14px;'>AI-powered descriptions with audio</p>
    </div>
    
    <div style='background: #1e2936; padding: 15px; border-radius: 8px; border-left: 3px solid #64b5f6;'>
        <h5 style='color: #64b5f6; margin: 0 0 10px 0;'>Features:</h5>
        <ul style='color: #b0bec5; margin: 0; padding-left: 15px; font-size: 14px; line-height: 1.4;'>
            <li>AI image analysis</li>
            <li>Clear descriptions</li>
            <li>Text-to-speech</li>
            <li>Mobile-friendly</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def render_upload_section():
    """Render the image upload section"""
    st.markdown("""
    <div style='background: #263238; padding: 15px; border-radius: 8px; margin-bottom: 20px;'>
        <h4 style='color: #4fc3f7; margin: 0; text-align: center;'>📤 Upload Image</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Input method selection
    input_method = st.radio(
        "Choose input method:",
        ["📁 Upload File", "📷 Take Photo"],
        horizontal=True
    )
    
    uploaded_file = None
    
    if input_method == "📁 Upload File":
        uploaded_file = st.file_uploader(
            "Choose an image file", 
            type=['png', 'jpg', 'jpeg', 'bmp', 'webp'],
            key="image_upload_v2",  # Changed key to force refresh
            help="Limit 10MB per file • PNG, JPG, JPEG, BMP, WEBP"
        )
    else:
        uploaded_file = st.camera_input("Take a photo with your camera")
    
    if uploaded_file is not None:
        # Check file size (10MB limit)
        file_size = uploaded_file.size if hasattr(uploaded_file, 'size') else len(uploaded_file.read())
        uploaded_file.seek(0)  # Reset file pointer after reading
        
        max_size_mb = 10
        max_size_bytes = max_size_mb * 1024 * 1024  # 10MB in bytes
        
        if file_size > max_size_bytes:
            st.error(f"❌ File too large! Maximum size allowed is {max_size_mb}MB. Your file is {file_size / 1024 / 1024:.1f}MB.")
            st.info("💡 Please compress your image or choose a smaller file.")
            st.session_state.uploaded_file = None
        else:
            st.session_state.uploaded_file = uploaded_file
            st.success(f"✅ Image uploaded successfully! ({file_size / 1024 / 1024:.1f}MB)")
            st.image(uploaded_file, caption="📸 Your uploaded image", use_column_width=True)
    else:
        st.session_state.uploaded_file = None
    
    if st.session_state.uploaded_file:
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔍 **Analyze Image**", type="primary", use_container_width=True):
                return True
    return False

def render_results_section():
    """Render the analysis results section"""
    st.markdown("""
    <div style='background: #1a237e; padding: 15px; border-radius: 8px; margin-bottom: 20px;'>
        <h4 style='color: #7986cb; margin: 0; text-align: center;'>📊 Results</h4>
    </div>
    """, unsafe_allow_html=True)
    
    if st.session_state.analysis_results:
        results = st.session_state.analysis_results
        
        # Show description
        st.markdown("""
        <div style='background: linear-gradient(135deg, #2e3440 0%, #434c5e 100%); padding: 25px; border-radius: 15px; margin: 20px 0; border-left: 5px solid #81c784; box-shadow: 0 4px 15px rgba(0,0,0,0.2);'>
            <h4 style='color: #81c784; margin-bottom: 15px;'>📝 Image Description</h4>
        </div>
        """, unsafe_allow_html=True)
        
        description = results.get('description', 'No description available')
        st.markdown(f"""
        <div style='background: #1e2936; padding: 25px; border-radius: 12px; margin: 20px 0; border: 2px solid #37474f; box-shadow: 0 4px 15px rgba(0,0,0,0.3);'>
            <p style='color: #e8eaf6; line-height: 1.8; font-size: 16px; margin: 0;'>{description}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show audio
        if 'audio_file' in results and results['audio_file']:
            st.markdown("""
            <div style='background: linear-gradient(135deg, #4a148c 0%, #7b1fa2 100%); padding: 25px; border-radius: 15px; margin: 20px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.2);'>
                <h4 style='color: #ce93d8; margin-bottom: 15px;'>🔊 Audio Description</h4>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div style='background: #1a1a2e; padding: 20px; border-radius: 12px; margin: 10px 0; border: 2px solid #7b1fa2;'>
                <p style='color: #d1c4e9; margin: 0; text-align: center;'>🎧 Listen to the audio description below - perfect for accessibility!</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.audio(results['audio_file'], format='audio/mp3')
        
        # Tips section
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1b5e20 0%, #388e3c 100%); padding: 25px; border-radius: 15px; margin: 20px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.2);'>
            <h4 style='color: #a5d6a7; margin-bottom: 15px;'>💡 Tips</h4>
            <ul style='color: #c8e6c9; margin: 0; padding-left: 20px; line-height: 1.8;'>
                <li>Use headphones for better audio quality</li>
                <li>The description is optimized for screen readers</li>
                <li>Try different images for various types of analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    else:
        # Placeholder
        st.markdown("""
        <div style='background: #2d3748; padding: 30px; border-radius: 15px; margin: 20px 0; border: 2px dashed #4a5568; text-align: center;'>
            <p style='color: #a0aec0; font-size: 18px; margin-bottom: 20px;'>📤 Upload an image and click "🔍 Analyze Image" to see AI-powered results here.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Features preview
        st.markdown("""
        <div style='background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%); padding: 25px; border-radius: 15px; margin: 20px 0; box-shadow: 0 4px 15px rgba(0,0,0,0.2);'>
            <h4 style='color: #90cdf4; margin-bottom: 15px;'>🌟 What you'll get:</h4>
            <ul style='color: #bee3f8; margin: 0; padding-left: 20px; line-height: 1.8;'>
                <li><strong style='color: #63b3ed;'>Detailed Description:</strong> AI analyzes your image and provides a comprehensive description</li>
                <li><strong style='color: #63b3ed;'>Audio Output:</strong> Text-to-speech conversion for accessibility</li>
                <li><strong style='color: #63b3ed;'>Screen Reader Friendly:</strong> Optimized for assistive technologies</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def render_footer():
    """Render simple footer with creator information - InkLink style"""
    st.markdown(
        """
        <div style='text-align: center; color: #666; font-size: 12px; margin-top: 1rem; padding: 10px;'>
            <p>Made with ❤️ by <strong>Geetanshi Goel</strong></p>
            <div style='margin-top: 8px;'>
                <a href="https://github.com/geetanshi0205" target="_blank" style='margin: 0 8px; text-decoration: none;'>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" style="vertical-align: middle;">
                        <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.30.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                    </svg>
                </a>
                <a href="https://www.linkedin.com/in/geetanshi-goel-49ba5832b/" target="_blank" style='margin: 0 8px; text-decoration: none;'>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" style="vertical-align: middle;">
                        <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                    </svg>
                </a>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    """Main application function"""
    # Page configuration
    st.set_page_config(
        page_title="Percepto - AI Vision for Accessibility",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Dark theme CSS
    st.markdown("""
    <style>
        .stApp {
            background-color: #0e1117;
            color: #ffffff;
        }
        .stSidebar {
            background-color: #1a1d21;
        }
        .stMarkdown {
            color: #ffffff;
        }
        .stRadio > label {
            color: #ffffff !important;
        }
        .stFileUploader > label {
            color: #ffffff !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # Render header
    render_header()
    
    # Render sidebar
    with st.sidebar:
        render_sidebar()
    
    # Render main content
    should_analyze = render_upload_section()
    
    # Handle analysis
    if should_analyze:
        with st.spinner("🤖 Analyzing your image with AI..."):
            try:
                ai = PerceptoAI()
                results = ai.analyze_image(st.session_state.uploaded_file)
                
                if "error" in results:
                    st.error(f"❌ Analysis failed: {results['error']}")
                    st.info("💡 Please try uploading a different image or check your internet connection.")
                else:
                    st.session_state.analysis_results = results
                    st.success("✅ Analysis completed successfully!")
                    
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                st.info("💡 Please check your ANTHROPIC_API_KEY and internet connection.")
    
    # Render results
    render_results_section()
    
    # Render footer
    render_footer()

if __name__ == "__main__":
    main()