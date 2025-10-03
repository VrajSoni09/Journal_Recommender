# 🎓 Research Journal Recommendation System

AI-powered journal recommendation system that helps researchers find the best academic journals for their papers using Google Gemini AI and OpenAlex API.

## 📋 Table of Contents
- [Features](#features)
- [System Architecture](#system-architecture)
- [Repository Structure](#repository-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Troubleshooting](#troubleshooting)

## ✨ Features

- **AI-Powered Refinement**: Uses Google Gemini 2.0 Flash to refine paper titles, abstracts, and extract keywords
- **Smart Search**: Searches OpenAlex API with intelligent keyword matching
- **Realistic Metrics**: Estimates acceptance rates based on journal prestige (h-index)
- **Top 3 Recommendations**: Displays gold 🥇, silver 🥈, and bronze 🥉 medal rankings
- **Auto Cache Clearing**: Prevents stale results with automatic cache management
- **Open Access Support**: Filters for free/open access journals
- **Real-time Processing**: FastAPI backend with async processing

## 🏗️ System Architecture

```
┌─────────────────┐
│   Next.js       │
│   Frontend      │ ← User Interface (Port 3000)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   FastAPI       │
│   Backend       │ ← API Server (Port 8000)
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌──────┐  ┌──────┐
│ Vraj │  │ Aadi │
│  AI  │  │Search│
└──────┘  └──────┘
    │         │
    ▼         ▼
┌──────┐  ┌──────┐
│Gemini│  │OpenAlex│
│  API │  │  API   │
└──────┘  └────────┘
```

## 📁 Repository Structure

```
Journal_Recommender/
│
├── Frontend/                    # Next.js 15.5.4 Frontend
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx        # Home page
│   │   │   ├── dashboard/      # Dashboard
│   │   │   ├── recommendations/# Results page
│   │   │   └── api/            # API routes
│   │   └── components/         # React components
│   ├── package.json
│   ├── next.config.ts
│   └── tailwind.config.ts
│
├── Backend/                     # Python Backend
│   ├── Vraj/                   # AI Refinement Module
│   │   ├── main.py             # Gemini AI integration
│   │   ├── .env.example        # Environment template
│   │   └── requirements.txt
│   │
│   ├── Aadi/                   # Journal Search Module
│   │   ├── fetch_journals.py   # OpenAlex search
│   │   └── requirements.txt
│   │
│   ├── api_server.py           # Main FastAPI server
│   ├── requirements.txt        # Combined dependencies
│   └── .env.example
│
└── README.md                    # This file
```

## 🔧 Prerequisites

### Required Software
- **Python 3.8+** (Tested with Python 3.13)
- **Node.js 18+** (Tested with Node.js 20)
- **npm** or **yarn**
- **Git**

### API Keys
- **Google Gemini API Key** (Free tier: 200 requests/day)
  - Get it from: https://ai.google.dev/

## 📦 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/VrajSoni09/Journal_Recommender.git
cd Journal_Recommender
```

### 2. Backend Setup

```bash
# Navigate to Backend directory
cd Backend

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file in Vraj directory
cd Vraj
copy .env.example .env  # Windows
# or
cp .env.example .env    # Linux/Mac

# Edit .env and add your Gemini API key
# GEMINI_API_KEY=your_api_key_here
```

### 3. Frontend Setup

```bash
# Navigate to Frontend directory (from repository root)
cd Frontend

# Install dependencies
npm install

# The frontend will automatically connect to backend on localhost:8000
```

## ⚙️ Configuration

### Backend Configuration (.env)

Create `Backend/Vraj/.env`:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

### Frontend Configuration

The frontend is pre-configured to connect to `http://localhost:8000`. No additional configuration needed.

### Acceptance Rate Estimation

The system estimates acceptance rates based on journal h-index:
- **h-index > 300**: ~10% ± 3% (Top-tier: Nature, Science)
- **h-index 100-300**: 15-35% (Interpolated, excellent to very good)
- **h-index 10-100**: 35-60% (Interpolated, good to moderate)
- **h-index < 10**: 60-85% (Lower quality)

## 🚀 Running the Application

### Option 1: Manual Start (Recommended for Development)

**Terminal 1 - Backend:**
```bash
cd Backend
python api_server.py
```
The backend will start on `http://localhost:8000`

**Terminal 2 - Frontend:**
```bash
cd Frontend
npm run dev
```
The frontend will start on `http://localhost:3000`

### Option 2: Production Build

**Backend:**
```bash
cd Backend
uvicorn api_server:app --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd Frontend
npm run build
npm start
```

## 📖 API Documentation

### Main Endpoint

**POST** `/api/recommend`

**Request Body:**
```json
{
  "subjectArea": "Computer Science",
  "title": "Neural Networks for Image Recognition",
  "abstract": "Deep learning models using convolutional neural networks...",
  "accPercentFrom": 0,
  "accPercentTo": 100,
  "openAccess": true
}
```

**Response:**
```json
{
  "success": true,
  "recommendations": [
    {
      "rank": 1,
      "name": "Journal of Economic Perspectives",
      "publisher": "American Economic Association",
      "impactFactor": 386.0,
      "citationCount": 534118,
      "acceptanceRate": 12,
      "openAccess": true,
      "apc": 0,
      "homepage": "https://...",
      "score": 64.0,
      "explanation": "Strong publication venue..."
    }
  ],
  "processingTime": 8.45,
  "timestamp": "2025-10-04T00:55:45Z"
}
```

### Health Check

**GET** `/health`

Returns server status and version information.

## 🔍 How It Works

1. **User Input**: User enters paper details (subject, title, abstract, filters)
2. **AI Refinement (Vraj)**: 
   - Gemini AI fixes spelling, expands abbreviations
   - Extracts 15-20 relevant keywords
   - Quota fallback uses intelligent regex extraction
3. **Cache Clearing**: Automatically clears old results to prevent stale data
4. **Journal Search (Aadi)**:
   - Searches OpenAlex with strict `AND` logic: `"Subject AND (keyword1 AND keyword2...)"`
   - Fetches top works in the field
   - Identifies journals publishing those works
5. **Scoring & Ranking**:
   - Relevance (40%): How often journal appears in top works
   - Impact (30%): H-index and citation count
   - Open Access (30%): Accessibility bonus
6. **Acceptance Rate Estimation**: Based on h-index with ±3% variance
7. **Top 3 Display**: Returns gold/silver/bronze ranked journals

## 🛠️ Troubleshooting

### Backend Issues

**Problem: "Gemini quota exceeded"**
- **Solution**: The system automatically uses fallback keyword extraction
- **Note**: Gemini free tier = 200 requests/day

**Problem: "Port 8000 already in use"**
```bash
# Windows:
taskkill /F /IM python.exe
# Linux/Mac:
killall python
```

**Problem: "Same results for different subjects"**
- **Solution**: Cache is now auto-cleared before each search
- **Manual fix**: Delete `Backend/Aadi/journal_results.json` and `__pycache__` directories

### Frontend Issues

**Problem: "localhost refused to connect"**
```bash
# Restart frontend
cd Frontend
npm run dev
```

**Problem: "Module not found"**
```bash
# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### Search Result Issues

**Problem: "Getting biology journals for Computer Science"**
- **Fixed**: Search now uses strict `AND` logic with subject area
- **Verify**: Check `Backend/Aadi/format.json` for correct keywords

**Problem: "Acceptance rate always 50%"**
- **Fixed**: Now uses realistic h-index based estimation with variance

## 📊 Key Features Breakdown

### Automatic Cache Management
- Clears `journal_results.json` before each search
- Removes Python `__pycache__` to prevent stale code
- Ensures fresh results every time

### Intelligent Fallback System
When Gemini quota is exceeded:
- Extracts keywords using regex
- Removes stop words (the, a, and, etc.)
- Focuses on technical terms
- Maintains search quality

### Strict Search Algorithm
```python
query = "Computer Science AND (neural AND networks AND image AND recognition AND deep)"
```
This ensures journals MUST match the subject AND core keywords.

### Realistic Acceptance Rates
- Smooth linear interpolation between h-index ranges
- ±3% random jitter for variance
- Clamped between 5-85%
- Different values for journals with same h-index

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the MIT License.

## 👥 Authors

- **Vraj** - AI Refinement System (Gemini Integration)
- **Aadi** - Journal Search System (OpenAlex Integration)
- **Kunj** - Full-Stack Integration & Deployment

## 🙏 Acknowledgments

- Google Gemini API for AI-powered text refinement
- OpenAlex API for comprehensive journal database
- Next.js team for the amazing framework
- FastAPI for high-performance backend

## 📧 Support

For issues, questions, or suggestions:
- Create an issue on GitHub
- Email: [Your Email]

---

**Made with ❤️ by the Research Hub Team**
