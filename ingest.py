import argparse
import glob
import os
import pickle

from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.embeddings import HuggingFaceEmbeddings, OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS

def _convert_to_uf8(file_path):
    # Only process Markdown files that are not already encoded in UTF-8
    with open(file_path, 'rb') as f:
        data = f.read()

    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError:
        # If the file is not already UTF-8 encoded, decode it using the correct encoding
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(data.decode('iso-8859-1'))
            print(f"Converted to utf-8: {file_path}")
    else:
        # If the file is already encoded in UTF-8, do nothing
        pass

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--openai-embeddings", action="store_true", help="Use OpenAI embeddings")
    return parser.parse_args()

def ingest_docs():
    args = parse_arguments()
    folder_path = os.environ.get("MARKDOWN_FILES")

    if not folder_path:
        print("Error: MARKDOWN_FILES environment variable is not set.")
        return

    if not os.path.exists(folder_path):
        print(f"Error: {folder_path} does not exist.")
        return

    markdown_files = []
    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in dirs if not d.startswith('.')]
        for file in files:
            if file.endswith(".md"):
                markdown_files.append(os.path.join(root, file))

    vectorstore_path = os.path.join(folder_path, "vectorstore.pkl")
    if os.path.exists(vectorstore_path):
        vectorstore_mtime = os.path.getmtime(vectorstore_path) if os.path.exists(vectorstore_path) else 0
        markdown_files = [file for file in markdown_files if os.path.getmtime(file) > vectorstore_mtime]
        print(f"Vector store detected, ingesting {len(markdown_files)} new files")
    else:
        print(f"Creating new vector store, ingesting {len(markdown_files)} files:")

    # Loop through each markdown file, read the contents, and add it as a document to the vector store
    documents = []
    for file_path in markdown_files:
        try:
            _convert_to_uf8(file_path)
            with open(file_path, "r") as f:
                print(file_path)
                loader = UnstructuredMarkdownLoader(file_path)
                raw_documents = loader.load()
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000,
                    chunk_overlap=200,
                )
                documents_chunks = text_splitter.split_documents(raw_documents)
                for document in documents_chunks:
                    documents.append(document)
        except Exception as e:
            print(f"Error loading file: {file_path}, error: {e}")
            continue

    # Create vector store
    if documents:
        if args.openai_embeddings:
            print("Generating OpenAI embeddings...")
            embeddings = OpenAIEmbeddings()
        else:
            print("Generating local embeddings...")
            embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
        vectorstore = FAISS.from_documents(documents, embeddings)
        if os.path.exists(vectorstore_path):
            # Make an incremental adding just with new documents if a vector store already exists
            with open(vectorstore_path, "rb") as f:
                vectorstore = pickle.load(f)
                tmp_new_docs_vectorstore = FAISS.from_documents(documents, embeddings)
                vectorstore.merge_from(tmp_new_docs_vectorstore)
        else:
            vectorstore = FAISS.from_documents(documents, embeddings)

        # Save vectorstore
        with open(vectorstore_path, "wb") as f:
            pickle.dump(vectorstore, f)

if __name__ == "__main__":
    ingest_docs()
