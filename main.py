import os
import re
import math
import urllib.parse
import smtplib
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
    
    proto = "https://"
    domain = "api.textmebot.com/send.php"
    url = f"{proto}{domain}?recipient={WHATSAPP_PHONE_NUMBER}&apikey={TEXTMEBOT_API_KEY}&text={encoded}"

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
# 4. ROTATION CONTROL ENGINE (ROUND-ROBIN)
# ==========================================
def get_next_category():
    # Sequence: Finance -> Fashion -> Online Earning -> Technology -> Repeat
    categories = [
        "Finance & Personal Money Management (Investment, Budgeting, Crypto & Financial Literacy)",
        "Fashion, Lifestyle & Style Trends (Outfit Ideas, Beauty Tips, Accessories & Personal Styling)",
        "Online Earning & Work From Home Ideas (Freelancing, Passive Income, Blogging & Smart Earning)",
        "Technology & AI Tools (Smartphones, Software, AI Innovations & Gadget Reviews)"
    ]
    
    state_file = "category_index.txt"
    current_index = 0

    if os.path.exists(state_file):
        try:
            with open(state_file, "r") as f:
                content = f.read().strip()
                if content:
                    current_index = int(content)
        except Exception as e:
            print(f"⚠️️ [State Warning] Index file read issue: {e}")
            current_index = 0

    if current_index >= len(categories) or current_index < 0:
        current_index = 0

    selected_category = categories[current_index]

    next_index = (current_index + 1) % len(categories)
    try:
        with open(state_file, "w") as f:
            f.write(str(next_index))
    except Exception as e:
        print(f"⚠️ [State Warning] Index file update fail hua: {e}")

    return selected_category


# ==========================================
# 5. HIGH-RANKING SEO GEMINI AI GENERATOR
# ==========================================
def generate_blog_content():
    print("🤖 [Gemini Engine] Generating High-Ranking SEO Blog Content...")
    
    selected_category = get_next_category()
    print(f"🎯 [DEBUG] Selected Sequence Category: {selected_category}")
    
    prompt = (
        f"Act as a professional SEO Content Writer. Write an in-depth, original, and highly comprehensive blog post in {BLOG_LANGUAGE}. "
        f"The post MUST focus on a viral, highly searched, low-competition topic inside the category: '{selected_category}'.\n\n"
        "SEO Formatting Rules:\n"
        "1. First line MUST be a highly catchy, keyword-rich H1 Title wrapped in <h1>Title</h1>.\n"
        "2. Add a strong Hook/Introduction (150 words) naturally incorporating main search keywords.\n"
        "3. Divide content into structured sections using <h2> and <h3> subheadings.\n"
        "4. Include bullet points (<ul><li>) and key takeaway callouts for high reader retention.\n"
        "5. Conclude with a clear FAQ section (2-3 questions) at the end to target Google Snippets.\n"
        "6. Output ONLY pure semantic HTML without markdown block indicators like ```html."
    )
    
    proto = "https://"
    domain = "generativelanguage.googleapis.com"
    path = "/v1beta/models/gemini-2.5-flash:generateContent"
    url = f"{proto}{domain}{path}?key={GEMINI_API_KEY}"
    
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
    
    title_match = re.search(r'<h1>(.*?)</h1>', raw_text, re.IGNORECASE | re.DOTALL)
    if title_match:
        title = title_match.group(1).strip()
        body_html = re.sub(r'<h1>.*?</h1>', '', raw_text, count=1, flags=re.IGNORECASE | re.DOTALL).strip()
    else:
        title = "Trending Guide & Step by Step Strategy"
        body_html = raw_text

    print(f"✅ [Gemini Engine] Extracted Title: {title}")
    return title, body_html, selected_category


# ==========================================
# 6. SEO-OPTIMIZED LIGHTWEIGHT IMAGE ENGINE
# ==========================================
def get_featured_image(topic):
    print("🎨 [Image Engine] Generating SEO-optimized featured image URL...")
    prompt_encoded = urllib.parse.quote(f"hd cinematic concept photo of {topic}, professional lighting, studio quality, 8k resolution")
    
    proto = "https://"
    domain = "image.pollinations.ai/prompt/"
    clean_image_url = f"{proto}{domain}{prompt_encoded}?width=800&height=450&nologo=true"
    
    alt_text = re.sub(r'[^\w\s]', '', topic)

    return f'<p><img src="{clean_image_url}" alt="{alt_text}" title="{alt_text}" style="width:100%; height:auto; border-radius:8px; margin-bottom:20px;"></p>'


# ==========================================
# 7. GMAIL-TO-BLOGGER PUBLISHER ENGINE
# ==========================================
def publish_to_blogger(title, full_html):
    print("📧 [Blogger Engine] Publishing via Gmail Secret Address...")
    
    msg = MIMEText(full_html, 'html')
    msg['Subject'] = title
    msg['From'] = GMAIL_USER
    msg['To'] = BLOGGER_EMAIL

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.send_message(msg)
        print("✅ [Blogger Engine] Delivered to Blogger successfully!")
    except Exception as smtp_err:
        print(f"❌ [DEBUG] Gmail SMTP Exception: {smtp_err}")
        raise smtp_err


# ==========================================
# MAIN EXECUTION FLOW
# ==========================================
def main():
    print("🚀 [System] Starting Auto SEO Blog Publisher...")
    
    title, body_html, category_used = generate_blog_content()
    
    clean_text = re.sub(r'<[^>]*>', '', body_html)
    word_count = len(clean_text.split())
    read_time = max(1, math.ceil(word_count / 200))
    print(f"🔍 [DEBUG] Word Count: {word_count}, Read Time: {read_time} min")
    
    image_html = get_featured_image(title)
    badge_html = f'<p>⏱️ <i>Reading Time: ~{read_time} min</i> | 📌 <b>Category:</b> {category_used.split("(")[0].strip()}</p><hr>'
    
    final_content = image_html + badge_html + body_html
    
    publish_to_blogger(title, final_content)
    
    send_whatsapp_alert(title, read_time, category_used)
    
    print("🎉 [System] Daily SEO Post successfully processed!")

if __name__ == "__main__":
    main()
