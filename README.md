
---

# 📌 **FinEcho – AI Voice Banking Assistant**

### GHCI 25 Hackathon – Round 2 Submission

**Team:** FinEcho
**Project Type:** AI Voice Assistant for Financial Operations
**Mode:** Voice-Only (No Text – Full Voice UI)
**Youtube Link:** https://youtu.be/A6B2qBqP0mk

---

# 🎯 **Project Overview**

**FinEcho** is an AI-powered, voice-first banking assistant designed to enable users to perform **secure and hands-free financial operations** through natural speech.
The system uses **STT (Speech-to-Text)** → **LLM Intent Classification** → **n8n Automation** → **Database/API Execution** → **TTS Voice Response**.

FinEcho provides:

* Check balance
* View last 5 transactions
* Transfer money (mock)
* Get FD rate (mock API)
* General banking queries (ATM charges, card info, loan eligibility, etc.)

The entire pipeline is powered by **n8n Automation**, **Murf.ai STT**, **Gemini AI** for intent detection, **MySQL database**, and a **lightweight Python API**.

---

# 🛠️ **Technology Stack**

### **Frontend**

* HTML + JavaScript (Web Voice Interface)
* Microphone recorder (Blob to binary)
* Fetch API → n8n webhook
* Plays TTS audio returned from backend

### **Backend**

* n8n Cloud / Local instance (Main Logic Engine)

### **AI / ML Components**

* **Murf API** – Speech transcription
* **Gemini 2.5 Flash** – Intent detection & natural language understanding
* **Custom Prompt Template** (fixed intents + entity extraction)
* **TTS API** – Murf.ai or Google TTS

### **Database**

* MySQL

  * Users
  * Accounts
  * Transactions



# 🧩 **System Architecture**

```
🎤 User Speaks 
   ↓
Frontend (JavaScript Webpage)
   • Records audio
   • Sends audio + userId + authToken → n8n webhook

🌐 n8n Workflow
1. Webhook receives request  
2. Auth check node  
3. Merge node (combine user + audio)  
4. Murf STT → transcript  
5. Gemini → intent classification  
6. Switch node → choose flow  
7. For "check_balance":
      • Merge userId  
      • Call FastAPI /balance?user_id=xxx  
8. n8n sends responseText + TTS audio  
   ↓

🎧 Frontend
• Displays text response (optional)
• Plays TTS audio output
```

---

# 🗄️ **Data Model & SQL Schema**

### **Users Table**

```sql
CREATE TABLE users (
  user_id VARCHAR(255) PRIMARY KEY,
  full_name VARCHAR(255) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### **Accounts Table**

```sql
CREATE TABLE accounts (
  account_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id VARCHAR(255),
  account_type VARCHAR(50),
  balance DECIMAL(10,2),
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

### **Transactions Table**

```sql
CREATE TABLE transactions (
  transaction_id INT AUTO_INCREMENT PRIMARY KEY,
  user_id VARCHAR(255),
  transaction_type ENUM('debit','credit'),
  amount DECIMAL(10,2),
  description VARCHAR(255),
  transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

### **Sample Data**

You already inserted data for:

* user_001 (Anjali Sharma)
* user_002 (Rohan Verma)

---


# 🔗 **n8n Workflow Explanation**

### **Nodes Used**

1. Webhook (POST) – receives audio + user_id
2. Auth Check (JS node)
3. IF node – continue only if auth == true
4. Merge node – bring back original user_id
5. Murf STT Node – convert audio → text
6. Gemini AI Text Node – generate JSON with transcript + intent
7. JavaScript Parser Node – clean JSON
8. Switch Node – route based on intent
9. Branches:

   * **check_balance** → HTTP node → FastAPI `/balance`
   * **transaction_history** → FastAPI `/transactions`
   * **fd_rate** → Beeceptor mock endpoint
   * **general_query** → Gemini → TTS output
10. TTS Node – convert text response to speech
11. Webhook Response – return audio file to frontend

---

# 🌐 **Frontend Setup**

### **index.html**

* Records audio
* Sends to n8n
* Receives audio
* Plays response



# 🔐 **Security & Compliance**

* Auth Token verification
* All database access via FastAPI only
* No model hosting (all cloud APIs)
* No user-sensitive audio stored
* Compliant with RBI guidelines for mock systems
* HTTPS enforced

---

# ⚡ **Scalability & Performance**

* n8n modular workflows
* MySQL can scale to millions of transactions
* Frontend and backend stateless – can be containerized
* All AI calls async → supports multiple users
* Workflow can be extended to:

  * Loan Inquiry
  * Credit card application
  * Full banking suite
