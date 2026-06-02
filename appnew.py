"""
Marketing Email Editor — Streamlit App
Based on the Software Requirements Specification for a Marketing Email Editor Demo.

Requirements:
    pip install streamlit jinja2

Optional (rich text editor):
    pip install streamlit-quill

Run:
    streamlit run email_editor.py
"""

import base64
import smtplib
import streamlit as st
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Marketing Email Editor",
    page_icon="✉️",
    layout="wide",
)

# ── Jinja2 HTML template ──────────────────────────────────────────────────────
EMAIL_TEMPLATE = Template("""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{{ subject }}</title>
</head>
<body style="margin:0;padding:0;background:#f4f4f4;font-family:Arial,Helvetica,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f4;padding:32px 0;">
  <tr><td align="center">
    <table width="600" cellpadding="0" cellspacing="0"
           style="background:#ffffff;border-radius:8px;overflow:hidden;max-width:600px;width:100%;">

      <!-- HEADER -->
      <tr>
        <td style="background:{{ header_bg }};padding:28px 32px;">
          {% if logo_b64 %}
            <img src="{{ logo_b64 }}" alt="{{ brand_name }}"
                 style="max-height:54px;max-width:180px;object-fit:contain;display:block;">
          {% else %}
            <span style="font-size:24px;font-weight:700;color:#ffffff;
                         letter-spacing:-0.5px;">{{ brand_name }}</span>
          {% endif %}
        </td>
      </tr>

      <!-- BANNER IMAGE (optional) -->
      {% if banner_b64 %}
      <tr>
        <td style="padding:0;">
          <img src="{{ banner_b64 }}" alt="Banner"
               style="width:100%;display:block;max-height:280px;object-fit:cover;">
        </td>
      </tr>
      {% endif %}

      <!-- BODY -->
      <tr>
        <td style="padding:36px 32px 24px;">
          <h1 style="margin:0 0 20px;font-size:26px;font-weight:700;
                     color:#111111;line-height:1.3;">{{ subject }}</h1>
          <div style="font-size:16px;line-height:1.7;color:#333333;">
            {{ body_html }}
          </div>

          <!-- CTA BUTTON -->
          {% if cta_text and cta_url %}
          <table cellpadding="0" cellspacing="0" style="margin:28px 0 0;">
            <tr>
              <td style="border-radius:6px;background:{{ cta_bg }};">
                <a href="{{ cta_url }}"
                   style="display:inline-block;padding:14px 32px;font-size:15px;
                          font-weight:700;color:#ffffff;text-decoration:none;
                          border-radius:6px;">{{ cta_text }}</a>
              </td>
            </tr>
          </table>
          {% endif %}
        </td>
      </tr>

      <!-- FOOTER -->
      <tr>
        <td style="background:#f9f9f9;border-top:1px solid #eeeeee;
                   padding:20px 32px;text-align:center;">
          <p style="margin:0;font-size:13px;color:#888888;line-height:1.6;">
            {{ address }}
          </p>
          <p style="margin:6px 0 0;font-size:12px;color:#aaaaaa;">
            {{ copyright_text }}
          </p>
          {% if include_unsubscribe and unsubscribe_url %}
          <p style="margin:6px 0 0;font-size:12px;">
            <a href="{{ unsubscribe_url }}"
               style="color:#aaaaaa;text-decoration:underline;">Unsubscribe</a>
          </p>
          {% endif %}
        </td>
      </tr>

    </table>
  </td></tr>
</table>
</body>
</html>""")


# ── Helper: image → base64 data URI ──────────────────────────────────────────
def to_data_uri(uploaded_file) -> str | None:
    """Convert a Streamlit UploadedFile to a base64 data URI."""
    if uploaded_file is None:
        return None
    mime = uploaded_file.type  # e.g. "image/png"
    b64 = base64.b64encode(uploaded_file.read()).decode("utf-8")
    return f"data:{mime};base64,{b64}"


