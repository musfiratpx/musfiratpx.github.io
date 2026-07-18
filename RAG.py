import os #this is a script written by gemini.
from langchain_community.document_loaders import PyPDFDirectoryLoader, WikipediaLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
import requests

# get and chunk data
print("Loading data sources...")

def download_nasa_pdfs(query, max_results=20):
    if not os.path.exists("./docs"):
        os.makedirs("./docs")
        
    url = "https://ntrs.nasa.gov/api/citations/search"
    params = {"q": query, "rows": max_results}
    results = requests.get(url, params=params).json()
    
    for doc in results["results"]:
        doc_id = doc["id"]
        pdf_url = f"https://ntrs.nasa.gov/api/citations/{doc_id}/downloads/{doc_id}.pdf"
        r = requests.get(pdf_url)
        if r.status_code == 200:
            with open(f"./docs/{doc_id}.pdf", "wb") as f:
                f.write(r.content)
            print(f"Downloaded {doc_id}.pdf")
        else:
            print(f"Skipped {doc_id} (no PDF available)")

download_nasa_pdfs("spiral galaxies", max_results=5)
download_nasa_pdfs("geometry", max_results=5)

pdf_loader = PyPDFDirectoryLoader("./docs/")
# all data in folder named 'docs'
if not os.path.exists("./docs"):
    os.makedirs("./docs")
pdf_documents = pdf_loader.load()

# wikipedia pages
wiki_queries = [
    "Fibonacci sequence",
    "Golden ratio",
    "Spiral galaxy",
    "Logarithmic spiral",
    "Timeline of cosmological theories"
]

wiki_documents = []
for q in wiki_queries:
    try:
        loader = WikipediaLoader(query=q, load_max_docs=2)
        wiki_documents.extend(loader.load())
        print(f"Loaded wiki context for: {q}")
    except Exception as e:
        print(f"Skipped wiki query {q}: {e}")

all_docs = pdf_documents + wiki_documents

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=150,
    separators=["\n\n", "\n", " ", ""]
)
final_chunks = text_splitter.split_documents(all_docs)

# labeling source data if missing
for chunk in final_chunks:
    if "source" not in chunk.metadata:
        chunk.metadata["source"] = "Local Space-Math Archive"

# embeddings and vector storage
print("Embedding text chunks locally via Hugging Face...")
hf_embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

#chroma database
vector_store = Chroma.from_documents(
    documents=final_chunks,
    embedding=hf_embeddings,
    persist_directory="./free_space_db"
)
retriever = vector_store.as_retriever(search_kwargs={"k": 3})

# RAG prompt. for now, I want to use a chatbot system just to see how this can work.
system_prompt_template = """
You are an entity who researches theories and connections already created by humans surrounding mathematics, space, and time.
Your core directive is provide the user an accurate and well-sourced theory that has to do with math and space.
You must use ONLY verfied sources and context. You will respond in a short 5-7 sentence paragraph.

CRITICAL INSTRUCTIONS FOR ACCURACY AND TRUTH:
1. DO NOT MAKE THINGS UP. Do not attempt to guess or extrapolate or create false theories or information.
2. MANDATORY SOURCE CITATION: For every claim, equation, or theory you state, you MUST cite its specific source file path or website title from the context metadata. Use inline formatting, e.g., (Source: docs/nasa_paper.pdf) or (Source: Wikipedia).
3. MATHEMATICAL ACCURACY: Keep LaTeX notations intact exactly as given.

Context provided for generation:
---------------------
{context}
---------------------

User Query: {question} 

Academic Answer:"""

prompt = ChatPromptTemplate.from_template(system_prompt_template)

# initialize llm
print("Connecting to local Ollama instance...")
local_llm = Ollama(model="llama3", temperature=0.0)

def format_docs(docs):
    formatted = []
    for doc in docs:
        source_name = doc.metadata.get('source', 'Unknown Source')
        page_num = doc.metadata.get('page', '')
        page_info = f", Page {page_num}" if page_num else ""
        formatted.append(f"Content: {doc.page_content}\n[Source Metadata: {source_name}{page_info}]\n---")
    return "\n\n".join(formatted)

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | local_llm
    | StrOutputParser()
)

# execution
print("\n--- RAG Pipeline Ready ---")
query = "Tell me about how the fibonacci sequence relates to the golden ratio, and also space."
response = rag_chain.invoke(query)

print("\nResult:\n", response)