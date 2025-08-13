# 🧠 Smart Quiz Generator

An interactive **AI-powered quiz creation tool** built with **Streamlit** and **LangChain** that uses **GPT-4** to generate quizzes from your own documents (PDF/TXT) or web content (URLs).  
The app processes your content, stores it in a **FAISS vector database**, and lets you create customized quizzes on any topic.

---

## 📌 Features
- Upload **PDF** or **TXT** files, or provide **web URLs**.
- Process documents into searchable vector embeddings using **OpenAI embeddings**.
- Create quizzes in multiple formats:
  - Multiple Choice Questions (MCQ)
  - True/False
  - Fill-in-the-Blank
- Customizable number of questions.
- Download generated quizzes as text files.

---

## 🛠 Installation

### 1️⃣ Clone the repository
```bash
git clone https://github.com/kumpatlapavankumar/EduBot-Smart-Quiz-Generator.git
cd smart-quiz-generator
```

### 2️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Set your OpenAI API key
Create a `.env` file in the project folder and add:
```env
OPENAI_API_KEY=your_api_key_here
```
Or use **Streamlit Secrets** for deployment:
```toml
# .streamlit/secrets.toml
OPENAI_API_KEY = "your_api_key_here"
```

---

## 🚀 Usage

Run the app locally:
```bash
streamlit run main.py
```

### **Tab 1 – Process Content**
- Paste URLs or upload PDF/TXT files.
- Click **"🚀 Process Content"** to store embeddings.

### **Tab 2 – Generate Quiz**
- Enter a topic (e.g., *Machine Learning Basics*).
- Select quiz type and number of questions.
- Click **"✨ Generate Quiz"** to create your quiz.
- Download the quiz as a `.txt` file.

---

## 📂 Project Structure
```
.
├── main.py                 # Main Streamlit application
├── requirements.txt        # Python dependencies
├── quiz_vector_store.pkl   # Generated FAISS vector store (after processing)
└── README.md               # Documentation
```

---

## 📦 Tech Stack
- **Python**
- **Streamlit** – Web app framework
- **LangChain** – Document processing & LLM integration
- **OpenAI GPT-4** – Quiz generation
- **FAISS** – Vector storage & retrieval
- **PyMuPDF** – PDF parsing
- **nltk** – Text processing

---

## 📝 License
This project is licensed under the MIT License.

---

## 👨‍💻 Author
**Pavankumar**  
💡 Powered by **GPT-4**, **LangChain**, and **Streamlit**.
