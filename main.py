import os
import sys
import time
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# -------------------------------------------------------------
# 1. Environment Variables Verification
# -------------------------------------------------------------
print("==========================================")
print("🔍 [DEBUG] Step 1: Checking Environment Variables...")

GEMINI_KEY = os.environ.get("GEMINI_KEY")
GMAIL_USER = os.environ.get("GMAIL_USER")
GMAIL_PASS = os.environ.get("GMAIL_PASS")
BLOGGER_EMAIL = os.environ.get("BLOGGER_EMAIL")
WA_PHONE = os.environ.get("WA_PHONE")
TMB_KEY = os.environ.get("TMB_KEY")

print(f"👉 GEMINI_KEY Present: {bool(GEMINI_KEY)}")
print(f"👉 GMAIL_USER: {'***' if GMAIL_USER else 'Missing'}")
print(f"👉 GMAIL_PASS Present: {bool(GMAIL_PASS)}")
print(f"👉 BLOGGER_EMAIL: {'***' if BLOGGER_EMAIL else 'Missing'}")
print(f"👉 WA_PHONE: {'***' if WA_PHONE else 'Missing'}")
print(f"👉 TMB_KEY Present: {bool(TMB_KEY)}")
print("==========================================")

if not all([GEMINI_KEY, GMAIL_USER, GMAIL_PASS, BLOGGER_EMAIL]):
    print("❌ Error: Essential environment variables are missing!")
    sys.exit(1)


# -------------------------------------------------------------
# 2. Gemini Content Generation with Retry Logic & High Timeout
# -------------------------------------------------------------
def generate_blog_content():
    print("🚀 [System] Starting Auto SEO Blog Publisher...")
    print("🤖 [Gemini Engine] Generating High-Ranking SEO Blog Content...")
    
    category = "Finance & Personal Money Management (Investment, Budgeting, Crypto & Financial Literacy)"
    print(f"🎯 [DEBUG] Selected Sequence Category: {category}")
    print("🔍 [DEBUG] Sending request to Gemini API...")

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_KEY}"
    
    prompt = (
        f"Write a detailed, high-quality, SEO-optimized blog post in Hindi about {category}. "
        "Include an engaging title and structure the post using HTML tags like <h2>, <h3>, <p>, and <ul>."
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    
    headers = {"Content-Type": "application/json"}

    # Retry mechanism: 3 attempts with 120s timeout each
    max_retries = 3
    for attempt in range(1, max_retries + 1):
        try:
            print(f"⏳ Attempt {attempt}/{max_retries} to call Gemini API (Timeout: 120s)...")
            response = requests.post(url, json=payload, headers=headers, timeout=120)
            response.raise_for_status()
            
            data = response.json()
            generated_text = data["candidates"][0]["content"]["parts"][0]["text"]
            
            # Simple parsing logic (assumes title is on the first line or formatted)
            lines = generated_text.strip().split("\n")
            title = lines[0].replace("#", "").strip()
            body_html = "\n".join(lines[1:])
            
            return title, body_html, category

        except (requests.exceptions.ReadTimeout, requests.exceptions.ConnectionError) as e:
            print(f"⚠️ [Warning] Gemini API request timed out on attempt {attempt}: {e}")
            if attempt < max_retries:
                print("🔄 Retrying in 10 seconds...")
                time.sleep(10)
            else:
                print("❌ [Error] Gemini API failed after max retries due to timeout.")
                raise e
        except Exception as e:
            print(f"❌ [Error] Unexpected error during API call: {e}")
            raise e


# -------------------------------------------------------------
# 3. Publish Post via Email to Blogger
# -------------------------------------------------------------
def send_email_to_blogger(title, body_html):
    print("📧 Sending blog post to Blogger via Email...")
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = title
    msg["From"] = GMAIL_USER
    msg["To"] = BLOGGER_EMAIL

    html_part = MIMEText(body_html, "html")
    msg.attach(html_part)

    try:
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(GMAIL_USER, BLOGGER_EMAIL, msg.as_string())
        server.quit()
        print("✅ Blog post published successfully via Email!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        raise e


# -------------------------------------------------------------
# 4. Main Execution
# -------------------------------------------------------------
def main():
    try:
        title, body_html, category_used = generate_blog_content()
        send_email_to_blogger(title, body_html)
        print("🎉 Workflow Completed Successfully!")
    except Exception as e:
        print(f"💥 Script execution failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
