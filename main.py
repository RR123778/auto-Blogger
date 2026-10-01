import os
import sys
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google import genai

def main():
    # ==========================================
    # Step 1: Checking Environment Variables
    # ==========================================
    gemini_key = os.getenv("GEMINI_KEY")
    gmail_user = os.getenv("GMAIL_USER")
    gmail_pass = os.getenv("GMAIL_PASS")
    blogger_email = os.getenv("BLOGGER_EMAIL")
    wa_phone = os.getenv("WA_PHONE")
    tmb_key = os.getenv("TMB_KEY")
    blog_lang = os.getenv("BLOG_LANG", "HINDI")

    print("==========================================")
    print("🔍 [DEBUG] Step 1: Checking Environment Variables...")
    print(f"👉 GEMINI_KEY Present: {bool(gemini_key)}")
    print(f"👉 GMAIL_USER: {'***' if gmail_user else 'None'}")
    print(f"👉 GMAIL_PASS Present: {bool(gmail_pass)}")
    print(f"👉 BLOGGER_EMAIL: {'***' if blogger_email else 'None'}")
    print(f"👉 WA_PHONE: {'***' if wa_phone else 'None'}")
    print(f"👉 TMB_KEY Present: {bool(tmb_key)}")
    print("==========================================")

    if not gemini_key:
        print("❌ [Error] GEMINI_KEY missing!")
        sys.exit(1)

    print("🚀 [System] Starting Auto SEO Blog Publisher...")
    print("🤖 [Gemini Engine] Generating High-Ranking SEO Blog Content...")
    
    selected_category = "Finance & Personal Money Management (Investment, Budgeting, Crypto & Financial Literacy)"
    print(f"🎯 [DEBUG] Selected Sequence Category: {selected_category}")
    print("🔍 [DEBUG] Sending request to Gemini API...")

    # ==========================================
    # Step 2: Content Generation with Gemini 2.5 Flash
    # ==========================================
    try:
        client = genai.Client(api_key=gemini_key)

        prompt = f"""
        Write a high-ranking, SEO-optimized blog post on the topic category: '{selected_category}'.
        Language: {blog_lang}
        
        Return the result strictly as JSON with these keys:
        1. "title": A compelling SEO-friendly title.
        2. "body": Full article in clean HTML standard formatting (use <h2>, <h3>, <p>, <ul>, <li>).
        """

        print("⏳ Attempt 1/3 to call Gemini API (Timeout: 120s)...")
        
        # Fixed Model Name: gemini-2.5-flash
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )

        content_json = json.loads(response.text)
        post_title = content_json.get("title")
        post_body = content_json.get("body")

        print("✅ [Success] Generated content successfully!")
        print(f"📌 Post Title: {post_title}")

    except Exception as e:
        print(f"💥 Script execution failed: {e}")
        sys.exit(1)

    # ==========================================
    # Step 3: Publish via Email to Blogger (Email-to-Blog)
    # ==========================================
    if gmail_user and gmail_pass and blogger_email:
        try:
            print("✉️ [Blogger] Sending email post to Blogger Secret Email...")
            
            msg = MIMEMultipart()
            msg['From'] = gmail_user
            msg['To'] = blogger_email
            msg['Subject'] = post_title

            msg.attach(MIMEText(post_body, 'html'))

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(gmail_user, gmail_pass)
            server.send_message(msg)
            server.quit()

            print("🎉 [Success] Published to Blogger via Email!")

        except Exception as e:
            print(f"⚠️ [Warning] Failed to send email to Blogger: {e}")
    else:
        print("ℹ️ Skipping email publishing (GMAIL credentials or BLOGGER_EMAIL not fully provided).")

    print("==========================================")
    print("Process completed successfully.")

if __name__ == "__main__":
    main()
