from typing import Union
from fastapi import FastAPI, Depends
from starlette.middleware.sessions import SessionMiddleware
from PIL import Image
import os
import io
from io import BytesIO
import uvicorn
import asyncio

import base64

from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from fastapi.responses import StreamingResponse, Response
from transformers import pipeline
from rag.car_manual_bot import car_manual_generator

from fastapi.responses import JSONResponse
from fastapi_sessions.backends.implementations import InMemoryBackend
from fastapi_sessions.session_verifier import SessionVerifier
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters

os.environ["LANGCHAIN_TRACING_V2"]="true"
os.environ["LANGCHAIN_ENDPOINT"]="https://api.smith.langchain.com"
# TODO: LangChain API Key
os.environ["LANGCHAIN_API_KEY"]="LangChain API Key"
os.environ["LANGCHAIN_PROJECT"]="my-small_mechanic"

# TODO: OpenAI API Key
os.environ['OPENAI_API_KEY'] = 'OpenAI API Key'
os.environ['MILVUS_PORT'] = '19530'

# milvus_host = 'localhost'
# TODO:EC2 SERVER IP
milvus_host = 'EC2 SERVER IP'
milvus_port = os.environ["MILVUS_PORT"]

DB_COLLECTION_NAME = "HYNDAI_CAR_MANUAL"
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']
NAMESPACE_TYPE = ["IONIQ5_2024", "SANTAFE_MX5_2024", "SONATA_DN8_2024"]
# NAMESPACE = NAMESPACE_TYPE[0]

# TODO: Context Path
CONTEXT_PATH = 'Context Path'
device='cpu'
reranker = pipeline("text-classification", model="Dongjin-kr/ko-reranker", device=device)


app = FastAPI()

def from_image_to_bytes(img):
    """
    pillow image 객체를 bytes로 변환
    """
    # Pillow 이미지 객체를 Bytes로 변환
    imgByteArr = io.BytesIO()
    img.save(imgByteArr, format=img.format)
    imgByteArr = imgByteArr.getvalue()
    # Base64로 Bytes를 인코딩
    encoded = base64.b64encode(imgByteArr)
    # Base64로 ascii로 디코딩
    decoded = encoded.decode('ascii')
    return decoded

@app.get("/")
async def read_root(id:int, namespace:str):
    return
    

@app.get("/aget_car_information/")
async def agenerate_car_manual_answer(namespace: str, query: str, session_id: str):
    stream_it = AsyncIteratorCallbackHandler()
    text_generator = car_manual_generator(OPENAI_API_KEY, namespace, milvus_host, milvus_port, DB_COLLECTION_NAME, 10, rrk_weight=(0, 1),
                                score_filter=True, threshold=0.3, drop_duplicates=True, context_path=CONTEXT_PATH, reranker=reranker)

    # 멀티파트 응답 생성
    boundary = "my-custom-boundary"

    async def generate_response():
        task = asyncio.create_task(text_generator._agenerate_answer(query, session_id, stream_it))
        async for chunk in stream_it.aiter():
            print(chunk)
            yield (f"{boundary}\r\n"
                   f"Content-Type: text/event-stream\r\n\r\n"
                   f"{chunk}").encode("utf-8")
        if not task.done():
            await task
        # get the return value from the wrapped coroutine
        answer, context_bag = task.result()
        
        if (len(context_bag['image_urls'])!=0) or (len(context_bag['table_image_urls'])!=0):
            image = str(context_bag['image_urls'] + context_bag['table_image_urls'])
        # image = str(['./image/너구리.jpg'])
            yield (f"{boundary}\r\n"
                    f"Content-Type: text/plain\r\n\r\n"
                    f"{image}").encode("utf-8")

    # 응답 반환
    return StreamingResponse(generate_response(), media_type=f"multipart/form-data; boundary={boundary}")

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

if __name__ == "__main__" :
	uvicorn.run("main:app", reload=True)