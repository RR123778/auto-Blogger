import smtplib
import json
import urllib.parse
import requests
import os
import re
import math
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# ==========================================
# 1. CONFIGURATION & ENVIRONMENT SECRETS
# ==========================================
GEMINI_API_KEY = os.environ.get("GEMINI_KEY")
SENDER_GMAIL = os.environ.get("GMAIL_USER")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_PASS")
BLOGGER_SECRET_EMAIL = os.environ.get("BLOGGER_EMAIL")
WHATSAPP_PHONE_NUMBER = os.environ.get("WA_PHONE")
TEXTMEBOT_API_KEY = os.environ.get("TMB_KEY")
LANGUAGE_MODE = os.environ.get("BLOG_LANG", "HINDI").upper()

# Fallback topics if auto-trend generation fails
FALLBACK_NICHES = [
    "Artificial Intelligence and Future Jobs",
    "Latest Electric Vehicle Technologies",
    "Cybersecurity Best Practices for 2026",
    "Space Exploration and Mars Missions"
]

# ==========================================
# 2. HELPER FUNCTIONS
# ==========================================
def clean_json_response(raw_text):
    """Extracts valid JSON block even if markdown formatting is included."""
    match = re.search(r'```json\s*(.*?)\s*```', raw_text, re.DOTALL)
    if match:
        return match.group(1)
    return raw_text.strip()

def calculate_reading_time(html_content):
    """Calculates estimated reading time based on word count."""
    clean_text = re.sub(r'<[^>]+>', '', html_content)
    words = len(clean_text.split())
    minutes = math.ceil(words / 180) # Average reading speed
    return max(1, minutes)

# ==========================================
# 3. HIGH-TECH GEMINI AI GENERATOR
# ==========================================
def generate_ai_blog(language_mode):
    print(f"⚡ [AI Engine] Generating Trending Content in {language_mode}...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    
    lang_instruction = (
        "Write completely in fluent, natural Hindi (Devanagari script). Use clean modern tone."
        if language_mode == "HINDI" 
        else "Write in engaging, high-authority English."
    )

    prompt = f"""
    Act as a Master SEO Blogger and Content Architect.
    
    Task:
    1. Pick an extremely trending, high-search-volume topic related to Technology, AI, Tech Career, or Digital Trends.
    2. Write a comprehensive, long-form (1000+ words) highly structured blog post on this topic.
    
    Language Requirement:
    {lang_instruction}

    Formatting Rules:
    - Include engaging Subheadings (<h2>, <h3>).
    - Insert Bullet points (<ul>, <li>) and a Key Takeaways callout box (<div style="...">).
    - Output MUST strictly be valid raw JSON matching the exact schema below.

    JSON Schema Required:
    {{
        "title": "High-CTR Catchy SEO Title",
        "topic_name": "The underlying topic name",
        "meta_description": "150-character meta description",
        "image_prompt": "Ultra-detailed 8k cinematic lighting English prompt for Pollinations AI, ultra-realistic, no text on image",
        "content_html": "Full article HTML string (using <h2>, <h3>, <p>, <ul>, <li>, <strong>, <blockquote> tags)"
    }}
    """

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.7, "topP": 0.95}
    }
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        if response.status_code != 200:
            raise Exception(f"API Error {response.status_code}: {response.text}")
        
        raw_text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
        json_str = clean_json_response(raw_text)
        return json.loads(json_str)
    except Exception as e:
        print(f"❌ [AI Engine Error]: {e}")
        return None

# ==========================================
# 4. ADVANCED EMAIL (BLOGGER PUBLISHER)
# ==========================================
def publish_to_blogger(title, full_html):
    print("📧 [Blogger Engine] Sending optimized email package...")
    msg = MIMEMultipart("alternative")
    msg["From"] = SENDER_GMAIL
    msg["To"] = BLOGGER_SECRET_EMAIL
    msg["Subject"] = title

    part = MIMEText(full_html, "html", "utf-8")
    msg.attach(part)

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
            server.login(SENDER_GMAIL, GMAIL_APP_PASSWORD)
            server.sendmail(SENDER_GMAIL, BLOGGER_SECRET_EMAIL, msg.as_string())
        print("✅ [Blogger Engine] Post dispatched successfully!")
        return True
    except Exception as e:
        print(f"❌ [Email Failed]: {e}")
        return False

