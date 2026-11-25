# AI Skin Specialist 🩺

An AI-powered skin consultation assistant that allows users to describe their skin concerns through voice input and provide skin images or videos for AI-assisted analysis. The application processes the patient's input and generates written guidance along with an audio response.

Built using **Python, Gradio, Groq AI, Whisper, and Deepgram**.

> **Disclaimer:** This application provides informational AI-generated guidance only. It is not a substitute for professional medical advice, diagnosis, or treatment.

---

## ✨ Features

- **Voice Input:** Users can describe their skin concerns using a microphone or an audio file.
- **Speech-to-Text:** Converts patient voice input into text using Groq Whisper.
- **Image Analysis:** Processes skin images using a Groq vision model.
- **Video Analysis:** Extracts video frames for visual analysis.
- **Combined Input:** Supports image-only, video-only, or image-and-video input.
- **AI-Powered Guidance:** Generates responses based on the patient's description and available visual information.
- **Text-to-Speech:** Converts AI-generated guidance into audio using Deepgram.
- **Interactive Interface:** Provides a user-friendly interface built with Gradio.
- **Centralized Logging:** Uses a dedicated logging module to manage application logs.
- **Media Validation:** Validates uploaded audio, image, and video inputs before processing.

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Gradio | Interactive web interface |
| Groq API | AI-powered processing |
| Groq Whisper | Voice transcription |
| Groq Vision Model | Image and video analysis |
| Deepgram API | Text-to-speech generation |
| Pillow | Image processing |
| OpenCV | Video frame processing |
| python-dotenv | Environment variable management |
| uv | Python package and project management |

---

## 📂 Project Structure

```text
ai-skin-specialist/
│
├── main.py
├── app_logging.py
├── media_validation.py
│
├── brain_of_the_doctor_groq.py
├── voice_of_the_patient.py
├── voice_of_the_doctor.py
│
├── stitch_ai_skin_specialist_dashboard/
│   ├── code.html
│   ├── DESIGN.md
│   └── screen.png
│
├── .env.example
├── .gitignore
├── pyproject.toml
├── uv.lock
└── README.md
```

### Important Files

- **`main.py`** — Main Gradio application and processing workflow.
- **`brain_of_the_doctor_groq.py`** — Handles AI-based image/video analysis and response generation using Groq.
- **`voice_of_the_patient.py`** — Handles patient audio transcription using Groq Whisper.
- **`voice_of_the_doctor.py`** — Converts generated text responses into speech using Deepgram.
- **`media_validation.py`** — Validates audio, image, and video inputs.
- **`app_logging.py`** — Provides centralized application logging.
- **`stitch_ai_skin_specialist_dashboard/`** — Separate dashboard design prototype, not integrated into the default Gradio application.

---

## ⚙️ Requirements

Before running the project, make sure you have:

- Python 3.11 or newer
- uv package manager
- Groq API key
- Deepgram API key
- Internet connection

---

## 🚀 Installation and Setup

### 1. Clone the Repository

```bash
git clone YOUR_REPOSITORY_URL
```

Navigate into the project directory:

```bash
cd ai-skin-specialist
```

### 2. Install Dependencies

Install the project dependencies using uv:

```bash
uv sync
```

### 3. Configure Environment Variables

Create a `.env` file from the provided example.

**Windows PowerShell:**

```powershell
Copy-Item .env.example .env
```

**Linux / macOS:**

```bash
cp .env.example .env
```

Open the `.env` file and add your API keys:

```env
# Required API Keys
GROQ_API_KEY=your_groq_api_key_here
DEEPGRAM_API_KEY=your_deepgram_api_key_here

# Optional Model Configuration
WHISPER_MODEL=whisper-large-v3
GROQ_MODEL=qwen/qwen3.8-27b
DEEPGRAM_TTS_MODEL=aura-2-thalia-en

# Optional: Only for the alternative MiniMax implementation
MINIMAX_API_KEY=
MINIMAX_BASE_URL=https://api.minimax.io/anthropic
MINIMAX_MODEL=MiniMax-M3
```

**Note:**
- `GROQ_API_KEY` and `DEEPGRAM_API_KEY` are required for the default application workflow.
- Model configuration variables are optional.
- MiniMax variables are retained for optional configuration compatibility; the default application does not use the alternative MiniMax implementation.
- Never upload your actual `.env` file or expose API keys publicly.

---

## ▶️ Run the Application

Start the application using:

```bash
uv run python main.py
```

Once the application starts, open the following address in your browser:

```text
http://127.0.0.1:7861
```

You can now interact with the AI Skin Specialist application.

---

## 🔄 Application Workflow

The application follows this workflow:

```text
       Patient Input
             |
     +-------+-------+
     |       |       |
   Voice   Image   Video
     |       |       |
     v       |       |
 Groq Whisper |       |
     |       |       |
     v       v       v
  Transcribed  Visual Processing
     Text          |
        \          /
         \        /
          v      v
       Groq AI Model
             |
             v
    AI-Generated Guidance
             |
       +-----+-----+
       |           |
       v           v
   Text Output  Deepgram TTS
                   |
                   v
               Audio Output
```

### Processing Steps

1. The patient provides a voice description of their skin concern.
2. Groq Whisper converts the voice input into text.
3. The patient can provide a skin image, video, or both.
4. The application processes the available visual input.
5. The transcribed text and visual information are passed to the Groq AI model.
6. The AI generates informational guidance based on the provided information.
7. The generated response is displayed as text.
8. Deepgram converts the response into audio.

### Image and Video Support

The application supports three input combinations:

- Image only
- Video only
- Image and video together

For video processing, the application extracts up to three frames for visual analysis. When an image is also supplied, it processes the image along with up to two video frames.

---

## 🔐 Security and Privacy

The project follows basic security practices:

- API keys are stored in environment variables.
- The `.env` file is excluded from Git using `.gitignore`.
- `.env.example` contains placeholder values for configuration.
- Uploaded media is validated before processing.
- Application logging is centralized.

**Important:** Avoid uploading sensitive personal or medical information unless you understand how the application and its external AI services process that information. Do not assume that uploaded media or API requests are automatically private.

---

## ⚠️ Medical Disclaimer

AI Skin Specialist is an experimental AI-powered informational assistant.

- It does not provide a confirmed medical diagnosis.
- AI-generated responses may be incomplete or inaccurate.
- Visual analysis cannot replace a professional skin examination.
- Users should consult a qualified healthcare professional for medical concerns.
- Do not use the application to make medication or treatment decisions without professional advice.

---

## 🔮 Future Improvements

Potential future improvements include:

- Improved skin image analysis.
- More accurate voice interaction.
- Better multilingual support.
- Enhanced user interface.
- Improved video processing.
- Consultation history and report generation.
- Additional AI model integrations.

---

## 👨‍💻 Author

**Bikram Das|Purbasha Ram**

AI Skin Specialist — An AI-powered skin consultation assistant built using Python and modern AI technologies.

---

## ⭐ Support

If you find this project interesting or useful, consider giving the repository a star ⭐ on GitHub.

Contributions, suggestions, and feedback are welcome!