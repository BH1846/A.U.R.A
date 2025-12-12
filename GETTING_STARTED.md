# 🚀 Getting Started with AURA

Welcome to AURA! This guide will get you up and running in minutes.

## 📋 Prerequisites Checklist

Before you begin, make sure you have:

- [ ] **Python 3.9 or higher** installed
  - Check: `python --version`
  - Download: https://www.python.org/downloads/

- [ ] **Node.js 16 or higher** installed
  - Check: `node --version`
  - Download: https://nodejs.org/

- [ ] **Git** installed
  - Check: `git --version`
  - Download: https://git-scm.com/

- [ ] **OpenAI API Key** with GPT-4 access
  - Get one: https://platform.openai.com/api-keys
  - Ensure you have GPT-4 access enabled

- [ ] **GitHub Personal Access Token** (optional, for private repos)
  - Get one: https://github.com/settings/tokens

---

## 🎯 Quick Start (3 Steps)

### Step 1: Get Your API Key
1. Go to https://platform.openai.com/api-keys
2. Create a new API key
3. Copy it (it starts with `sk-`)
4. Keep it handy for Step 3

### Step 2: Run the Setup Script
Open PowerShell in the project directory and run:
```powershell
.\start.ps1
```

This script will:
- ✅ Create virtual environment
- ✅ Install all dependencies
- ✅ Create .env file
- ✅ Prompt you for API key
- ✅ Start both servers

### Step 3: Add Your API Key
When prompted:
1. The script will open `.env` file in Notepad
2. Find the line: `OPENAI_API_KEY=your_openai_api_key_here`
3. Replace `your_openai_api_key_here` with your actual key
4. Save and close Notepad
5. Press any key to continue

**That's it! The system will start automatically.**

---

## 🌐 Access Points

Once started, you can access:

### 🎨 **Frontend (User Interface)**
```
http://localhost:3000
```
- Submit candidate applications
- Answer interview questions
- View evaluation reports
- Access recruiter dashboard

### 🔧 **Backend API**
```
http://localhost:8000
```
- Direct API access
- For integrations

### 📚 **API Documentation**
```
http://localhost:8000/docs
```
- Interactive API docs (Swagger UI)
- Test endpoints
- View request/response schemas

---

## 🧪 Test the System

### Quick Test (5 minutes)

1. **Open the frontend**: http://localhost:3000

2. **Submit a test candidate**:
   - Name: Test User
   - Email: test@example.com
   - GitHub URL: Use a public repository (e.g., any of your projects)
   - Role: Frontend (or any role)

3. **Wait for analysis** (1-3 minutes)
   - System will analyze the repository
   - You'll see a loading screen

4. **Answer questions**
   - You'll get 6-10 questions about the project
   - Provide detailed answers (aim for 2-3 sentences minimum)

5. **View results**
   - Automatic evaluation
   - Comprehensive report
   - Download PDF

6. **Check dashboard**
   - Navigate to http://localhost:3000/dashboard
   - See all candidates
   - Compare scores

---

## 📖 What to Read Next

After getting started:

1. **README.md** - Project overview and features
2. **ARCHITECTURE.md** - System design and diagrams
3. **API_DOCUMENTATION.md** - Complete API reference
4. **PROJECT_SUMMARY.md** - Detailed technical overview

---

## 🐛 Troubleshooting

### "Python command not found"
**Solution**: Install Python from https://www.python.org/downloads/
Make sure to check "Add Python to PATH" during installation.

### "npm command not found"
**Solution**: Install Node.js from https://nodejs.org/

### "OpenAI API key invalid"
**Solution**: 
- Verify your API key is correct
- Ensure you have GPT-4 access
- Check your OpenAI account has credits

### "Port 8000 already in use"
**Solution**: Edit `backend/.env` and change `PORT=8000` to another port (e.g., `PORT=8001`)

### "Port 3000 already in use"
**Solution**: When Vite starts, it will ask if you want to use another port. Press 'y' to accept.

