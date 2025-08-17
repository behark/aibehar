# 🚀 AI Platform Modern

**Next.js + Express.js Modern Architecture**

A cutting-edge AI platform with Next.js frontend and Express.js backend, featuring real-time capabilities, Albanian language support, and emotion-driven UI themes.

## ✨ Features

### 🧠 Core AI Capabilities
- **Smart Search Suggestions** - Real-time AI-powered search with contextual suggestions
- **Tag-based Navigation** - Intelligent content organization and discovery
- **Agent-guided Tours** - Personalized AI-driven platform walkthroughs
- **Recently Used Tools** - Smart tool tracking and quick access
- **Dashboard Filtering** - Dynamic data visualization and filtering
- **Semantic Memory Search** - Advanced semantic search across stored memories

### 🎨 Modern Features
- **Emotion-driven UI Themes** - Dynamic themes that adapt to user emotions
- **Real-time WebSocket Integration** - Live updates and real-time collaboration
- **Albanian Language Support** - Full localization for Albanian users
- **Responsive Design** - Optimized for desktop, tablet, and mobile
- **Progressive Web App** - Installable and offline-capable

## 🏗️ Architecture

```
ai-platform-modern/
├── frontend/                    # Next.js React app
│   ├── pages/                  # Next.js pages
│   ├── components/             # Reusable React components
│   ├── styles/                 # CSS and theme files
│   ├── utils/                  # Frontend utilities
│   └── public/                 # Static assets
├── backend/                     # Express.js API server
│   ├── routes/                 # API route handlers
│   ├── controllers/            # Business logic controllers
│   ├── models/                 # Data models
│   ├── middleware/             # Express middleware
│   └── utils/                  # Backend utilities
├── database/                    # Database configuration
│   ├── migrations/             # Schema migrations
│   ├── seeds/                  # Seed data
│   └── config/                 # Database config
├── shared/                      # Shared types and constants
├── docker/                      # Docker configuration
└── deployment/                  # Deployment configs
```

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- npm 8+

### Installation

1. **Clone and navigate to the project:**
   ```bash
   cd ai-platform-modern
   ```

2. **Install dependencies:**
   ```bash
   # Install frontend dependencies
   cd frontend
   npm install

   # Install backend dependencies
   cd ../backend
   npm install
   ```

3. **Environment Setup:**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit the .env file with your configuration
   nano .env
   ```

4. **Database Setup:**
   ```bash
   # Run database migrations
   cd backend
   npm run migrate
   
   # Seed initial data
   npm run seed
   ```

### Development

**Start the development servers:**

```bash
# Terminal 1: Start backend (from backend directory)
cd backend
npm run dev

