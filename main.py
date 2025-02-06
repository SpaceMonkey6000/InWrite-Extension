import streamlit as st
import requests
import json

# Configure page
st.set_page_config(
    page_title="LinkedIn Post Generator",
    page_icon="✍️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling
st.markdown("""
    <style>
        .stSelectbox [data-testid='stMarkdownContainer'] {
            font-size: 18px;
        }
        .stButton button {
            width: 100%;
            background: #0A66C2;
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 16px;
            cursor: pointer;
            transition: 0.3s;
        }
        .stButton button:hover {
            background: #004182;
        }
        .success-message {
            padding: 1rem;
            background: #0E1117;
            border-radius: 8px;
            border-left: 4px solid #0A66C2;
            margin: 1rem 0;
        }
    </style>
""", unsafe_allow_html=True)

# API configurations (Replace with your actual API keys)
NEWS_API_KEY = "b752a0d1e2644510a92fb3426c1d6088"
OPENROUTER_API_KEY = "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"
OPENROUTER_MODEL = "openai/gpt-3.5-turbo"  # Change this to your preferred model

# Header Section
st.markdown("<h1 style='text-align: center; margin-bottom: 2rem;'>📝 LinkedIn Post Generator</h1>", unsafe_allow_html=True)

# Main content
with st.container():
    niche = st.selectbox(
        "Select your niche:",
        ["Finance", "Tech", "Science", "Startups", "Consulting", "Business", "Management"],
        index=0,
        help="Choose the industry for your LinkedIn post"
    )

    generate_button = st.button("Generate Post ✨")

# Function to fetch news
def get_latest_news(topic):
    try:
        url = f"https://newsapi.org/v2/everything?q={topic}&sortBy=popularity&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        articles = response.json().get('articles', [])
        return articles[0] if articles else None
    except Exception as e:
        st.error(f"Error fetching news: {e}")
        return None

# Function to generate post
def generate_linkedin_post(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {
                "role": "user",
                "content": f"""
                    Create a professional LinkedIn post about this news article: 
                    {prompt}
                    
                    Requirements:
                    - Use professional but engaging tone
                    - Include relevant hashtags
                    - Add emojis where appropriate
                    - Keep paragraphs short
                    - Include key takeaways
                    - Add a call-to-action question
                """
            }
        ]
    }

    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            data=json.dumps(payload)
        )
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        st.error(f"Error generating post: {e}")
        return None

# Handle generation
if generate_button:
    if not NEWS_API_KEY or not OPENROUTER_API_KEY:
        st.error("Please configure your API keys first!")
        st.stop()

    with st.spinner("📰 Finding latest industry news..."):
        news_article = get_latest_news(niche)
        
        if news_article:
            prompt = f"""
                Article Title: {news_article.get('title', '')}
                Source: {news_article.get('source', {}).get('name', '')}
                Description: {news_article.get('description', '')}
                Content: {news_article.get('content', '')}
            """
            
            with st.spinner("🧠 Crafting professional post..."):
                post = generate_linkedin_post(prompt)
                
                if post:
                    st.markdown("<div class='success-message'>🎉 Post Generated Successfully!</div>", unsafe_allow_html=True)
                    st.markdown("---")
                    st.markdown(post)
                    st.markdown("---")
                    st.download_button(
                        label="Download Post 📥",
                        data=post,
                        file_name=f"{niche.lower()}_linkedin_post.md",
                        mime="text/markdown"
                    )