import streamlit as st
import os
import pickle
from dotenv import load_dotenv
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import UnstructuredURLLoader, PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
from langchain.schema import SystemMessage, HumanMessage
from langchain.docstore.document import Document
import nltk
nltk.download('punkt')
FILE_PATH = "quiz_vector_store.pkl"

# Load API key
if "OPENAI_API_KEY" in st.secrets:
    os.environ["OPENAI_API_KEY"] = st.secrets["OPENAI_API_KEY"]
else:
    load_dotenv()

# ---------------------- QUIZ GENERATION ----------------------
def generate_prompt(content, quiz_type, num_questions):
    if quiz_type == "MCQ":
        return f"Generate {num_questions} MCQs from this content:\n\n\"\"\"{content}\"\"\"\nEach question must have 4 options (A-D) and clearly indicate the correct answer."
    elif quiz_type == "True/False":
        return f"Generate {num_questions} True/False questions from this content:\n\n\"\"\"{content}\"\"\"\nIndicate the correct answer after each question."
    elif quiz_type == "Fill-in-the-Blank":
        return f"Generate {num_questions} fill-in-the-blank questions from this content:\n\n\"\"\"{content}\"\"\"\nPut the correct answer in parentheses at the end of each question."

def message_create(prompt):
    return [
        SystemMessage(content="You are a helpful AI tutor."),
        HumanMessage(content=prompt),
    ]

def get_quiz(prompt):
    chat_model = ChatOpenAI(model="gpt-4", temperature=0.7)
    response = chat_model.invoke(message_create(prompt))
    return response.content

# ---------------------- PROCESSING ----------------------
def process_documents(docs):
    if not docs:
        st.error("❌ No documents found to process.")
        return False

    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ".", " "],
        chunk_size=3000,
        chunk_overlap=100
    )
    docs = text_splitter.split_documents(docs)

    if not docs:
        st.error("❌ Document splitting failed. No chunks were created.")
        return False

    st.write(f"📄 Total chunks created: {len(docs)}")

    embeddings = OpenAIEmbeddings()
    try:
        vector_store = FAISS.from_documents(docs, embeddings)
    except IndexError:
        st.error("❌ Failed to create FAISS index. Possibly no valid embeddings were generated.")
        return False

    with open(FILE_PATH, "wb") as fb:
        pickle.dump(vector_store, fb)

    return True

def process_from_urls(urls):
    try:
        loader = UnstructuredURLLoader(urls=urls)
        docs = loader.load()
    except Exception as e:
        st.error(f"❌ Error loading from URLs: {e}")
        return False

    return process_documents(docs)

def process_from_files(uploaded_files):
    all_docs = []
    for uploaded_file in uploaded_files:
        try:
            if uploaded_file.name.endswith(".txt"):
                text = uploaded_file.read().decode("utf-8")
                if text.strip():
                    docs = [Document(page_content=text, metadata={"source": uploaded_file.name})]
                else:
                    st.warning(f"{uploaded_file.name} is empty.")
                    continue
            elif uploaded_file.name.endswith(".pdf"):
                with open("temp_file.pdf", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                loader = PyMuPDFLoader("temp_file.pdf")
                docs = loader.load()
            else:
                st.warning(f"Unsupported file type: {uploaded_file.name}")
                continue
            all_docs.extend(docs)
        except Exception as e:
            st.error(f"Error processing file {uploaded_file.name}: {e}")
    return process_documents(all_docs)

# ---------------------- QUIZ GENERATION ----------------------
def generate_quiz(topic, quiz_type="MCQ", num_questions=5):
    if not os.path.exists(FILE_PATH):
        st.error("❌ No processed data found. Please process documents first.")
        return None

    with open(FILE_PATH, "rb") as f:
        vectorstore = pickle.load(f)

    retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
    retrieved_docs = retriever.get_relevant_documents(topic)

    if not retrieved_docs:
        st.error("❌ No relevant content found for the given topic.")
        return None

    combined_text = "\n".join(doc.page_content for doc in retrieved_docs)

    prompt = generate_prompt(combined_text, quiz_type, num_questions)
    quiz = get_quiz(prompt)
    return quiz

# ---------------------- STREAMLIT UI ----------------------
st.set_page_config(page_title="🧠 Smart Quiz Generator", layout="wide")
st.markdown("<h1 style='text-align: center;'>🧠 Smart Quiz Generator</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Generate quizzes from your own documents or web content using GPT-4</p>", unsafe_allow_html=True)
st.markdown("---")

tab1, tab2 = st.tabs(["📂 Process Content", "📝 Generate Quiz"])

# ----------- TAB 1 ------------
with tab1:
    st.subheader("📄 Add Content")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**🔗 Paste Web URLs**")
        urls = st.text_area("One URL per line")

    with col2:
        st.markdown("**📤 Upload Files**")
        uploaded_files = st.file_uploader("Upload PDFs or TXT files", type=["pdf", "txt"], accept_multiple_files=True)

    if st.button("🚀 Process Content"):
        processed = False
        if urls.strip():
            url_list = [u.strip() for u in urls.split("\n") if u.strip()]
            processed = process_from_urls(url_list)
        if uploaded_files:
            processed = process_from_files(uploaded_files)
        if processed:
            st.success("✅ Content successfully processed and stored! Now go to the quiz generation section to create a quiz.")

# ----------- TAB 2 ------------
with tab2:
    st.subheader("🎯 Quiz Settings")
    st.markdown("Customize your quiz below:")

    col1, col2, col3 = st.columns(3)

    with col1:
        topic = st.text_input("🔍 Topic", placeholder="e.g., Linear Regression")

    with col2:
        quiz_type = st.selectbox("📘 Quiz Type", ["MCQ", "True/False", "Fill-in-the-Blank"])

    with col3:
        num_questions = st.number_input("❓ Number of Questions", min_value=1, max_value=50, value=5)

    if st.button("✨ Generate Quiz"):
        if topic.strip() == "":
            st.warning("⚠️ Please enter a topic for the quiz.")
        else:
            with st.spinner("Generating quiz..."):
                quiz = generate_quiz(topic, quiz_type, num_questions)
                if quiz:
                    st.success("✅ Quiz generated!")
                    st.subheader("📋 Your Quiz")
                    st.text_area("Quiz Output", quiz, height=300)
                    st.download_button("📥 Download Quiz", quiz, file_name=f"{topic.replace(' ', '_')}_quiz.txt")