# ── Helper: plain text → HTML paragraphs ─────────────────────────────────────
def text_to_html(text: str) -> str:
    """Convert newline-separated text to <p> tags."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    return "".join(
        f'<p style="margin:0 0 16px;">'
        + p.replace("\n", "<br>")
        + "</p>"
        for p in paragraphs
    )


# ── Helper: send test email via smtplib ──────────────────────────────────────
def send_test_email(
    smtp_host: str,
    smtp_port: int,
    smtp_user: str,
    smtp_pass: str,
    from_addr: str,
    to_addr: str,
    subject: str,
    html_body: str,
) -> tuple[bool, str]:
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = from_addr
        msg["To"] = to_addr
        msg.attach(MIMEText(html_body, "html"))
        with smtplib.SMTP(smtp_host, smtp_port, timeout=10) as server:
            server.ehlo()
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.sendmail(from_addr, [to_addr], msg.as_string())
        return True, "✅ Test email sent successfully."
    except Exception as exc:
        return False, f"❌ Failed to send: {exc}"


# ── Sidebar: all editor controls ─────────────────────────────────────────────
with st.sidebar:
    st.title("✉️ Email Builder")

    # ── Component A: Header ────────────────────────────────────────────────
    with st.expander("🏷 Header", expanded=True):
        brand_name = st.text_input("Company / brand name", value="Acme Co.")
        header_bg  = st.color_picker("Header background color", value="#1a1a2e")
        logo_file  = st.file_uploader(
            "Brand logo", type=["png", "jpg", "jpeg", "gif"], key="logo"
        )

    # ── Component A: Body ─────────────────────────────────────────────────
    with st.expander("📝 Body content", expanded=True):
        subject = st.text_input(
            "Subject line",
            value="Introducing our biggest sale yet 🎉",
        )
        body_text = st.text_area(
            "Main message",
            height=160,
            value=(
                "Hi there,\n\n"
                "We're thrilled to announce our biggest sale of the year. "
                "For a limited time, enjoy exclusive discounts across our entire catalog.\n\n"
                "Don't miss out — this offer expires soon!"
            ),
        )
        banner_file = st.file_uploader(
            "Marketing banner image",
            type=["png", "jpg", "jpeg", "gif"],
            key="banner",
        )

    # ── Component B: CTA button ───────────────────────────────────────────
    with st.expander("🔗 Call to action", expanded=True):
        cta_text = st.text_input("Button text", value="Shop now")
        cta_url  = st.text_input("Button URL",  value="https://example.com")
        cta_bg   = st.color_picker("Button color", value="#e63946")

    # ── Component A: Footer ───────────────────────────────────────────────
    with st.expander("📋 Footer", expanded=True):
        address        = st.text_input(
            "Company address",
            value="123 Main Street, New York, NY 10001",
        )
        copyright_text = st.text_input(
            "Copyright text",
            value="© 2025 Acme Co. All rights reserved.",
        )
        include_unsubscribe = st.checkbox(
            "Include unsubscribe link (GDPR)", value=True
        )
        unsubscribe_url = ""
        if include_unsubscribe:
            unsubscribe_url = st.text_input(
                "Unsubscribe URL",
                value="https://example.com/unsubscribe",
            )

    # ── Optional: test send ───────────────────────────────────────────────
    with st.expander("📤 Send test email (optional)", expanded=False):
        smtp_host = st.text_input("SMTP host",     value="smtp.gmail.com")
        smtp_port = st.number_input("SMTP port",   value=587, step=1)
        smtp_user = st.text_input("SMTP username", value="")
        smtp_pass = st.text_input("SMTP password", type="password", value="")
        from_addr = st.text_input("From address",  value="")
        to_addr   = st.text_input("Test receiver email", value="")
        send_btn  = st.button("Send test ✉️", use_container_width=True)


# ── Compile images to base64 ──────────────────────────────────────────────────
logo_b64   = to_data_uri(logo_file)
banner_b64 = to_data_uri(banner_file)

# ── Compile HTML via Jinja2 ───────────────────────────────────────────────────
compiled_html = EMAIL_TEMPLATE.render(
    brand_name          = brand_name,
    header_bg           = header_bg,
    logo_b64            = logo_b64,
    banner_b64          = banner_b64,
    subject             = subject,
    body_html           = text_to_html(body_text),
    cta_text            = cta_text,
    cta_url             = cta_url,
    cta_bg              = cta_bg,
    address             = address,
    copyright_text      = copyright_text,
    include_unsubscribe = include_unsubscribe,
    unsubscribe_url     = unsubscribe_url,
)

# ── Main area: preview + export ───────────────────────────────────────────────
st.subheader("Live preview")

tab_preview, tab_code = st.tabs(["📧 Visual", "🗒 HTML source"])

with tab_preview:
    st.components.v1.html(compiled_html, height=700, scrolling=True)

with tab_code:
    st.code(compiled_html, language="html")

# ── Export button ─────────────────────────────────────────────────────────────
st.download_button(
    label     = "⬇️ Download HTML file",
    data      = compiled_html,
    file_name = "marketing_email.html",
    mime      = "text/html",
    use_container_width=True,
)

# ── Handle test send ──────────────────────────────────────────────────────────
if send_btn:
    if not all([smtp_host, smtp_user, smtp_pass, from_addr, to_addr]):
        st.warning("Please fill in all SMTP fields before sending.")
    else:
        with st.spinner("Sending…"):
            ok, msg = send_test_email(
                smtp_host=smtp_host,
                smtp_port=int(smtp_port),
                smtp_user=smtp_user,
                smtp_pass=smtp_pass,
                from_addr=from_addr,
                to_addr=to_addr,
                subject=subject,
                html_body=compiled_html,
            )
        if ok:
            st.success(msg)
        else:
            st.error(msg)