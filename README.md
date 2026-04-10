# 🏥 MediRoute
### AI-Powered Healthcare Triage Assistant

MediRoute helps users in Indonesia determine the urgency of their symptoms and recommends the most appropriate healthcare facility — from pharmacy to emergency room.

> **Live Demo:** [mediroute-zeta.vercel.app](https://mediroute-zeta.vercel.app)

---

## 🩺 The Problem

Indonesians often don't know where to seek care when they feel unwell:
- Minor symptoms sent to hospital IGD = overcrowded ERs
- Serious symptoms dismissed as "just need rest" = delayed treatment
- Existing solutions (Halodoc, Alodokter) are too heavy, require accounts, and aren't agent based

**MediRoute solves this with a lightweight, conversational triage agent.**

---

## ✨ How It Works

1. User describes their symptoms in **any language** (Bahasa Indonesia or English)
2. Agent asks targeted follow up questions one at a time (max 4)
3. Agent assesses urgency and outputs a triage result:

| Level | Meaning | Recommendation |
|-------|---------|----------------|
| 🟢 MILD | No immediate danger | Rest at home / Apotek |
| 🟡 MODERATE | Needs medical attention | Puskesmas / Klinik |
| 🔴 SEVERE | Urgent — seek help now | RS / IGD immediately |

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | HTML, CSS, Vanilla JS |
| AI Model | LLaMA 3.3 70B via Groq API |
| Backend | Vercel Serverless Functions (Node.js) |
| Deployment | Vercel |
| Version Control | GitHub |

---

## 🚀 Running Locally

### Web App
Just open `index.html` in your browser. No server needed for local testing (add your Groq API key directly).

### CLI Version
```bash
pip install groq
export GROQ_API_KEY=your_key_here
python main.py
```

---

## 📁 Project Structure

```
mediroute/
├── api/
│   └── chat.js       # Vercel serverless function (handles Groq API calls)
├── index.html        # Frontend web app
└── main.py           # CLI version
```

---

## 🔒 Security

API keys are stored as Vercel environment variables. Never exposed to the client.

---

## 🗺 Roadmap

- [x] Conversational triage agent
- [x] Multi-language support (ID/EN auto detect)
- [x] Web UI with triage result card
- [x] Serverless deployment on Vercel
- [ ] Location based faskes recommendation (Google Maps API)
- [ ] Voice input support

---

## ⚠️ Disclaimer

MediRoute is not a substitute for professional medical advice. Always consult a licensed doctor for diagnosis and treatment.

---

*Built by [Edward Alexander](https://wardcv.netlify.app) 
