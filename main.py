"""Main entrypoint for the app."""
import logging
import os
import pickle
from collections import OrderedDict
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from langchain.vectorstores import VectorStore

from callback import QuestionGenCallbackHandler, StreamingLLMCallbackHandler
from chain import get_chain
from schemas import ChatResponse

MAX_HISTORY_LENGTH = 100

app = FastAPI()
templates = Jinja2Templates(directory="templates")
vectorstore: Optional[VectorStore] = None

@app.on_event("startup")
async def startup_event():
    logging.info("loading vectorstore")
    if not Path("vectorstore.pkl").exists():
        raise ValueError("vectorstore.pkl does not exist, please run make ingest first")
    with open("vectorstore.pkl", "rb") as f:
        global vectorstore
        vectorstore = pickle.load(f)


@app.get("/")
async def get(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.websocket("/chat")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    question_handler = QuestionGenCallbackHandler(websocket)
    stream_handler = StreamingLLMCallbackHandler(websocket)
    chat_history = []
    qa_chain = get_chain(vectorstore, question_handler, stream_handler)
    # Use the below line instead of the above line to enable tracing
    # Ensure `langchain-server` is running
    # qa_chain = get_chain(vectorstore, question_handler, stream_handler, tracing=True)

    while True:
        try:
            # Receive and send back the client message
            question = await websocket.receive_text()
            resp = ChatResponse(sender="you", message=question, type="stream")
            await websocket.send_json(resp.dict())

            # Construct a response
            start_resp = ChatResponse(sender="bot", message="", type="start")
            await websocket.send_json(start_resp.dict())

            result = await qa_chain.acall(
                {"question": question, "chat_history": chat_history[-MAX_HISTORY_LENGTH:]}
            )

            source_links = OrderedDict()
            for doc in result['source_documents']:
                source = doc.metadata['source']
                source_rel_path = os.path.relpath(source, os.environ.get('MARKDOWN_FILES'))
                obsidian_url = f"obsidian://open?vault={os.path.basename(os.environ.get('MARKDOWN_FILES'))}&file={source_rel_path.replace(os.path.sep, '%2F')}"
                source_link = f"<a href=\"{obsidian_url}\">{source_rel_path}</a>"
                source_links[source_link] = None
            resp = ChatResponse(sender="bot", message='<br>'.join(source_links.keys()), type="sources")
            await websocket.send_json(resp.dict())
            
            chat_history.append((question, result["answer"]))
            if len(chat_history) > MAX_HISTORY_LENGTH:
                chat_history = chat_history[-MAX_HISTORY_LENGTH:]

            end_resp = ChatResponse(sender="bot", message="", type="end")
            await websocket.send_json(end_resp.dict())
        except WebSocketDisconnect:
            logging.info("websocket disconnect")
            break
        except Exception as e:
            logging.error(e)
            resp = ChatResponse(
                sender="bot",
                message="Perdón, algo salió mal. Intentalo de nuevo.",
                type="error",
            )
            await websocket.send_json(resp.dict())



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=9000)
