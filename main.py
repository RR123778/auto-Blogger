import os
import re
import math
import urllib.parse
import smtplib
import base64
from email.mime.text import MIMEText
import requests

# ==========================================
# 1. ENVIRONMENT VARIABLES & SECRETS
# ==========================================
print("==========================================")
print("🔍 [DEBUG] Step 1: Checking Environment Variables...")
GEMINI_API_KEY = os.getenv("GEMINI_KEY")
GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_PASS = os.getenv("GMAIL_PASS")
BLOGGER_EMAIL = os.getenv("BLOGGER_EMAIL")
WHATSAPP_PHONE_NUMBER = os.getenv("WA_PHONE")
TEXTMEBOT_API_KEY = os.getenv("TMB_KEY")
BLOG_LANGUAGE = os.getenv("BLOG_LANG", "HINDI")

print(f"👉 GEMINI_KEY Present: {bool(GEMINI_API_KEY)}")
print(f"👉 GMAIL_USER: {GMAIL_USER}")
print(f"👉 GMAIL_PASS Present: {bool(GMAIL_PASS)}")
print(f"👉 BLOGGER_EMAIL: {BLOGGER_EMAIL}")
print(f"👉 WA_PHONE: {WHATSAPP_PHONE_NUMBER}")
print(f"👉 TMB_KEY Present: {bool(TEXTMEBOT_API_KEY)}")
print("==========================================")


# ==========================================
# 2. BACKUP EMAIL ALERT ENGINE
# ==========================================
def send_backup_email_alert(title, topic, error_msg):
    print("📧 [Backup Email Engine] Sending fallback email notification...")
    try:
        subject = f"⚠️ [Alert] Blog Published (WhatsApp Failed): {title}"
        body = (
            f"Hello,\n\n"
            f"Aapka blog post successfully publish ho gaya hai, lekin TextMeBot alert fail ho gaya tha.\n\n"
            f"📌 Title: {title}\n"
            f"🎯 Topic: {topic}\n"
            f"⚠️ TextMeBot Error: {error_msg}\n\n"
            f"Status: Published to Blogger\n"
        )
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = GMAIL_USER
        msg['To'] = GMAIL_USER

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.send_message(msg)
        print("📧 [Backup Email Engine] Fallback Email alert sent successfully!")
    except Exception as mail_err:
        print(f"⚠️ [Backup Email Engine] Failed to send fallback email: {mail_err}")


# ==========================================
# 3. CRASH-PROOF WHATSAPP ENGINE WITH FALLBACK
# ==========================================
def send_whatsapp_alert(title, read_time, topic):
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
        resp = requests.get(url, timeout=10)
        print(f"🔍 [DEBUG] TextMeBot HTTP Status: {resp.status_code}")
        print(f"🔍 [DEBUG] TextMeBot Response: {resp.text}")
        if resp.status_code == 200 and "ERR" not in resp.text:
            print("📱 [WhatsApp Engine] Alert delivered successfully!")
        else:
            error_details = resp.text
            print(f"⚠️ [WhatsApp Engine] WhatsApp failed! Triggering email fallback... Details: {error_details}")
            send_backup_email_alert(title, topic, error_details)
    except Exception as e:
        print(f"⚠️ [WhatsApp Engine] TextMeBot Error/Down: {e}. Triggering email fallback...")
        send_backup_email_alert(title, topic, str(e))


# ==========================================
# 4. GEMINI AI CONTENT GENERATOR
# ==========================================
def generate_blog_content():
    print("🤖 [Gemini Engine] Generating trending blog post...")
    
    prompt = (
        f"Write a highly engaging, SEO-optimized, comprehensive blog post in {BLOG_LANGUAGE}. "
        "Pick a popular trending topic in AI, tech, online earning, or modern skills. "
        "Structure the output in clean HTML with <h2>, <h3>, <p>, and <ul>/<li> tags. "
        "Do NOT include markdown block markers like ```html. "
        "The first line MUST be the title wrapped inside <h1> tags."
    )
    
    url = f"[https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=](https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=){GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    print("🔍 [DEBUG] Sending request to Gemini API...")
    response = requests.post(url, json=payload, headers=headers, timeout=30)
    
    print(f"🔍 [DEBUG] Gemini API HTTP Status: {response.status_code}")
    if response.status_code != 200:
        print(f"❌ [DEBUG] Gemini API Error Response: {response.text}")
        
    response.raise_for_status()
    
    data = response.json()
    raw_text = data['candidates'][0]['content']['parts'][0]['text']
    print(f"🔍 [DEBUG] Raw Content Generated (First 150 chars): {raw_text[:150]}...")
    
    title_match = re.search(r'<h1>(.*?)</h1>', raw_text, re.IGNORECASE | re.DOTALL)
    if title_match:
        title = title_match.group(1).strip()
        body_html = re.sub(r'<h1>.*?</h1>', '', raw_text, count=1, flags=re.IGNORECASE | re.DOTALL).strip()
    else:
        title = "Trending Tech & AI Insights"
        body_html = raw_text

    print(f"✅ [Gemini Engine] Extracted Title: {title}")
    return title, body_html