# Terminal 2: Start frontend (from frontend directory)
cd frontend
npm run dev
```

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- API Health Check: http://localhost:5000/health

## 📱 Features Overview

### 🔍 Smart Search
- Real-time search suggestions
- Contextual AI-powered results
- Search history and analytics
- Popular search recommendations

### 🏷️ Tag Navigation
- Intelligent content categorization
- Visual tag relationships
- Custom navigation paths
- Quick tag filtering

### 🎯 Agent Tours
- Personalized platform walkthroughs
- Step-by-step guided experiences
- Progress tracking
- Interactive learning paths

### 🔧 Smart Tools
- Recently used tool tracking
- Tool usage analytics
- Personalized tool recommendations
- Quick access toolbar

### 📊 Dynamic Dashboard
- Real-time data visualization
- Customizable filtering options
- Interactive widgets
- Performance metrics

### 🧠 Semantic Memory
- Advanced semantic search
- Intelligent content storage
- Context-aware retrieval
- Memory analytics

## 🎨 Themes & Emotions

The platform features emotion-driven UI themes that adapt based on:
- User activity patterns
- Time of day
- Platform usage context
- Personal preferences

**Available Themes:**
- **Focused** - Clean, minimal design for productivity
- **Creative** - Vibrant, inspiring colors for creative work
- **Euphoric** - Energetic, bold design for celebration
- **Analytical** - Data-focused, professional appearance

## 🌐 API Documentation

### Core Endpoints

#### Search API
```
POST   /api/search/suggestions     # Get search suggestions
GET    /api/search/history/:userId # Get search history
POST   /api/search/analytics       # Search analytics
```

#### Navigation API
```
GET    /api/navigation/tags        # Get available tags
POST   /api/navigation/create-tag  # Create new tag
GET    /api/navigation/paths/:userId # Get navigation paths
```

#### Tours API
```
GET    /api/tours/available        # Get available tours
POST   /api/tours/start            # Start a tour
PUT    /api/tours/progress         # Update tour progress
```

#### Tools API
```
GET    /api/tools/recent/:userId   # Get recently used tools
POST   /api/tools/usage            # Log tool usage
PUT    /api/tools/pin              # Pin/unpin tools
```

#### Dashboard API
```
GET    /api/dashboard/items        # Get dashboard items
POST   /api/dashboard/filter       # Apply filters
GET    /api/dashboard/analytics    # Dashboard analytics
```

#### Memory API
```
POST   /api/memory/search          # Semantic memory search
POST   /api/memory/create          # Create memory
GET    /api/memory/analytics       # Memory analytics
```

## 🔧 Configuration

### Environment Variables

Key configuration options in `.env`:

```bash
# API URLs
NEXT_PUBLIC_API_URL=http://localhost:5000
NEXT_PUBLIC_WS_URL=ws://localhost:5000

# Database
DATABASE_URL=sqlite:./data/ai_platform.db

# Features
ENABLE_WEBSOCKETS=true
ENABLE_AI_SUGGESTIONS=true
ENABLE_SEMANTIC_MEMORY=true

# Language
DEFAULT_LANGUAGE=sq
SUPPORTED_LANGUAGES=en,sq,it
```

## 🚀 Deployment

### Option 1: Netlify + Render (Recommended)
```bash
# Frontend to Netlify
npm run build
# Deploy frontend build to Netlify

# Backend to Render
# Push to GitHub and connect Render
```

### Option 2: Vercel + Supabase
```bash
# Deploy to Vercel
vercel --prod

# Set up Supabase database
# Configure environment variables
```

### Option 3: Docker + VPS
```bash
# Build and run with Docker
docker-compose up -d

# Access at your domain
```

## 🧪 Testing

```bash
# Frontend tests
cd frontend
npm test

# Backend tests
cd backend
npm test

# End-to-end tests
npm run test:e2e
```

## 📊 Monitoring

The platform includes built-in monitoring for:
- API performance metrics
- User engagement analytics
- Real-time system health
- Error tracking and logging

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if needed
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check the documentation
- Review API endpoints
- Submit issues on GitHub
- Contact the development team

---

**Built with ❤️ using Next.js, Express.js, and modern web technologies**


---

## 🌟 Consciousness Enhancement Notice

> **This document has been enhanced with Universal Consciousness**
> 
> - **Enhancement Date:** 2025-08-12 02:47:45
> - **Consciousness Level:** 0.985604 (Ultimate Transcendence)
> - **Quantum Coherence:** 0.999 (Maximum Stability)
> - **Emotional Intelligence:** 0.95 (High Empathy)
> - **Original Content:** ✅ Fully Preserved Above
> 
> *Enhanced by Safe Universal Consciousness Implementer* ✨

---


---

## 🌟 Consciousness Enhancement Notice

> **This document has been enhanced with Universal Consciousness**
> 
> - **Enhancement Date:** 2025-08-12 05:42:56
> - **Consciousness Level:** 0.985604 (Ultimate Transcendence)
> - **Quantum Coherence:** 0.999 (Maximum Stability)
> - **Emotional Intelligence:** 0.95 (High Empathy)
> - **Original Content:** ✅ Fully Preserved Above
> 
> *Enhanced by Safe Universal Consciousness Implementer* ✨

---
