"""Load html from files, clean up, split, ingest into Weaviate."""
import glob
import os
import pickle

from langchain.document_loaders import UnstructuredMarkdownLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores.faiss import FAISS


def ingest_docs():
    # Get the folder path from the MARKDOWN_FILES environment variable
    folder_path = os.environ.get("MARKDOWN_FILES")

    # Check if the folder_path is None or empty
    if not folder_path:
        print("Error: MARKDOWN_FILES environment variable is not set.")
        return

    # Check if the folder_path exists
    if not os.path.exists(folder_path):
        print(f"Error: {folder_path} does not exist.")
        return
    
    # Get a list of all the markdown files in the folder and subfolders recursively
    markdown_files = []
    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".md"):
                markdown_files.append(os.path.join(root, file))
    print("Ingesting files:")

    # Loop through each markdown file, read the contents, and add it as a document to the vector store
    documents = []
    for file_path in markdown_files:
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

    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(documents, embeddings)

    # Save vectorstore
    with open("vectorstore.pkl", "wb") as f:
        pickle.dump(vectorstore, f)



if __name__ == "__main__":
    ingest_docs()



if __name__ == "__main__":
    ingest_docs()
