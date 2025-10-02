import streamlit as st
import os
import io
import tempfile
import base64
from PIL import Image
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Nano Banana Party Photo Editor",
    page_icon="🍌",
    layout="wide"
)

# Custom CSS for birthday party theme
st.markdown("""
<style>
    .main-header {
        text-align: center;
        color: #FF6B6B;
        margin-bottom: 2rem;
        font-family: 'Comic Sans MS', cursive;
    }
    .party-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    .upload-section {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        margin: 1rem 0;
        border: 2px dashed #FF6B6B;
        text-align: center;
    }
    .prompt-section {
        padding: 1rem;
        margin: 1rem 0;
    }
    .results-section {
        background-color: #d4edda;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #28a745;
    }
    .stButton > button {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.5rem 2rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: scale(1.05);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    /* Mobile optimizations */
    @media (max-width: 768px) {
        .main-container {
            padding: 0.5rem;
        }
        .party-section {
            margin: 0.5rem 0;
            padding: 1rem;
        }
        .upload-section {
            padding: 1rem;
        }
        .prompt-section {
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Pre-defined prompts for birthday party
PREDEFINED_PROMPTS = {
    "german_kinky": "😈 German Kinky Style - Change clothing to playful German themed kinky outfits with sexy leather and accessories",
    "cr7_hug": "⚽ Cristiano Ronaldo Super Fan - Make them hugging a life-size Cristiano Ronaldo doll with football background",
    "silly_madness": "🤪 Silly Madness - Add ridiculous props like oversized sunglasses, clown noses, and funny hats. Change the outputs to epic party mode.",
    "shroomy": "🍄 Shroomy - Make the people appear in a colorful shroomy world. Change the outfits to alice in wonderland mode.",
}

def generate_single_photo(uploaded_image, prompt_name, prompt_description):
    """Generate a single photo for a specific prompt"""
    try:
        client = genai.Client(
            api_key=os.environ.get("GEMINI_API_KEY"),
        )

        model = "gemini-2.5-flash-image-preview"
        
        # Create focused prompt for this specific theme with quality emphasis
        full_prompt = f"🎉 Birthday Party Photo Magic! Remove the green screen background and {prompt_description} Create a high-resolution, professional, fun, and party-ready image! Keep the person prominent and natural. Use high-quality details, sharp focus, and vibrant colors. Make it look like a professional silly party photo."
        
        response = client.models.generate_content(
            model=model,
            contents=[full_prompt, uploaded_image],
        )

        generated_images = []
        
        # Check if response and candidates exist
        if not response or not response.candidates or len(response.candidates) == 0:
            st.error(f"❌ No response from AI for {prompt_name}")
            return []
        
        candidate = response.candidates[0]
        if not candidate.content or not candidate.content.parts:
            st.error(f"❌ Invalid response structure for {prompt_name}")
            return []
        
        for part in candidate.content.parts:
            if part.text is not None:
                st.info(f"💭 {prompt_name}: {part.text}")
            elif part.inline_data is not None:
                # Save the generated image with high quality
                safe_name = prompt_name.replace(" ", "_").replace("📂", "").strip()
                file_name = f"party_photo_{safe_name}.jpg"
                image = Image.open(io.BytesIO(part.inline_data.data))
                
                # Convert to RGB if necessary and save with high quality
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Save as high-quality JPEG (quality=95)
                image.save(file_name, 'JPEG', quality=95, optimize=True)
                
                # Add to display list
                generated_images.append((image, file_name, prompt_name))
        
        return generated_images
        
    except Exception as e:
        st.error(f"❌ Error creating {prompt_name} photo: {str(e)}")
        return []

def generate_party_photos(uploaded_image, selected_prompts, custom_prompts):
    """Generate multiple photos - one per prompt"""
    if not selected_prompts and not custom_prompts:
        return []
    
    generated_images = []
    total_photos = len(selected_prompts) + len(custom_prompts)
    
    # Create progress containers
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    current_index = 0
    
    # Generate photos for predefined prompts
    for prompt_key in selected_prompts:
        if prompt_key in PREDEFINED_PROMPTS:
            current_index += 1
            prompt_name = PREDEFINED_PROMPTS[prompt_key]
            status_text.text(f"🎨 Generating: {prompt_name}")
            progress_bar.progress(current_index / total_photos)
            
            with st.spinner(f"Creating {prompt_name.lower()}..."):
                photos = generate_single_photo(uploaded_image, prompt_name, PREDEFINED_PROMPTS[prompt_key])
                generated_images.extend(photos)
    
    # Generate photos for custom prompts
    for custom_prompt in custom_prompts:
        if custom_prompt.strip():
            current_index += 1
            prompt_name = "Custom Creation"
            status_text.text(f"✨ Custom Creation: {custom_prompt}")
            progress_bar.progress(current_index / total_photos)
            
            with st.spinner(f"Creating your custom idea: {custom_prompt[:30]}..."):
                photos = generate_single_photo(uploaded_image, f"Custom: {custom_prompt}", custom_prompt)
                generated_images.extend(photos)
    
    # Complete progress
    progress_bar.progress(1.0)
    status_text.text("🎉 All photos generated successfully!")
    
    return generated_images

def main():
    # Header
    st.markdown('<h1 class="main-header">🍌 Nano Banana Party Photo Editor</h1>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; font-size: 18px; color: #666; margin-bottom: 2rem;">✨ Take photos with greenscreen and transform them into magical birthday party memories! ✨</div>', unsafe_allow_html=True)
    
    # Initialize session state
    if 'generated_images' not in st.session_state:
        st.session_state.generated_images = []
    if 'custom_prompts' not in st.session_state:
        st.session_state.custom_prompts = []
    
    # Single column mobile-first layout
    st.markdown('### 📸 Step 1: Take Your Photo')
    
    uploaded_file = st.file_uploader(
        "📷 Upload your greenscreen photo",
        type=['png', 'jpg', 'jpeg', 'webp'],
        help="Upload a photo with greenscreen background (PNG, JPG, JPEG, or WebP)",
        key="photo_upload"
    )
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        # Display smaller image for mobile
        st.image(image, caption="🎭 Your Original Photo", width=300)
        st.session_state.current_image = image

    st.markdown('</div>', unsafe_allow_html=True)
    
    #st.markdown('<div class="party-section">', unsafe_allow_html=True)
    st.markdown('### 🎨 Step 2: Choose Your Magic!')
    
    # Pre-defined prompts section
    st.markdown('#### 🌟 Pre-made Party Themes (check all you want!):')
    
    selected_prompts = []
    for prompt_key, prompt_text in PREDEFINED_PROMPTS.items():
        if st.checkbox(prompt_text, key=f"predefined_{prompt_key}"):
            selected_prompts.append(prompt_key)
        
    # Custom prompts section
    st.markdown('#### ✨ Add Your Own Ideas:')
    
    # Display existing custom prompts
    if st.session_state.custom_prompts:
        for i, custom_prompt in enumerate(st.session_state.custom_prompts):
            col_display, col_remove = st.columns([4, 1])
            with col_display:
                st.write(f"💡 {custom_prompt}")
            with col_remove:
                if st.button("🗑️", key=f"remove_{i}", help="Remove this prompt"):
                    st.session_state.custom_prompts.pop(i)
                    st.rerun()
    
    # Add new custom prompt
    new_prompt = st.text_input(
        "💫 Add a custom idea:",
        placeholder="e.g., Make it look like a winter wonderland",
        key="new_prompt_input"
    )
    
    if st.button("➕ Add Custom Prompt", disabled=not new_prompt.strip()):
        st.session_state.custom_prompts.append(new_prompt)
        st.rerun()
    
    
    # Generate section
    if 'current_image' in st.session_state:
        st.markdown('### 🚀 Step 3: Create Your Magic Photo!')
        
        # Show selected prompts summary
        if selected_prompts or st.session_state.custom_prompts:
            st.markdown('**🎯 Selected Effects:**')
            
            # Show predefined selections
            for prompt_key in selected_prompts:
                st.markdown(f"✅ {PREDEFINED_PROMPTS[prompt_key]}")
            
            # Show custom selections
            for custom_prompt in st.session_state.custom_prompts:
                st.markdown(f"✅ {custom_prompt}")
        
        if st.button("🎨 Generate Magic Photos!", type="primary", disabled=not (selected_prompts or st.session_state.custom_prompts)):
            if not os.environ.get("GEMINI_API_KEY"):
                st.error("❌ Please set your GEMINI_API_KEY in the .env file")
            else:
                # Show estimated time
                total_prompts = len(selected_prompts) + len(st.session_state.custom_prompts)
                st.info(f"⏱️ Generating {total_prompts} photos (1 per prompt selected). This may take {total_prompts * 15-30} seconds...")
                
                # Generate the photos
                generated_images = generate_party_photos(
                    st.session_state.current_image,
                    selected_prompts,
                    st.session_state.custom_prompts
                )
                
                # Store generated images in session state
                st.session_state.generated_images = generated_images
                
                # Show completion message
                st.success(f"🎉 Successfully generated {len(generated_images)} amazing photos!")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Results section
    if 'generated_images' in st.session_state and st.session_state.generated_images:
        st.markdown('<div class="results-section">', unsafe_allow_html=True)
        st.markdown('### 🎉 Your Amazing Party Photos!')
        
        # Vertical gallery for generated images
        total_images = len(st.session_state.generated_images)
        
        if total_images > 0:
            st.markdown(f"**📸 All {total_images} Party Photos:**")
            
            for i, image_data in enumerate(st.session_state.generated_images):
                # Handle different image data formats
                if len(image_data) == 3:
                    image, filename, prompt_name = image_data
                    caption = f"🎨 {prompt_name}"
                else:
                    image, filename = image_data
                    caption = f"🎨 Photo {i + 1}"
                
                # Display image
                st.image(image, caption=caption, width=500)
                
                # Download button below each image
                download_label = f"📥 Download: {prompt_name}" if len(image_data) == 3 else f"📥 Download Photo {i + 1}"
                
                # Create download button
                buf = io.BytesIO()
                image.save(buf, format='JPEG', quality=95)
                byte_im = buf.getvalue()
                
                st.download_button(
                    label=download_label,
                    data=byte_im,
                    file_name=filename,
                    mime="image/jpeg",
                    key=f"gallery_download_{i}",
                    use_container_width=True
                )
                
                # Add some space between photos
                if i < total_images - 1:
                    st.markdown("---")
        
        # Download options
        st.markdown("**📥 Download Your Photos:**")
        
        if st.button("📦 Download All Photos", type="primary", key="download_all"):
            # Create individual download buttons for all photos
            st.success("📸 Download individual photos below!")
            
            for i, image_data in enumerate(st.session_state.generated_images):
                if len(image_data) == 3:
                    image, filename, prompt_name = image_data
                    download_label = f"📥 {prompt_name}"
                else:
                    image, filename = image_data
                    download_label = f"📥 Photo {i+1}"
                
                # Create download button
                buf = io.BytesIO()
                image.save(buf, format='JPEG', quality=95)
                byte_im = buf.getvalue()
                
                st.download_button(
                    label=download_label,
                    data=byte_im,
                    file_name=filename,
                    mime="image/jpeg",
                    key=f"bulk_download_{i}"
                )
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")

if __name__ == "__main__":
    main()