# Voice to CRM
![Python](https://img.shields.io/badge/Python-3670A0?style=flat&logo=python&logoColor=white) ![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat&logo=langchain&logoColor=white) ![Airtable](https://img.shields.io/badge/Airtable-18BFFF?style=flat&logo=airtable&logoColor=white) ![Telegram](https://img.shields.io/badge/Telegram-26A5E4?style=flat&logo=telegram&logoColor=white)

An intelligent agent that automatically analyzes a vocal request (by telegram chat) to identify and process requests.

## 🔧 Installation

Clone the repository
```shell
git clone https://github.com/Oscaro92/voice2crm.git
cd voice2crm
```

Create a virtual environment
```shell
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
.\venv\Scripts\activate  # Windows
```

Install dependencies
```shell
pip install -r requirements.txt
```

## ⚙️ Configuration

Create a `.env` file with the following variables:
```
OPENAI_API_KEY=sk-proj-...
AIRTABLE_API_KEY=
BASE_ID=
TABLE_ID=
HTTPTOKEN=
```

## 🚀 Usage

Run project
```shell
python chatbotTG.py
```

## 📁 Project Structure

```
voice2crm/
├── agent.py            # Agent 
├── chatbotTG.py        # Chatbot Telegram
├── requirements.txt    # Dependencies
├── .env                # Environment variables
└── README.md           # Documentation
```

## 📝 License

This project is licensed under the MIT License.
