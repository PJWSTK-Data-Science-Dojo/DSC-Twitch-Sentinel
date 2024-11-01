# twitch-dev-2024

## Prerequisites
- Node.js
- Python
- Twitch Developer Account

## Getting Started
### Clone the Repository
```bash 
git clone https://github.com/PJWSTK-Data-Science-Dojo/twitch-dev-2024.git
cd twitch-dev-2024
```

### Run the Backend (FastAPI + Sockets.IO)
```bash
cd server

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# Windows command line
.venv\Scripts\activate
# Windows bash console (Git Bash)
source .venv/Scripts/activate
# MacOS and Linux
source .venv/bin/activate

# Install the required dependencies
pip install -r requirements.txt


# Start the Server
uvicorn app:app --reload
```
By default, the backend will be available at: `http://localhost:8000`.

### Run the Frontend (React.js)
```bash
cd client # From base repository directory

# Install the required dependencies
npm install

# Create certificates for localhost to enable HTTPS
npm run postinstall

# Configure .env file
cp .env.example .env 

# Start the Client
npm start
```


## Project Structure
```bash
├── client                  # Frontend (React.js)
│   ├── public              # Static assets
│   └── src                 # React source files
├── server                  # Backend (FastAPI)
│   ├── app.py              # FastAPI application files
│   ├── requirements.txt    # File with all python dependecies
│   ├── twitch_api          # Module focused on communication with Twitch API
│   ├── sentiment_analysis  # Module focused on Sentiment analysis
│   └── utils               # Utility modules
└── README.md               # Project README
```