import random
import time
import streamlit as st
from code_rag.rag import QA
import sqlite3
import json
import ast
import os

from langchain.agents import initialize_agent
from langchain.agents.tools import Tool
from langchain.chains import LLMChain
from langchain.callbacks import StreamlitCallbackHandler
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import RedisChatMessageHistory

import httpx
import asyncio
from httpx import TimeoutException

import redis

# TODO: Put Redis Server
REDIS_URL = "REDIS SERVER URL"
session_id = "999"

async def get_streaming_response(namespace, query, session_id):
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream('GET', 'http://localhost:8000/aget_car_information/', params={'namespace': namespace, 'query': query, 'session_id': session_id}) as response:
            async for chunk in response.aiter_text():
                yield chunk

class ChatBot():
    def __init__(self, personal_id=999):
        self.messages = []
        self.type=0
        self.id=1
        self.answer = []
        self.set_num = -999
    def reset_chat(self, personal_id):
        st.session_state.chat_bot = ChatBot(personal_id)
        st.rerun()

    def reset_button(self):
        self.type = 0
        self.set_num=-999
        self.id = 1
        self.answer = []

    def reset_messages(self, r, redis_messages):
        self.messages=[]
        key = [key for key in st.session_state.key_list if b'image' in key and st.session_state.key in key]
        val = []
        if len(key)==1:
            result = list(reversed(r.lrange(key[0], 0, -1)))
            result = [json.loads(item.decode('utf-8')) for item in result]

            for res in result:
                image = ast.literal_eval(res['data']['content'])
                val.append(image)

        else:
            # key는 하나여야만 함
            print('FAIL: Too Many Keys')

        for ind, mes in enumerate(redis_messages):
            content = {}
            content['text']=mes
            if ind%2:
                if len(val)!=0:
                    content['image'] = val[ind//2]
                else: 
                    content['image'] = []
                self.messages.append({"role": "assistant", "content": content, "answer_type": 'image'})
            else:
                content['image'] = []
                self.messages.append({"role": "user", "content": content, "answer_type": 'image'})
        return
    
    # Button 클릭 시 작동
    def display_question_buttons(self, answer_type):
        conn = sqlite3.connect('button.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM button WHERE id=?", (self.id,))
        result = cursor.fetchone()
        response = json.loads(result[2])
        
        if result[4] == 0:
            with st.chat_message("assistant"):
                for index, res in enumerate(response):
                    ind = str(self.id) + '_' + str(index)

                    if st.button(res, key=f"question_{ind}", type="primary"):
                        st.session_state.clicked = True
                        cursor.execute("SELECT * FROM button WHERE question=?", (res,))
                        self.answer = cursor.fetchone()
                        if self.answer[4]==2:
                            user_res = {"text": res, 'image': []}
                            self.messages.append({"role": "user", "content": user_res})
                            self.type = 1
                        else:
                            
                            text = response
                            assis_res = {"text": [text, res], 'image': []}
                            self.messages.append({"role": "assistant", "content": assis_res, "answer_type": answer_type})
                            user_res = {"text": res, 'image': []}
                            self.messages.append({"role": "user", "content": user_res})
                else:
                    if self.answer:
                        self.set_num = self.answer[0]
            if self.set_num != -999:
                self.id = self.set_num
            if st.session_state.clicked:
                st.session_state.clicked = False
                st.rerun()
        else:
            self.type = 1
            text = json.loads(result[2])[0]
            image_paths = json.loads(result[3])
            res = {"text": text, "image": image_paths}
            # question = result[1]
            answer_type='image'
            self.messages.append({"role": "assistant", "content": res, "answer_type": answer_type})
            with st.chat_message("assistant"):
                
                st.write_stream(response)
                with st.expander("Click to view images"):
                    if len(image_paths) != 0:
                        cols = st.columns(len(image_paths))
                        for i, image_path in enumerate(image_paths):
                            with cols[i]:
                                st.image(image_path)
            asyncio.run(self.handle_user_input(answer_type))

    def display_chat_history(self):
        for message in self.messages:
            with st.chat_message(message["role"]):
                content = message["content"]
                if message["role"]=='assistant':
                    if message['answer_type']=='image':
                        st.markdown(content["text"])
                    else:
                        for index, res in enumerate(content['text'][0]):
                            if res != content['text'][1]:
                                st.button(res)
                            else:
                                st.button(res, type="primary")
                else:
                    st.markdown(content["text"])
                
                if message["role"]=='assistant' and content["image"] != None and message["answer_type"] == "image":
                    image_paths = content["image"]
                    if len(image_paths) != 0:
                        with st.expander("Click to view images"):
                            if len(image_paths)<4:
                                cols = st.columns(len(image_paths))
                            else:
                                cols = st.columns(4)
                            for i, image_path in enumerate(image_paths):
                                with cols[i%4]:
                                    st.image(image_path)

    async def handle_user_input(self, answer_type):

        col1, col2 = st.columns([8.5,1.5])
        with col1:
            user_input = st.chat_input("질문할 내용을 적어주세요: ", key="user_input")
        with col2:
            if st.button('버튼 질문', key=f"reset_button", type="primary"):
                answer_type = "button"
                self.reset_button()
                st.rerun()

        if user_input:
            st.chat_message("user").write(user_input)
            st.toast("서칭 중......")
            user_question = {"text": user_input, "image": []}
            self.messages.append({"role": "user", "content": user_question})
            # st.toast('Yeaaaaaaaaah',  icon='🎉')
            with st.chat_message("assistant"):
                
                with st.spinner("Waiting for response..."):
                    try:
                        container = st.empty()
                        # Buffer to store the incoming chunks
                        buffer = b""
                        boundary = b"my-custom-boundary"
                        image_paths = ''
                        answer = ''
                        # Get the streaming response from FastAPI
                        async for chunk in get_streaming_response(st.session_state.car_model, user_input, st.session_state.session_id):
                            buffer += chunk.encode('utf-8')  # chunk를 바이트로 변환
                            parts = buffer.split(boundary)
                            
                            for part in parts:
                                part_data = part.split(b"\r\n\r\n")

                            if len(part_data) >= 2:
                                header, data = part_data[0], part_data[1]

                                if b"Content-Type: text/event-stream" in header:
                                    token = data.decode("utf-8")
                                    answer += token
                                    container.markdown(answer)
                                elif b"Content-Type: text/plain" in header:
                                    image_paths = data.decode('utf-8')  # 이미지 경로를 문자열로 변환  
                        
                        try:
                            image_paths = ast.literal_eval(image_paths)
                            assistant_response = {"text": answer, "image": image_paths}
                        except:
                            assistant_response = {"text": answer, "image": []}
                        
                        with container.container():
                            st.markdown(answer)
                            if len(image_paths) != 0:
                                with st.expander("Click to view images"):
                                    if len(image_paths)<4:
                                        cols = st.columns(len(image_paths))
                                    else:
                                        cols = st.columns(4)
                                    for i, image_path in enumerate(image_paths):
                                        
                                        with cols[i%4]:
                                            st.image(image_path)

                        self.messages.append({"role": "assistant", "content": assistant_response, "answer_type": answer_type})
                    except TimeoutException:
                        pass


    def side_bar(self):
        with st.sidebar:
            
            car_model = st.selectbox(
                "차정",
                ["IONIQ5_2024", "SANTAFE_MX5_2024", "SONATA_DN8_2024"]
            )
            r= redis.Redis(host='43.200.165.177', port=6379)
            st.session_state.car_model = car_model
            key_list = r.keys(f'message_store:{st.session_state.personal_id}*')
            key_list = [key for key in key_list if b'image' not in key]
            print(key_list)
            if len(key_list)>0:
                for index, key in enumerate(key_list, start=1):

                    result = list(reversed(r.lrange(key, 0, -1)))
                    conv = result[-2]
                    first_text = json.loads(conv.decode())['data']['content'][:16]
                    if st.button(f'Chat_{index}: {first_text}', key=f"side_bar_{key}", type="secondary"):
                        # st.session_state.session_id = 
                        st.session_state.clicked = True
                        st.session_state.key = key
                        redis_messages = list(map(lambda conv: json.loads(conv.decode())['data']['content'], result))
                        st.session_state.session_id = f'{st.session_state.personal_id}_{index}' 
                        self.reset_messages(r, redis_messages)
            else:
                index = 0
            st.session_state.max_session = index
            if st.session_state.clicked:
                st.session_state.clicked = False
                # self.type = 1
                st.rerun()
            if st.button("New Chat", key="new_chat"):
                new_session = st.session_state.max_session + 1
                st.session_state.session_id = f'{st.session_state.personal_id}_{new_session}' 
                self.reset_chat(st.session_state.personal_id)
                st.rerun()

    def run(self):
        print("START")
        self.side_bar()
        st.title(f"My Small Javis ver.{st.session_state.car_model}")

        if len(self.messages) == 0:
            answer_type = "button"
            self.display_question_buttons(answer_type)

        self.display_chat_history()
        if len(self.messages) > 0:
            last_message = self.messages[-1]
            answer_type = last_message.get("answer_type", "image")
            if self.type==0:
                answer_type = "button"
                self.display_question_buttons(answer_type)
            else:
                answer_type="image"
                asyncio.run(self.handle_user_input(answer_type))
        print("END")

if "chat_bot" not in st.session_state:
    st.session_state.clicked = False
    st.session_state.personal_id=999
    st.session_state.car_model = 'IONIQ5_2024'

    r= redis.Redis(host='43.200.165.177', port=6379)
    key_list = r.keys(f'message_store:{st.session_state.personal_id}*')
    st.session_state.key_list = key_list
    key_list = [key for key in key_list if b'image' not in key]
    if len(key_list)!=0:
        temp = len(key_list) +1
        st.session_state.session_id = f'{st.session_state.personal_id}_{temp}'
    else:
        st.session_state.session_id = f'{st.session_state.personal_id}_1'
    st.session_state.chat_bot = ChatBot(st.session_state.personal_id)

st.session_state.chat_bot.run()






            # with open("./messages.txt", "w") as file:
            #     file.write(json.dumps(self.messages))