import random
import time
import streamlit as st
from code_rag.rag import QA
import sqlite3
import json

class ChatBot:
    def __init__(self):
        self.messages = []
        self.type=0
        self.id=1
        self.answer = []
        self.but = 0
        self.set_num = -999

    # 글자 타이핑 되도록 이펙트
    def stream_data(self, text):
        st.toast("답변 생성중입니다......")
        for word in text.split(" "):
            yield word + " "
            time.sleep(0.2)

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
                    print(res, index)
                    ind = str(self.id) + '_' + str(index)
                    if st.button(res, key=f"question_{ind}", type="primary"):
                        cursor.execute("SELECT * FROM button WHERE question=?", (res,))
                        self.answer = cursor.fetchone()
                        if self.answer[4]==2:
                            self.messages.append({"role": "user", "content": res})
                            self.type = 1
                        else:
                            self.but = 1
                            text = response
                            assis_res = {"text": [text, res], 'image': None}
                            self.messages.append({"role": "assistant", "content": assis_res, "answer_type": answer_type})
                            self.messages.append({"role": "user", "content": res})
                else:
                    if self.answer:
                        self.set_num = self.answer[0]

            # 활성화한 버튼 id 저장
            if self.set_num != -999:
                self.id = self.set_num
            # button 작동 여부 체크
            if self.but:
                self.but=0
                st.rerun()
        else:
            self.type = 1
            text = json.loads(result[2])[0]
            image_paths = json.loads(result[3])
            res = {"text": text, "image": image_paths}
            question = result[1]
            answer_type='image'
            # self.messages.append({"role": "user", "content": question})
            self.messages.append({"role": "assistant", "content": res, "answer_type": answer_type})

            with st.chat_message("assistant"):
                st.write_stream(response)
                with st.expander("Click to view images"):
                    if len(image_paths) != 0:
                        cols = st.columns(len(image_paths))
                        for i, image_path in enumerate(image_paths):
                            with cols[i]:
                                st.image(image_path)
            
            self.handle_user_input(answer_type)

    def display_chat_history(self):
        for message in self.messages:
            with st.chat_message(message["role"]):
                content = message["content"]
                if message["role"]=='assistant':
                    if message['answer_type']=='image':
                        st.markdown(content["text"])
                    else:
                        for _, res in enumerate(content['text'][0]):
                            if res != content['text'][1]:
                                st.button(res)
                            else:
                                st.button(res, type="primary")
                else:
                    st.markdown(content)
                
                if message["role"]=='assistant' and content["image"] != None and message["answer_type"] == "image":
                    image_paths = content["image"]
                    if len(image_paths) != 0:
                        with st.expander("Click to view images"):
                            cols = st.columns(len(image_paths))
                            for i, image_path in enumerate(image_paths):
                                with cols[i]:
                                    st.image(image_path)

    def handle_user_input(self, answer_type):
        user_input = st.text_input("질문할 내용을 적어주세요: ", key="user_input")
        if user_input:
            st.chat_message("user").write(user_input)
            st.toast("서칭 중......")
            self.messages.append({"role": "user", "content": user_input})
            assistant_response = QA(user_input)

            res = []
            for i in assistant_response['source_documents']:
                image_path = i.to_json()['kwargs']['metadata']['img_url']
                res += image_path
            res = [sub.replace('./image', '/llm_img') for sub in res]
            assistant_response = {"text": assistant_response['result'], "image": res}
            self.messages.append({"role": "assistant", "content": assistant_response, "answer_type": answer_type})

            st.toast('Yeaaaaaaaaah',  icon='🎉')
            with st.chat_message("assistant"):
                st.write_stream(self.stream_data(assistant_response["text"]))
                with st.expander("Click to view images"):
                    if assistant_response["image"]!= None:
                        image_paths = assistant_response["image"]
                        if len(image_paths) != 0:
                            cols = st.columns(len(image_paths))
                            for i, image_path in enumerate(image_paths):
                                with cols[i]:
                                    st.image(image_path)

    def run(self):
        print("START")
        st.title("My Small Javis")
        if len(self.messages) == 0:
            print("First if IN")
            answer_type = "button"
            self.display_question_buttons(answer_type)

        print("First if AFTER")
        self.display_chat_history()
        if len(self.messages) > 0:
            print("Second if IN")
            last_message = self.messages[-1]
            answer_type = last_message.get("answer_type", "image")
            if self.type==0:
                print("Third if IN")
                answer_type = "button"
                self.display_question_buttons(answer_type)
            else:
                print("Forth if IN")
                answer_type="image"
                self.handle_user_input(answer_type)
        print("END")

if "chat_bot" not in st.session_state:
    st.session_state.chat_bot = ChatBot()

st.session_state.chat_bot.run()