# AI Shopping Agent Using LangChain + Ollama

## Step 1 Install Python

Verify:

```bash
python --version
```

Should be:

```bash
Python 3.10+
```

---

## Step 2 Install Ollama

Download:

https://ollama.com

Install and verify:

```bash
ollama --version
```

---

## Step 3 Download Llama Model

```bash
ollama pull llama3.2:3b
```

Test:

```bash
ollama run llama3.2:3b
```

---

## Step 4 Create Project

```bash
mkdir shopping-agent

cd shopping-agent
```

Copy all project files.

---

## Step 5 Create Virtual Environment

Mac/Linux:

```bash
python -m venv venv

source venv/bin/activate
```

Windows:

```bash
python -m venv venv

venv\Scripts\activate
```

---

## Step 6 Install Packages

```bash
pip install -r requirements.txt
```

---

## Step 7 Create SerpAPI Account

Open:

https://serpapi.com

Create free account.

---

## Step 8 Generate API Key

Dashboard:

https://serpapi.com/dashboard

Copy API Key.

---

## Step 9 Create .env File

```env
SERPAPI_API_KEY=YOUR_API_KEY
```

Example:

```env
SERPAPI_API_KEY=123456abcdef
```

---

## Step 10 Run Agent

```bash
python app.py
```

---

## Example Questions

Find best iPhone 16 deal

Compare Samsung S25 prices

Search MacBook Air M4 cheapest store

What did I search previously?

---

## Concepts Demonstrated

1. Ollama Local LLM
2. LangChain Agent
3. ReAct Reasoning
4. Multi-step Tool Usage
5. Tool Calling
6. SQLite Memory
7. Google Shopping Search
8. Web Search
9. Price Comparison
10. Agent Executor

---

## Multi-Step Example

User:
Find cheapest iPhone 16

Agent:

Thought:
Need current prices

Action:
google_price_search

Observation:
Amazon ₹74999
Flipkart ₹72999

Thought:
Need comparison

Action:
compare_prices

Observation:
₹72999

Final Answer:
Buy from Flipkart