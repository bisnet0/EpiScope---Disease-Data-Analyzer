import os
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings  # type: ignore


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# 👇 AJUSTE 1: Voltar uma pasta ("..") para achar o 'datasets' que está na raiz do core_agent
KB_DIR = os.path.join(SCRIPT_DIR, "..", "datasets")

# A pasta destino dos artefatos
TRAIN_RESULTS_DIR = os.path.join(SCRIPT_DIR, "train_results")

os.makedirs(TRAIN_RESULTS_DIR, exist_ok=True)

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)


def build_knowledge_base() -> bool:
    """Lê os PDFs, fatia o texto e constrói o banco vetorial FAISS."""
    print(f"\n[RAG] 📚 Iniciando leitura dos PDFs em {KB_DIR}...")

    if not os.path.exists(KB_DIR):
        print(f"[RAG] ❌ Erro: A pasta {KB_DIR} não foi encontrada.")
        return False

    loader = PyPDFDirectoryLoader(KB_DIR)
    docs = loader.load()

    if not docs:
        print("[RAG] ❌ Erro: Nenhum documento encontrado na pasta.")
        return False

    print(
        f"[RAG] ✅ {len(docs)} páginas carregadas. Iniciando fatiamento (chunking)..."
    )

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(docs)

    print(
        f"[RAG] 🧠 Criando banco de dados vetorial FAISS com {len(splits)} fragmentos..."
    )
    vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)

    # 👇 AJUSTE 2: Salva na train_results com o nome 'rag_results'
    vectorstore.save_local(TRAIN_RESULTS_DIR, index_name="rag_results")
    print(
        f"[RAG] 💾 Cérebro médico salvo com sucesso em {TRAIN_RESULTS_DIR}/rag_results.faiss\n"
    )
    return True


def search_knowledge_base(query: str, k: int = 3) -> str:
    """Busca no banco FAISS os k fragmentos mais relevantes para a pergunta."""
    # 👇 Verifica diretamente se o arquivo rag_results.faiss foi gerado
    if not os.path.exists(os.path.join(TRAIN_RESULTS_DIR, "rag_results.faiss")):
        return "Aviso: Banco de conhecimento (FAISS) não encontrado. Inicialize o RAG primeiro."

    # 👇 Carrega apontando para a pasta e pedindo especificamente o index_name="rag_results"
    vectorstore = FAISS.load_local(
        folder_path=TRAIN_RESULTS_DIR,
        embeddings=embeddings,
        index_name="rag_results",
        allow_dangerous_deserialization=True,
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": k})

    docs = retriever.invoke(query)

    results = "\n\n".join(
        [f"--- Trecho Científico ---\n{doc.page_content}" for doc in docs]
    )
    return results


if __name__ == "__main__":
    build_knowledge_base()
