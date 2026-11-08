<div align="center">

<img src="https://img.shields.io/badge/DuckAi-ff6d00?style=for-the-badge&labelColor=1a1a2e&logo=duckduckgo&logoColor=white" alt="DuckAi" width="100%"/>

# DuckAi

### *DuckDuckGo AI Chat, straight from your terminal — completely free.*

**No API key&nbsp;&nbsp;·&nbsp;&nbsp;No account&nbsp;&nbsp;·&nbsp;&nbsp;No subscription**

Chat&nbsp;&nbsp;💬&nbsp;&nbsp;·&nbsp;&nbsp;Image input&nbsp;&nbsp;🖼️&nbsp;&nbsp;·&nbsp;&nbsp;Image generation&nbsp;&nbsp;🎨&nbsp;&nbsp;·&nbsp;&nbsp;File attachments&nbsp;&nbsp;📎&nbsp;&nbsp;·&nbsp;&nbsp;Live voice calls&nbsp;&nbsp;📞

<br/>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Node.js 18+](https://img.shields.io/badge/Node.js-18%2B-339933?style=for-the-badge&logo=node.js&logoColor=white)](https://nodejs.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-c0c4cc?style=for-the-badge)](#)
[![Stars](https://img.shields.io/badge/%E2%AD%90-Star-it!-ffd700?style=for-the-badge)](#)

**🌐 Language / زبان:**&nbsp;&nbsp;[**English**](#english)&nbsp;&nbsp;·&nbsp;&nbsp;[**فارسی**](#farsi)

</div>

> [!WARNING]
> **English:** This project is not affiliated with or endorsed by DuckDuckGo. It talks to a private, undocumented endpoint and may stop working at any time. Use it for personal, educational purposes, respect DuckDuckGo's terms of service, and don't abuse the service.
>
> **فارسی:** این پروژه به DuckDuckGo هیچ وابستگی یا تأییدی ندارد و با یک اندپوینت خصوصی و مستندنشده صحبت می‌کند؛ ممکن است هر زمان از کار بیفتد. فقط برای استفادهٔ شخصی و آموزشی باشد، قوانین DuckDuckGo رعایت شود و از سرویس سوءاستفاده نشود.

---

<a id="english"></a>

## 🇬🇧 English

DuckAi is a small Python CLI that gives you the **same AI chat you get on duck.ai — in your terminal, for free**. It reverse-engineers the browser handshake (solves the anti-abuse challenge locally with Node.js + jsdom), then streams answers, images and even **live two-way voice calls** straight to your console.

### ✨ Features

| | Feature | Description |
|:---:|---|---|
| 💬 | **Streaming chat** | Real-time token streaming with conversation memory |
| 🖼️ | **Image input** | JPG / PNG / WebP / BMP / GIF… — auto-converted to WebP, auto-resized |
| 📎 | **File attachments** | Source files (`.py`, `.js`, `.json`, `.md`…) inlined into the prompt |
| 🎨 | **Image generation** | Text → image, saved as JPEG with live progress |
| 🎙️ | **Dictation** | Microphone **or any audio file** → accurate transcript |
| 📞 | **Live voice call** | Full WebRTC call with the AI — you talk, it talks back |
| 🔀 | **6 free models** | GPT-6 Luna · GPT-5.4 Mini · Claude Haiku 5.5 · Mistral · gpt-oss · Gemma 4 |
| 🌐 | **Proxy support** | HTTP and SOCKS5 (`--proxy`) |
| 🌍 | **Bilingual UI** | English (default) + Persian — `--lang fa` |

---

### 📦 Installation

> [!IMPORTANT]
> **Prerequisites:** [Python 3.10+](https://www.python.org/downloads/) *(on Windows tick **"Add python.exe to PATH"** during install)* and [Node.js 18+](https://nodejs.org/) — Node is required to solve duck.ai's JS challenge.

```bash
git clone https://github.com/DarkBytee/DuckAi.git
cd DuckAi

pip install -r requirements.txt      # core: requests + pillow
npm install                          # jsdom — required
```

<details>
<summary>🎙️ <b>Optional — enable the voice features</b> (dictation + live call)</summary>
<br/>

```bash
pip install -r requirements-voice.txt   # numpy, sounddevice, av, aiortc
```

> [!TIP]
> Using a **SOCKS5** proxy? Also run: `pip install "requests[socks]"`
</details>

---

### 🚀 Quick start

```bash
python duck_cli.py
```

That's it — an interactive menu walks you through everything:

<p align="center">
  <img src="screenshots/menu.png" width="700" alt="DuckAi interactive menu"/>
</p>

---

#### 💬 Ask a one-off question

```bash
python duck_cli.py --ask "What is DuckDuckGo? Answer in one short sentence."
```

Streamed answer, straight to your terminal:

<p align="center">
  <img src="screenshots/chat.png" width="700" alt="One-off question with streaming answer"/>
</p>

Add context with **images** or **files**:

```bash
python duck_cli.py --ask "What is in this picture?" --image photo.jpg
python duck_cli.py --ask "What does this code do?" --file main.py
python duck_cli.py --ask "Review these files" --image shot.png --image logo.webp --file app.py utils.py
```

#### 💬 Continuous chat with memory

```bash
python duck_cli.py --chat
```

| Command | Description |
|---|---|
| `/img photo.jpg` | Attach image(s) to your next message |
| `/file main.py` | Attach text/code file(s) |
| `/draw a starry sky` | Generate an image |
| `/model` | Switch model mid-chat |
| `/mic` | Record → transcribe → send |
| `/live` | Live voice call (**use headphones!**) |
| `/clear` | Clear chat memory |
| `/exit` or empty Enter | Quit |

#### 🎨 Generate images

```bash
python duck_cli.py --draw "a cute orange duck mascot wearing headphones, flat vector style"
```

<p align="center">
  <img src="screenshots/draw.png" width="700" alt="Image generation in the terminal"/>
  <br/><br/>
  <img src="screenshots/sample-image.jpg" width="380" alt="Generated image sample — a duck mascot"/>
  <br/>
  <sup>↑ Real output of that exact command — a real duck, apparently 🦆</sup>
</p>

Generated images are saved as JPEG in the current folder (or `--out some/folder`).

#### 📞 Live voice call

```bash
python duck_cli.py --voice
```

A real two-way WebRTC call: the server detects when you stop talking (server-side VAD), transcribes your speech, answers with a real voice — and you see the full transcript in the console. You can even feed it an audio file instead of your microphone.

<p align="center">
  <img src="screenshots/voice.png" width="640" alt="Live WebRTC voice call transcript"/>
</p>

> [!TIP]
> Wear headphones during live calls — speaker echo confuses the voice-activity detection.

Other voice modes:

```bash
python duck_cli.py --listen             # mic → text (Enter = stop)
python duck_cli.py --dictate clip.mp3   # any audio file → text (wav/mp3/m4a/webm…)
```

#### 🤖 Switch models

```bash
python duck_cli.py --ask "hi" --model mini
```

**All six current free models** (mirrors duck.ai's own picker config, verified live):

| Shortcut | Model ID | Notes |
|:---:|---|---|
| `luna` | `gpt-6-luna` | free-tier default |
| `mini` | `gpt-5.4-mini` | faster, counts toward usage limits |
| `haiku` | `claude-haiku-5-5` | faster, counts toward usage limits |
| `mistral` | `mistral-small-2603` | |
| `oss` | `tinfoil/gpt-oss-120b` | open-source 120B |
| `gemma` | `tinfoil/gemma4-31b` | open-source Gemma 4 31B |

<p align="center">
  <img src="screenshots/models.png" width="620" alt="Model picker with all free models"/>
</p>

> [!NOTE]
> Legacy ids (`gpt-5.6-luna`, `gpt-5.4-nano`, `claude-haiku-4-5`) still work — duck.ai auto-upgrades them to their replacements.
> Paid-tier models (`gpt-5.6-terra`, `claude-sonnet-5-5`, `claude-opus-5-5`, `gpt-5.6-sol`) are rejected by the server with `ERR_MODEL_RESTRICTED` without a subscription.

#### 🌐 Proxy & language

```bash
python duck_cli.py --ask "hi" --proxy http://127.0.0.1:8080
python duck_cli.py --ask "hi" --proxy socks5://127.0.0.1:1080
python duck_cli.py --lang fa             # Persian UI (or: setx DUCKAI_LANG fa)
```

---

### 🔧 How it works

1. `GET https://duck.ai/` → extracts `data-version-tag` / `data-version-sha` → builds `x-fe-version`
2. `GET /duckchat/v1/status` (header `x-vqd-accept: 1`) → returns `x-vqd-hash-1`: a base64-encoded **JS challenge**
3. The challenge is solved **locally** with Node.js + jsdom (`jsa_jsdom.js`) — no real browser needed
4. The solution is packaged into the final `x-vqd-hash-1` proof (`client_hashes` = base64 of sha256)
5. `POST /duckchat/v1/chat` streams the answer back as **SSE** events

<details>
<summary><b>🎙 Voice protocol (WebRTC)</b></summary>
<br/>

`GET /duckchat/v1/ice-servers` → TURN servers → `POST /duckchat/v1/session` (offer/answer SDP, Opus audio) → your speech is transcribed server-side (VAD) and events flow over the `duckai-voice-session` datachannel: `input_audio_buffer.speech_*`, `response.output_audio_transcript.delta`, `output_audio_buffer.started/stopped`…
</details>

<details>
<summary><b>📁 Project layout</b></summary>
<br/>

```
DuckAi/
├── duck_cli.py              # main CLI: chat, images, files, image generation
├── duck_voice.py            # dictation + live WebRTC voice session
├── duck_i18n.py             # English/Persian UI strings
├── jsa_jsdom.js             # Node runner that solves the duck.ai challenge
├── requirements.txt         # core Python deps
├── requirements-voice.txt   # optional voice deps
├── package.json             # Node deps (jsdom)
└── screenshots/             # real CLI captures used in this README
```
</details>

### 🐞 Troubleshooting

| Problem | Fix |
|---|---|
| `Node.js was not found on PATH` | Install from [nodejs.org](https://nodejs.org), reopen the terminal |
| `The 'jsdom' package is missing` | Run `npm install` **inside the project folder** |
| `HTTP 403` / `No challenge received` | IP rate-limited — wait a bit, or use `--proxy` |
| `HTTP 418` repeatedly | duck.ai anti-abuse score — usually auto-recovers with a fresh challenge |
| Broken Persian text on Windows | Run `chcp 65001` first, or use Windows Terminal |
| `ERR_MODEL_RESTRICTED` | That model needs a paid tier — pick one of the six free ones |
| Microphone errors | `pip install -r requirements-voice.txt` |

---

<div align="center">

## 🇮🇷 فارسی

<a id="farsi"></a>

</div>

DuckAi یک ابزار خط فرمان کوچک پایتون است که **همان چت هوش مصنوعی duck.ai را — در ترمینال و به‌صورت کاملاً رایگان** در اختیارتان می‌گذارد. هندشیک مرورگر را به‌صورت معکوس بازسازی می‌کند (چالش ضد سوءاستفاده را محلی با Node.js + jsdom حل می‌کند)، بعد پاسخ‌ها، تصاویر و حتی **تماس زندهٔ صوتی دوطرفه** را مستقیم به کنسول استریم می‌کند.

### ✨ امکانات

| | قابلیت | توضیح |
|:---:|---|---|
| 💬 | **گفتگوی استریمی** | پاسخ لحظه‌ای با حافظهٔ گفتگو |
| 🖼️ | **ورودی تصویر** | JPG / PNG / WebP / BMP / GIF… — خودکار به WebP تبدیل و کوچک می‌شود |
| 📎 | **پیوست فایل** | فایل‌های کد (`.py`، `.js`، `.json`، `.md` و…) داخل پرامپت |
| 🎨 | **تولید تصویر** | متن → تصویر، ذخیرهٔ JPEG با پیشرفت زنده |
| 🎙️ | **دیکته** | میکروفون **یا هر فایل صوتی** → متن دقیق |
| 📞 | **تماس زندهٔ صوتی** | تماس کامل WebRTC — شما حرف می‌زنید، جواب صوتی می‌گیرید |
| 🔀 | **۶ مدل رایگان** | GPT-6 Luna · GPT-5.4 Mini · Claude Haiku 5.5 · Mistral · gpt-oss · Gemma 4 |
| 🌐 | **پروکسی** | HTTP و SOCKS5 (`--proxy`) |
| 🌍 | **رابط دوزبانه** | انگلیسی (پیش‌فرض) + فارسی — `--lang fa` |

---

### 📦 نصب

> [!IMPORTANT]
> **پیش‌نیازها:** [Python 3.10+](https://www.python.org/downloads/) *(در ویندوز حین نصب تیک **Add python.exe to PATH** را بزنید)* و [Node.js 18+](https://nodejs.org/) — Node برای حل چالش جاوااسکریپتی duck.ai لازم است.

```bash
git clone https://github.com/DarkBytee/DuckAi.git
cd DuckAi

pip install -r requirements.txt      # پکیج‌های اصلی: requests + pillow
npm install                          # jsdom — ضروری
```

<details>
<summary>🎙️ <b>اختیاری — فعال‌سازی قابلیت‌های صوتی</b> (دیکته + تماس زنده)</summary>
<br/>

```bash
pip install -r requirements-voice.txt   # numpy, sounddevice, av, aiortc
```

> [!TIP]
> از پروکسی **SOCKS5** استفاده می‌کنید؟ این را هم بزنید: `pip install "requests[socks]"`
</details>

---

### 🚀 شروع سریع

```bash
python duck_cli.py
```

همین! یک منوی تعاملی همه‌چیز را قدم‌به‌قدم نشان می‌دهد:

<p align="center">
  <img src="screenshots/menu.png" width="700" alt="منوی تعاملی DuckAi"/>
</p>

---

#### 💬 پرسیدن یک سؤال تک‌باره

```bash
python duck_cli.py --ask "DuckDuckGo چیست؟ در یک جمله کوتاه بگو."
```

پاسخ استریمی، مستقیم در ترمینال:

<p align="center">
  <img src="screenshots/chat.png" width="700" alt="سؤال تک‌باره با پاسخ استریمی"/>
</p>

افزودن زمینه با **تصویر** یا **فایل**:

```bash
python duck_cli.py --ask "تو این عکس چیه؟" --image photo.jpg
python duck_cli.py --ask "این کد چه‌کار می‌کند؟" --file main.py
python duck_cli.py --ask "این فایل‌ها را بررسی کن" --image shot.png --file app.py utils.py
```

#### 💬 گفتگوی پیوسته با حافظه

```bash
python duck_cli.py --chat
```

| دستور | توضیح |
|---|---|
| `/img عکس.jpg` | پیوست تصویر به پیام بعدی |
| `/file main.py` | پیوست فایل متنی/کد |
| `/draw آسمان پرستاره` | تولید تصویر |
| `/model` | تغییر مدل وسط گفتگو |
| `/mic` | ضبط ← تبدیل به متن ← ارسال |
| `/live` | تماس زندهٔ صوتی (**هندزفری بزنید!**) |
| `/clear` | پاک‌کردن حافظهٔ گفتگو |
| `/exit` یا Enter خالی | خروج |

#### 🎨 تولید تصویر

```bash
python duck_cli.py --draw "یک اردک نارنجی بامزه با هدفون، سبک وکتور فلت"
```

<p align="center">
  <img src="screenshots/draw.png" width="700" alt="تولید تصویر در ترمینال"/>
  <br/><br/>
  <img src="screenshots/sample-image.jpg" width="380" alt="نمونه تصویر تولیدشده"/>
  <br/>
  <sup>↑ خروجی واقعی همین دستور — یک اردک واقعی، به‌ظاهر 🦆</sup>
</p>

تصاویر تولیدشده به‌صورت JPEG در پوشهٔ فعلی ذخیره می‌شوند (یا `--out مسیر/پوشه`).

#### 📞 تماس زندهٔ صوتی

```bash
python duck_cli.py --voice
```

یک تماس دوطرفهٔ واقعی WebRTC: سرور تشخیص می‌دهد کی حرفتان تمام شده (VAD سمت سرور)، گفتارتان را تبدیل به متن می‌کند، با صدای واقعی جواب می‌دهد — و کل ترنسکریپت را در کنسول می‌بینید. حتی می‌توانید به‌جای میکروفون یک فایل صوتی به آن بدهید.

<p align="center">
  <img src="screenshots/voice.png" width="640" alt="ترنسکریپت تماس زندهٔ WebRTC"/>
</p>

> [!TIP]
> در تماس زنده حتماً هندزفری بزنید — اکوی بلندگو تشخیص گفتار سرور را گمراه می‌کند.

حالت‌های دیگر صدا:

```bash
python duck_cli.py --listen             # میکروفون ← متن (Enter = پایان)
python duck_cli.py --dictate clip.mp3   # هر فایل صوتی ← متن (wav/mp3/m4a/webm…)
```

#### 🤖 تغییر مدل

```bash
python duck_cli.py --ask "سلام" --model mini
```

**هر شش مدل رایگان فعلی** (مطابق کانفیگ خود duck.ai — تست‌شده به‌صورت زنده):

| میان‌بر | شناسه مدل | توضیح |
|:---:|---|---|
| `luna` | `gpt-6-luna` | پیش‌فرض سطح رایگان |
| `mini` | `gpt-5.4-mini` | سریع‌تر، از سهمیه مصرف می‌گذرد |
| `haiku` | `claude-haiku-5-5` | سریع‌تر، از سهمیه مصرف می‌گذرد |
| `mistral` | `mistral-small-2603` | |
| `oss` | `tinfoil/gpt-oss-120b` | متن‌باز ۱۲۰ میلیارد پارامتری |
| `gemma` | `tinfoil/gemma4-31b` | متن‌باز Gemma 4 نسخهٔ 31B |

<p align="center">
  <img src="screenshots/models.png" width="620" alt="انتخابگر مدل با همهٔ مدل‌های رایگان"/>
</p>

> [!NOTE]
> شناسه‌های قدیمی (`gpt-5.6-luna`، `gpt-5.4-nano`، `claude-haiku-4-5`) هنوز کار می‌کنند — سرور خودش آن‌ها را به مدل جایگزین ارتقا می‌دهد.
> مدل‌های سطح پولی (`gpt-5.6-terra`، `claude-sonnet-5-5`، `claude-opus-5-5`، `gpt-5.6-sol`) بدون اشتراک با خطای `ERR_MODEL_RESTRICTED` رد می‌شوند.

#### 🌐 پروکسی و زبان

```bash
python duck_cli.py --ask "سلام" --proxy http://127.0.0.1:8080
python duck_cli.py --ask "سلام" --proxy socks5://127.0.0.1:1080
python duck_cli.py --lang fa             # رابط فارسی (یا: setx DUCKAI_LANG fa)
```

---

### 🔧 چطور کار می‌کند

1. `GET https://duck.ai/` ← استخراج `data-version-tag` / `data-version-sha` ← ساخت `x-fe-version`
2. `GET /duckchat/v1/status` (هدر `x-vqd-accept: 1`) ← برگرداندن `x-vqd-hash-1`: یک **چالش JS** کدشده با base64
3. چالش **محلی** با Node.js + jsdom (`jsa_jsdom.js`) حل می‌شود — بدون مرورگر واقعی
4. جواب چالش در قالب نهایی `x-vqd-hash-1` بسته‌بندی می‌شود (`client_hashes` = base64ِ sha256)
5. `POST /duckchat/v1/chat` پاسخ را به‌صورت رویدادهای **SSE** استریم می‌کند

<details>
<summary><b>🎙 پروتکل صدا (WebRTC)</b></summary>
<br/>

`GET /duckchat/v1/ice-servers` ← سرورهای TURN ← `POST /duckchat/v1/session` (offer/answer SDP، صدای Opus) ← تشخیص گفتار سمت سرور انجام می‌شود و رویدادها روی datachannel به نام `duckai-voice-session` برمی‌گردند: `input_audio_buffer.speech_*`، `response.output_audio_transcript.delta`، `output_audio_buffer.started/stopped`…
</details>

<details>
<summary><b>📁 ساختار پروژه</b></summary>
<br/>

```
DuckAi/
├── duck_cli.py              # CLI اصلی: چت، تصویر، فایل، تولید تصویر
├── duck_voice.py            # دیکته + جلسهٔ ویس زندهٔ WebRTC
├── duck_i18n.py             # متن‌های دوزبانهٔ رابط
├── jsa_jsdom.js             # اجراکنندهٔ Node برای حل چالش duck.ai
├── requirements.txt         # وابستگی‌های اصلی پایتون
├── requirements-voice.txt   # وابستگی‌های اختیاری صوتی
├── package.json             # وابستگی‌های Node (jsdom)
└── screenshots/             # اسکرین‌شات‌های واقعی این README
```
</details>

### 🐞 رفع اشکال

| مشکل | راه‌حل |
|---|---|
| `Node.js was not found on PATH` | از [nodejs.org](https://nodejs.org) نصب کنید و ترمینال را دوباره باز کنید |
| `The 'jsdom' package is missing` | **داخل پوشهٔ پروژه** `npm install` را اجرا کنید |
| `HTTP 403` / `No challenge received` | IP محدود شده — کمی صبر کنید یا `--proxy` بدهید |
| تکرار `HTTP 418` | امتیاز ضد سوءاستفاده duck.ai — معمولاً با چالش تازه خودش رفع می‌شود |
| متن فارسی به‌هم‌ریخته در ویندوز | اول `chcp 65001` را بزنید یا از Windows Terminal استفاده کنید |
| `ERR_MODEL_RESTRICTED` | آن مدل مخصوص اشتراک پولی است — یکی از شش مدل رایگان را انتخاب کنید |
| خطای میکروفون | `pip install -r requirements-voice.txt` |

---

<div align="center">

**🦆 DuckAi** — free AI, straight from your terminal

<sub>MIT License · Use responsibly / با مسئولیت خودتان استفاده کنید</sub>

<br/>

⭐ **اگر این پروژه به کارت آمد، به آن ستاره بده!** · **Star this repo if it helped you!**

</div>