# ==========================================
# 5. POLLINATIONS AI IMAGE GENERATOR (FIXED & BASE64 EMBEDDED)
# ==========================================
def get_featured_image(topic):
    print("🎨 [Image Engine] Generating featured image via Pollinations.ai...")
    prompt_encoded = urllib.parse.quote(f"hd cinematic concept art of {topic}, vibrant lighting, 8k resolution")
    clean_image_url = f"[https://image.pollinations.ai/prompt/](https://image.pollinations.ai/prompt/){prompt_encoded}?width=800&height=450&nologo=true"
    print(f"🔍 [DEBUG] Pollinations Target URL: {clean_image_url}")
    
    try:
        # Image fetch karke Base64 string banate hain taaki Blogger email me bypass na ho
        resp = requests.get(clean_image_url, timeout=20)
        if resp.status_code == 200:
            b64_image = base64.b64encode(resp.content).decode('utf-8')
            img_src = f"data:image/jpeg;base64,{b64_image}"
            print("✅ [Image Engine] Image fetched and converted to Base64 successfully!")
        else:
            print(f"⚠️ [Image Engine] Pollinations returned HTTP {resp.status_code}. Using direct URL fallback.")
            img_src = clean_image_url
    except Exception as img_err:
        print(f"⚠️ [Image Engine] Failed to fetch image binary: {img_err}. Using direct URL fallback.")
        img_src = clean_image_url

    return f'<p><img src="{img_src}" alt="{topic}" style="width:100%; height:auto; border-radius:8px; margin-bottom:20px;"></p>'


# ==========================================
# 6. GMAIL-TO-BLOGGER PUBLISHER ENGINE
# ==========================================
def publish_to_blogger(title, full_html):
    print("📧 [Blogger Engine] Publishing blog via Gmail Secret Address...")
    print(f"🔍 [DEBUG] Sending Email From: {GMAIL_USER} To: {BLOGGER_EMAIL}")
    
    msg = MIMEText(full_html, 'html')
    msg['Subject'] = title
    msg['From'] = GMAIL_USER
    msg['To'] = BLOGGER_EMAIL

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30) as server:
            server.set_debuglevel(1)
            print("🔍 [DEBUG] Connecting to Gmail SMTP SSL...")
            server.login(GMAIL_USER, GMAIL_PASS)
            print("🔍 [DEBUG] Gmail Login Successful! Sending Message...")
            server.send_message(msg)
        print("✅ [Blogger Engine] Successfully delivered email to Blogger Secret Email!")
    except Exception as smtp_err:
        print(f"❌ [DEBUG] Gmail SMTP Exception: {smtp_err}")
        raise smtp_err


# ==========================================
# MAIN EXECUTION FLOW
# ==========================================
def main():
    print("🚀 [System] Starting Auto Blog Publisher...")
    
    title, body_html = generate_blog_content()
    
    word_count = len(re.sub(r'<[^>]*>', '', body_html).split())
    read_time = max(1, math.ceil(word_count / 200))
    print(f"🔍 [DEBUG] Calculated Word Count: {word_count}, Read Time: {read_time} min")
    
    image_html = get_featured_image(title)
    badge_html = f'<p>⏱️ <i>Reading Time: ~{read_time} min</i></p><hr>'
    final_content = image_html + badge_html + body_html
    
    publish_to_blogger(title, final_content)
    
    send_whatsapp_alert(title, read_time, title)
    
    print("🎉 [System] All tasks completed successfully!")

if __name__ == "__main__":
    main()