# ==========================================
# 5. WHATSAPP NOTIFIER (TEXTMEBOT)
# ==========================================
def notify_whatsapp(title, read_time, topic):
    print("📱 [WhatsApp Engine] Sending instant alert...")
    msg = (
        f"🚀 *New Blog Post Live!*\n\n"
        f"📌 *Title:* {title}\n"
        f"🎯 *Topic:* {topic}\n"
        f"⏱️ *Read Time:* ~{read_time} min\n"
        f"🌐 *Status:* Published to Blogger"
    )
    encoded = urllib.parse.quote(msg)
    url = f"https://api.textmebot.com/send.php?recipient={WHATSAPP_PHONE_NUMBER}&apikey={TEXTMEBOT_API_KEY}&text={encoded}"

    try:
        resp = requests.get(url, timeout=15)
        if resp.status_code == 200:
            print("📱 [WhatsApp Engine] Alert delivered!")
        else:
            print(f"⚠️ [WhatsApp Engine] Warning: {resp.text}")
    except Exception as e:
        print(f"❌ [WhatsApp Error]: {e}")

# ==========================================
# 6. PIPELINE ORCHESTRATOR
# ==========================================
def run_pipeline():
    print("=" * 50)
    print("🤖 STARTING AUTOMATED HIGH-TECH BLOGGER PIPELINE")
    print("=" * 50)

    # Step 1: Content Generation
    blog_data = generate_ai_blog(LANGUAGE_MODE)
    if not blog_data:
        print("❌ Pipeline stopped: Failed to generate blog content.")
        return

    title = blog_data.get("title", "Automated Tech Post")
    content_html = blog_data.get("content_html", "")
    image_prompt = blog_data.get("image_prompt", "Technology background cinematic")
    meta_desc = blog_data.get("meta_description", "")
    topic_name = blog_data.get("topic_name", "Technology")

    read_time = calculate_reading_time(content_html)

    # Step 2: Pollinations.ai Featured Image
    encoded_img_prompt = urllib.parse.quote(image_prompt)
    image_url = f"https://image.pollinations.ai/prompt/{encoded_img_prompt}?width=1200&height=630&nologo=true&seed=42"

    # Step 3: Inject Professional HTML Styling & Metadata Badges
    styled_header = f"""
    <div style="font-family: Arial, sans-serif; line-height: 1.7; color: #222;">
        <div style="text-align: center; margin-bottom: 25px;">
            <img src="{image_url}" alt="{title}" style="width: 100%; max-width: 850px; height: auto; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);" />
        </div>
        <div style="background: #f4f6f9; border-left: 4px solid #007bff; padding: 12px 20px; border-radius: 4px; margin-bottom: 25px; font-size: 14px;">
            <strong>⏱️ Reading Time:</strong> ~{read_time} Min | <strong>🏷️ Category:</strong> {topic_name}
            <p style="margin: 5px 0 0 0; color: #555; font-style: italic;">{meta_desc}</p>
        </div>
    """
    styled_footer = """
        <hr style="border: 0; height: 1px; background: #ddd; margin: 40px 0;" />
        <div style="background: #eef7ff; padding: 15px; border-radius: 8px; text-align: center; font-size: 13px; color: #0056b3;">
            🤖 <em>This post was automatically curated and written using Google Gemini AI.</em>
        </div>
    </div>
    """

    final_payload_html = styled_header + content_html + styled_footer

    # Step 4: Dispatch to Blogger
    if publish_to_blogger(title, final_payload_html):
        # Step 5: WhatsApp Notification
        notify_whatsapp(title, read_time, topic_name)
        print("\n🎉 ALL PIPELINE TASKS COMPLETED SUCCESSFULLY!")

if __name__ == "__main__":
    run_pipeline()