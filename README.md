# brAIn

This repo is an implementation of a locally hosted chatbot specifically focused on question answering over my docs (markdown files).
Built with [LangChain](https://github.com/hwchase17/langchain/) and [FastAPI](https://fastapi.tiangolo.com/).

The app leverages LangChain's streaming support and async API to update the page in real time for multiple users (like ChatGPT)

## ✅ Running locally

1. Install dependencies: `pip install -r requirements.txt`
2. set `MARKDOWN_FILES` env var with the path to your source files

   ```
   export MARKDOWN_FILES="<path to your source files>
   ```

3. Run `make ingest` or `make ingest-openai` to ingest markdown docs into the vectorstore (only needs to be done once).

4. Run the app: `make run` or just `make`
  
5. Open [localhost:9000](http://localhost:9000) in your browser.

## 🚀 Important Links

This project is based on the original [LangChain chat client example](https://github.com/hwchase17/chat-langchain)

Blog Posts:

* [Initial Launch](https://blog.langchain.dev/langchain-chat/)
* [Streaming Support](https://blog.langchain.dev/streaming-support-in-langchain/)

## 📚 Technical description

There are two components: ingestion and question-answering.

Ingestion has the following steps:

1. Load markdown files with LangChain's [UnstructuredMarkdownLoader](https://python.langchain.com/en/latest/modules/indexes/document_loaders/examples/markdown.html)
2. Split documents with LangChain's [TextSplitter](https://langchain.readthedocs.io/en/latest/reference/modules/text_splitter.html)
3. Create a vectorstore of embeddings, using LangChain's [vectorstore wrapper](https://langchain.readthedocs.io/en/latest/reference/modules/vectorstore.html) (with local embeddings or OpenAI's embeddings and FAISS vectorstore) to provide a mapping between documents and their corresponding embeddings, which can be used to retrieve the most relevant documents based on a similarity search using the embeddings.

Question-Answering has the following steps, all handled by [ConversationalRetrievalChain](https://python.langchain.com/en/latest/modules/chains/index_examples/chat_vector_db.html):

1. Given the chat history and new user input, determine what a standalone question would be (using GPT-3.5).
2. Given that standalone question, look up relevant documents from the vectorstore.
3. Pass the standalone question and relevant documents to GPT-3 to generate a final answer.