### "Module not found" errors
**Solution**: 
```powershell
cd backend
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Backend server won't start
**Solution**:
1. Check if virtual environment is activated
2. Verify .env file has your API key
3. Ensure Python 3.9+ is installed
4. Check terminal for specific error messages

---

## 💡 Tips for Best Results

### Choosing Repositories
- ✅ Use well-documented projects
- ✅ Include a README.md file
- ✅ Projects with 100+ lines of code work best
- ✅ Public repositories are easiest

### Answering Questions
- ✅ Provide detailed explanations (2-3 sentences minimum)
- ✅ Explain your reasoning
- ✅ Be specific about implementation details
- ✅ Mention trade-offs and alternatives
- ❌ Avoid one-word answers
- ❌ Don't say "I don't know" without explanation

### System Performance
- First run will be slower (downloads models)
- Subsequent runs are faster
- Analysis time: 1-3 minutes
- Evaluation time: 30-60 seconds

---

## 🎓 Learning Path

### Day 1: Get Started
- [ ] Complete installation
- [ ] Submit test candidate
- [ ] Answer questions
- [ ] View report

### Day 2: Explore Features
- [ ] Try different role types
- [ ] Test with multiple repositories
- [ ] Explore recruiter dashboard
- [ ] Download PDF reports

### Day 3: Understand the System
- [ ] Read architecture documentation
- [ ] Review API documentation
- [ ] Explore code structure
- [ ] Understand evaluation criteria

### Day 4+: Customize
- [ ] Modify role profiles
- [ ] Adjust scoring weights
- [ ] Customize questions
- [ ] Add new features

---

## 🔧 Configuration Options

### Basic Settings (backend/.env)

```env
# LLM Model
MODEL_NAME=gpt-4                    # or gpt-4-turbo
TEMPERATURE=0.7                     # 0.0-1.0 (lower = more consistent)

# Question Count
MAX_QUESTIONS=10                    # Maximum questions to generate
MIN_QUESTIONS=6                     # Minimum questions to generate

# Scoring Weights (must sum to 1.0)
WEIGHT_UNDERSTANDING=0.4            # 40% weight
WEIGHT_REASONING=0.3                # 30% weight
WEIGHT_COMMUNICATION=0.2            # 20% weight
WEIGHT_LOGIC=0.1                    # 10% weight
```

---

## 📞 Need Help?

### Resources
- 📖 **Documentation**: Read the docs in this folder
- 🐛 **Issues**: Check common issues above
- 💬 **API Docs**: http://localhost:8000/docs
- 🔍 **Logs**: Check terminal output for errors

### Debugging Steps
1. Check both terminal windows for errors
2. Verify all dependencies are installed
3. Ensure API key is correct in .env
4. Try restarting both servers
5. Check that required ports are available

---

## 🎯 Next Steps

Once everything is working:

✅ **Production Deployment**
   - See SETUP.md for production guidelines
   - Use PostgreSQL instead of SQLite
   - Add authentication
   - Enable HTTPS

✅ **Customization**
   - Modify role profiles in `backend/core/phase0_profiles/role_profiles.py`
   - Adjust evaluation weights in `.env`
   - Customize UI in `frontend/src/`

✅ **Integration**
   - Use API endpoints for integration
   - Generate JSON reports
   - Connect to ATS systems

---

## 🌟 Quick Command Reference

### Backend
```powershell
cd backend
.\venv\Scripts\Activate.ps1         # Activate environment
python main.py                       # Start server
pip install -r requirements.txt     # Install dependencies
deactivate                           # Deactivate environment
```

### Frontend
```powershell
cd frontend
npm install                          # Install dependencies
npm run dev                          # Start dev server
npm run build                        # Build for production
```

### Both
```powershell
.\start.ps1                          # Quick start (does everything)
```

---

## ✅ Success Indicators

You'll know everything is working when:

✅ Backend shows: `Uvicorn running on http://0.0.0.0:8000`
✅ Frontend shows: `Local: http://localhost:3000/`
✅ You can access the web interface
✅ API docs load at `/docs`
✅ Test submission completes successfully

---

## 🎉 Ready to Go!

You're all set! Here's what to do now:

1. **Open** http://localhost:3000
2. **Submit** a candidate with a GitHub repository
3. **Wait** 1-3 minutes for analysis
4. **Answer** the generated questions
5. **View** the comprehensive evaluation report

**Welcome to AURA! 🚀**

---

*For detailed information, see:*
- *SETUP.md - Complete installation guide*
- *README.md - Project documentation*
- *API_DOCUMENTATION.md - API reference*
