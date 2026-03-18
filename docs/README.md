GigShield AI — Backend
Requirements

Python 3.10 or higher
pip

Setup & Run
1. Clone the repo
bashgit clone https://github.com/Mrithikahub/gigshield-ai.git
cd gigshield-ai/backend
2. Create virtual environment
bashpython -m venv .venv
3. Activate it
Windows:
bash.venv\Scripts\activate
Mac/Linux:
bashsource .venv/bin/activate
4. Install dependencies
bashpip install -r requirements.txt
pip install joblib scikit-learn pandas
5. Run the server
bashpython -m uvicorn app.main:app --reload
6. Open API docs
http://localhost:8000/docs
