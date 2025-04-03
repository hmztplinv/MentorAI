# MentorAI
# AI Psychologist Application

This application provides psychological support through a locally run AI assistant with multiple therapy approaches. It is designed with privacy in mind, running completely locally without sending data to external servers.

## 📋 Features

- **Multiple Therapy Approaches**: 12 different therapeutic frameworks including CBT, Psychoanalytic, Humanistic, and more
- **Multilingual Support**: Turkish and English language support
- **Voice Input**: Speech-to-text capability using Whisper
- **Privacy-Focused**: All data remains on your local machine
- **Memory Management**: Short-term and long-term memory for more personalized interactions
- **Crisis Detection**: Identifies potential crisis situations and provides appropriate resources

## 🔧 Technology Stack

- **AI Model**: Phi-4 (via Ollama)
- **Speech Recognition**: Whisper
- **Backend**: Python FastAPI
- **Database**: SQLite (conversation history) + Chroma DB (vector database for semantic memory)
- **Frontend**: React (to be implemented)

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- [Ollama](https://ollama.ai/) installed and running
- Windows 11 (or other OS with proper adjustments)

### Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/ai-psychologist.git
   cd ai-psychologist
   ```

2. Run the setup script:
   ```
   python setup.py
   ```

3. Pull the Phi model in Ollama:
   ```
   ollama pull phi
   ```

4. Start the application:
   ```
   python run.py
   ```

5. The API documentation will open automatically in your browser at `http://localhost:8000/docs`

## 📝 API Documentation

Once the server is running, you can access the interactive API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🛠️ Project Structure

```
ai-psychologist/
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── chat.py
│   │   │   ├── sessions.py
│   │   │   ├── users.py
│   │   │   └── voice.py
│   │   └── api.py
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   ├── base.py
│   │   └── init_db.py
│   ├── models/
│   │   ├── message.py
│   │   ├── session.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── message.py
│   │   ├── session.py
│   │   └── user.py
│   ├── services/
│   │   ├── ai_service.py
│   │   ├── message_service.py
│   │   ├── session_service.py
│   │   ├── user_service.py
│   │   └── voice_service.py
│   ├── therapists/
│   │   └── prompts.py
│   ├── utils/
│   └── main.py
├── tests/
├── venv/
├── README.md
├── requirements.txt
├── run.py
└── setup.py
```

## 🔍 Therapy Approaches

The application supports the following therapy approaches:

1. **Cognitive Behavioral Therapy (CBT)**: Focuses on identifying and changing negative thought patterns
2. **Psychoanalytic Therapy**: Explores unconscious influences on current behavior
3. **Humanistic Therapy**: Emphasizes personal growth, self-actualization, and unconditional positive regard
4. **Existential Therapy**: Addresses existential questions about meaning, freedom, and responsibility
5. **Gestalt Therapy**: Focuses on present moment awareness and complete experiences
6. **Acceptance and Commitment Therapy (ACT)**: Combines mindfulness with value-based action
7. **Positive Psychology**: Emphasizes strengths, positive emotions, and well-being
8. **Schema Therapy**: Identifies and addresses early maladaptive schemas
9. **Solution-Focused Brief Therapy**: Focuses on solutions rather than problems
10. **Narrative Therapy**: Separates people from their problems through storytelling
11. **Family Systems Therapy**: Examines behavior in the context of family relationships
12. **Dialectical Behavior Therapy (DBT)**: Teaches skills for mindfulness, emotional regulation, and interpersonal effectiveness

## ⚠️ Disclaimer

This application is not a replacement for professional mental health services. It is designed as a supportive tool and should not be used for crisis intervention or as a substitute for professional therapy. If you or someone you know is experiencing a mental health crisis, please contact emergency services or a mental health professional.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Contributors

- [Your Name](https://github.com/yourusername)