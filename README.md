<div align="center">

<img src="https://img.shields.io/badge/🦆-DuckAi-ff6d00?style=for-the-badge&labelColor=1a1a2e&logo=duckduckgo&logoColor=white" alt="DuckAi" width="100%"/>

# DuckAi

**Free unofficial CLI for DuckDuckGo AI Chat (duck.ai)**

No API key &nbsp;•&nbsp; No account &nbsp;•&nbsp; Chat &nbsp;•&nbsp; Images &nbsp;•&nbsp; Files &nbsp;•&nbsp; Live Voice

<br/>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Node.js 18+](https://img.shields.io/badge/Node.js-18%2B-339933?style=flat-square&logo=node.js&logoColor=white)](https://nodejs.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=flat-square)](#)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](#)

**🌐 Language / زبان:** &nbsp; [🇬🇧 English](#english) &nbsp;•&nbsp; [🇮🇷 فارسی](#farsi)

</div>

---

> [!WARNING]
> **Disclaimer:** This project is not affiliated with or endorsed by DuckDuckGo. It uses a private, undocumented endpoint and may stop working at any time. Use it for personal, educational purposes and respect DuckDuckGo's terms of service. Don't abuse the service.
>
> **سلب مسئولیت:** این پروژه به DuckDuckGo هیچ وابستگی یا تأییدی ندارد و از یک اندپوینت خصوصی و مستندنشده استفاده می‌کند؛ ممکن است هر زمان از کار بیفتد. فقط برای استفادهٔ شخصی و آموزشی باشد و قوانین DuckDuckGo رعایت شود.

---

<a id="english"></a>
## 🇬🇧 English

### ✨ Features

| | Feature | Description |
|---|---|---|
| 💬 | **Text chat** | Streaming answers with conversation memory |
| 🖼️ | **Image input** | Send JPG / PNG / WebP / BMP… — auto-converted to WebP |
| 📎 | **File attachments** | Inline `.py`, `.js`, `.json`, `.md`… as fenced code blocks |
| 🎨 | **Image generation** | Text → image, saved as JPEG |
| 🎙️ | **Dictation** | Microphone or any audio file → transcript |
| 📞 | **Live voice chat** | Real two-way WebRTC call with the AI |
| 🔀 | **6 free models** | GPT-6 Luna, GPT-5.4 Mini, Claude Haiku 5.5, Mistral, gpt-oss, Gemma 4 |
| 🌐 | **Proxy support** | HTTP and SOCKS5 |
| 🌍 | **Bilingual UI** | English (default) and Persian — `--lang fa` |

### 📦 Installation

**Prerequisites:** [Python 3.10+](https://www.python.org/downloads/) *(on Windows tick "Add to PATH")* and [Node.js 18+](https://nodejs.org/)

```bash
git clone https://github.com/DarkBytee/DuckAi.git
cd DuckAi

pip install -r requirements.txt     # core (requests, pillow)
npm install                          # jsdom — required
```

<details>
<summary>🎙️ <b>Optional — voice features</b> (dictation + live call)</summary>
<br/>

```bash
pip install -r requirements-voice.txt   # numpy, sounddevice, av, aiortc
```

> SOCKS5 proxy? Also run: `pip install "requests[socks]"`
</details>

### 🚀 Quick start

```bash
python duck_cli.py                     # interactive menu (easiest)
python duck_cli.py --ask "Hello!"      # one-off question
python duck_cli.py --chat              # continuous chat with memory
```

<details open>
<summary><b>📖 All usage examples</b></summary>
<br/>

**One-off question / with attachments**

```bash
python duck_cli.py --ask "What is in this picture?" --image photo.jpg
python duck_cli.py --ask "What does this code do?" --file main.py
```

**Generate an image**

```bash
python duck_cli.py --draw "a cute orange cat sitting on a windowsill"
```

**Voice**

```bash
python duck_cli.py --listen            # mic → text (Enter = stop)
python duck_cli.py --dictate clip.mp3  # audio file → text
python duck_cli.py --voice             # live two-way call 🎙
```

**Model / proxy / language**

```bash
python duck_cli.py --ask "hi" --model mini
python duck_cli.py --ask "hi" --proxy socks5://127.0.0.1:1080
python duck_cli.py --lang fa           # Persian UI
```

**In-chat commands**

| Command | Description |
|---|---|
| `/img photo.jpg` | Attach image(s) to the next message |
| `/file main.py` | Attach text/code file(s) |
| `/draw a starry sky` | Generate an image |
| `/model` | Switch model |
| `/mic` | Record → transcribe → send |
| `/live` | Live voice call (**use headphones!**) |
| `/clear` | Clear chat memory |
| `/exit` | Quit |

</details>

### 🤖 Free models

Mirrors duck.ai's own picker config — verified live:

| Shortcut | Model ID | Notes |
|:---:|---|---|
| `luna` | `gpt-6-luna` | free-tier default |
| `mini` | `gpt-5.4-mini` | faster, counts toward usage limits |
| `haiku` | `claude-haiku-5-5` | faster, counts toward usage limits |
| `mistral` | `mistral-small-2603` | |
| `oss` | `tinfoil/gpt-oss-120b` | open-source 120B |
| `gemma` | `tinfoil/gemma4-31b` | open-source Gemma 4 31B |

> 💡 Legacy ids (`gpt-5.6-luna`, `gpt-5.4-nano`, `claude-haiku-4-5`) still work — duck.ai auto-upgrades them.
> Paid-tier models (`gpt-5.6-terra`, `claude-sonnet-5-5`, `claude-opus-5-5`, `gpt-5.6-sol`) are rejected with `ERR_MODEL_RESTRICTED`.

### 🔧 How it works

1. `GET https://duck.ai/` → extracts `data-version-tag` / `data-version-sha` → `x-fe-version`
2. `GET /duckchat/v1/status` (`x-vqd-accept: 1`) → `x-vqd-hash-1` = base64 JS challenge
3. Challenge is solved locally with **Node.js + jsdom** — no real browser needed
4. Solution is packaged into the final `x-vqd-hash-1` proof
5. `POST /duckchat/v1/chat` streams the answer back as **SSE**

<details>
<summary><b>🎙 Voice protocol (WebRTC)</b></summary>
<br/>

`GET /duckchat/v1/ice-servers` → TURN servers → `POST /duckchat/v1/session` (offer/answer SDP, Opus, server-side VAD) → events flow over the `duckai-voice-session` datachannel.
</details>

### 🐞 Troubleshooting

| Problem | Fix |
|---|---|
| `Node.js was not found on PATH` | Install from [nodejs.org](https://nodejs.org), reopen the terminal |
| `The 'jsdom' package is missing` | Run `npm install` inside the project folder |
| `HTTP 403` / `No challenge received` | IP rate-limited — wait, or use `--proxy` |
| Broken Persian text on Windows | Run `chcp 65001` first, or use Windows Terminal |
| Live voice hears itself | Wear headphones — echo confuses the server-side VAD |
| `ERR_MODEL_RESTRICTED` | That model needs a paid tier — use a free one |

---

<div align="center">

## 🇮🇷 فارسی

</div>

<a id="farsi"></a>

### ✨ امکانات

| | قابلیت | توضیح |
|---|---|---|
| 💬 | **گفتگوی متنی** | پاسخ استریمی با حافظهٔ گفتگو |
| 🖼️ | **ارسال تصویر** | JPG / PNG / WebP / BMP… — خودکار به WebP تبدیل می‌شود |
| 📎 | **پیوست فایل** | فایل‌های `.py`، `.js`، `.json`، `.md` و… داخل پرامپت |
| 🎨 | **تولید تصویر** | متن → تصویر، ذخیره به‌صورت JPEG |
| 🎙️ | **دیکته** | میکروفون یا هر فایل صوتی → متن |
| 📞 | **گفتگوی زندهٔ صوتی** | تماس دوطرفهٔ واقعی WebRTC با هوش مصنوعی |
| 🔀 | **۶ مدل رایگان** | GPT-6 Luna، GPT-5.4 Mini، Claude Haiku 5.5، Mistral، gpt-oss، Gemma 4 |
| 🌐 | **پروکسی** | HTTP و SOCKS5 |
| 🌍 | **رابط دوزبانه** | انگلیسی (پیش‌فرض) و فارسی — `--lang fa` |

### 📦 نصب

**پیش‌نیازها:** [Python 3.10+](https://www.python.org/downloads/) *(در ویندوز تیک Add to PATH را بزنید)* و [Node.js 18+](https://nodejs.org/)

```bash
git clone https://github.com/DarkBytee/DuckAi.git
cd DuckAi

pip install -r requirements.txt     # پکیج‌های اصلی
npm install                          # jsdom — ضروری
```

<details>
<summary>🎙️ <b>اختیاری — قابلیت‌های صوتی</b> (دیکته + تماس زنده)</summary>
<br/>

```bash
pip install -r requirements-voice.txt   # numpy, sounddevice, av, aiortc
```

> پروکسی SOCKS5 دارید؟ این را هم بزنید: `pip install "requests[socks]"`
</details>

### 🚀 شروع سریع

```bash
python duck_cli.py                     # منوی تعاملی (ساده‌ترین)
python duck_cli.py --ask "سلام!"       # یک سؤال تک‌باره
python duck_cli.py --chat              # گفتگوی پیوسته با حافظه
```

<details open>
<summary><b>📖 همهٔ مثال‌های استفاده</b></summary>
<br/>

**سؤال تک‌باره / با پیوست**

```bash
python duck_cli.py --ask "تو این عکس چیه؟" --image photo.jpg
python duck_cli.py --ask "این کد چه‌کار می‌کند؟" --file main.py
```

**تولید تصویر**

```bash
python duck_cli.py --draw "یک گربهٔ نارنجی بامزه روی طاقچه"
```

**صدا**

```bash
python duck_cli.py --listen            # میکروفون ← متن (Enter = پایان)
python duck_cli.py --dictate clip.mp3  # فایل صوتی ← متن
python duck_cli.py --voice             # تماس زندهٔ دوطرفه 🎙
```

**مدل / پروکسی / زبان**

```bash
python duck_cli.py --ask "سلام" --model mini
python duck_cli.py --ask "سلام" --proxy socks5://127.0.0.1:1080
python duck_cli.py --lang fa           # رابط فارسی
```

**دستورهای داخل گفتگو**

| دستور | توضیح |
|---|---|
| `/img عکس.jpg` | پیوست تصویر به پیام بعدی |
| `/file main.py` | پیوست فایل متنی/کد |
| `/draw آسمان پرستاره` | تولید تصویر |
| `/model` | تغییر مدل |
| `/mic` | ضبط ← تبدیل به متن ← ارسال |
| `/live` | تماس زندهٔ صوتی (**هندزفری بزنید!**) |
| `/clear` | پاک‌کردن حافظهٔ گفتگو |
| `/exit` | خروج |

</details>

### 🤖 مدل‌های رایگان

مطابق کانفیگ خود duck.ai — به‌صورت زنده تست‌شده:

| میان‌بر | شناسه مدل | توضیح |
|:---:|---|---|
| `luna` | `gpt-6-luna` | پیش‌فرض سطح رایگان |
| `mini` | `gpt-5.4-mini` | سریع‌تر، از سهمیه مصرف می‌گذرد |
| `haiku` | `claude-haiku-5-5` | سریع‌تر، از سهمیه مصرف می‌گذرد |
| `mistral` | `mistral-small-2603` | |
| `oss` | `tinfoil/gpt-oss-120b` | متن‌باز ۱۲۰ میلیارد پارامتری |
| `gemma` | `tinfoil/gemma4-31b` | متن‌باز Gemma 4 نسخهٔ 31B |

> 💡 شناسه‌های قدیمی (`gpt-5.6-luna`، `gpt-5.4-nano`، `claude-haiku-4-5`) هنوز کار می‌کنند — سرور خودش ارتقایشان می‌دهد.
> مدل‌های پولی (`gpt-5.6-terra`، `claude-sonnet-5-5`، `claude-opus-5-5`، `gpt-5.6-sol`) با خطای `ERR_MODEL_RESTRICTED` رد می‌شوند.

### 🔧 چطور کار می‌کند

1. `GET https://duck.ai/` ← استخراج `data-version-tag` / `data-version-sha` ← `x-fe-version`
2. `GET /duckchat/v1/status` (`x-vqd-accept: 1`) ← `x-vqd-hash-1` = چالش JS کدشده با base64
3. چالش محلی با **Node.js + jsdom** حل می‌شود — بدون مرورگر واقعی
4. جواب چالش در قالب نهایی `x-vqd-hash-1` بسته‌بندی می‌شود
5. `POST /duckchat/v1/chat` پاسخ را به‌صورت رویدادهای **SSE** استریم می‌کند

<details>
<summary><b>🎙 پروتکل صدا (WebRTC)</b></summary>
<br/>

`GET /duckchat/v1/ice-servers` ← سرورهای TURN ← `POST /duckchat/v1/session` (offer/answer SDP، کدک Opus، VAD سمت سرور) ← رویدادها روی datachannel به نام `duckai-voice-session` برمی‌گردند.
</details>

### 🐞 رفع اشکال

| مشکل | راه‌حل |
|---|---|
| `Node.js was not found on PATH` | از [nodejs.org](https://nodejs.org) نصب کنید و ترمینال را دوباره باز کنید |
| `The 'jsdom' package is missing` | داخل پوشهٔ پروژه `npm install` را اجرا کنید |
| `HTTP 403` / `No challenge received` | IP محدود شده — صبر کنید یا `--proxy` بدهید |
| متن فارسی به‌هم‌ریخته در ویندوز | اول `chcp 65001` را بزنید یا از Windows Terminal استفاده کنید |
| ویس زنده صدای خودش را می‌شنود | هندزفری بزنید — اکو VAD سرور را گمراه می‌کند |
| `ERR_MODEL_RESTRICTED` | آن مدل مخصوص اشتراک پولی است — از مدل‌های رایگان استفاده کنید |

---

<div align="center">

**🦆 DuckAi** — Built with ❤️ for free AI access

MIT License · Use responsibly

⭐ Star the repo if it helped you!

</div>
