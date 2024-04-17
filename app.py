import random
import time
import streamlit as st
from code_rag.rag import QA

class ChatBot:
    def __init__(self):
        self.messages = []
        self.sample_questions = [
    {
        "question": "전조등이 이상이 있을 때에는 어떻게 해?", 
        "response": (
            "Some popular tourist destinations are:", 
            [
                "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEi6d1r7s7ztBLqRrAwWcGyJuBPiDavc3pWnK31RO4dDtdryNcuzSZoDpaARvlLoLyUhyd08SCoVxMgre4avZ1CfuDb1ZLJIc8WSGGhO2abVG_VXq2cdiwCzUiAEYRISDCKMOzDiWZRbGQvWB5lbgsXS57i7iBYkGsc2bnhhaFk5vEpiJaKcb-yG02wa/s728-rw-e365/malware.jpg",
                "https://www.lrt.lt/img/2022/02/09/1191080-981331-756x425.jpg",
                "https://img1.daumcdn.net/thumb/R1280x0/?scode=mtistory2&fname=https%3A%2F%2Fblog.kakaocdn.net%2Fdn%2FpqxXh%2FbtryMmIqGyE%2Fe8Hj032ki0BlcaoNAUQHw1%2Fimg.webp"
            ], "image"
        )
        
    },
     {
        "question": "What are some popular tourist destinations?", 
        "response": (
            "Some popular tourist destinations are:", 
            None, "image"
        )
    },
    {
        "question": "What are some popular tourist destinations?", 
        "response": (
            "Some popular tourist destinations are:", 
            [
                "https://i.namu.wiki/i/ESJaxFoXfpmIKxDWddb_RhaeRvurnnKi9Mbjy8lcbGj4c93xonvOHtAft4OKKnk6tlWPxYfY9S5XxZUOU3gw9FVHBfcnkr1FCy7HjrsX8w8tEJ3TAfPHSIZ_kOcUAptpIsRMa-u-aGkdbZseOtrM5w.webp", 
                "https://i.namu.wiki/i/CM5hlP9b2YPEFiwPWiCQFoLsEOezKLMPXl8Ue30yp8ikXb1mAOCmYICkzuRfX8a6IA3eZ0Cf495sdpS0pMRs5oQnDbZYDaAujc8gktqQBiqaQlFeTZJomhVrjTslbOlGjnl9OR_aV7u4Ndf-H-M2Jw.webp", 
                "https://i.namu.wiki/i/x1fgDyNxD879zmWyVo70Cbq3YC0kr2cgeZaFys99g9j3wzAdYHGGPVfnZLwp5EHP0CELBjkn-mWVj8HUUHYbHIN-or4qSBYhXrXfmKXLZfl01uhgjxB8DEjnS93JSgp1PqKKSgr4WTrWyH6eRkh4Eg.webp"
            ], "button"
        )
    },
        ]

    # def response_generator(self, text, image_paths):
    #     if image_paths==None:
    #         image_paths=''
    #     response = f"{text}|{','.join(image_paths)}"
    #     for word in response.split():
    #         yield word + " "
    #         time.sleep(0.05)

    # Button 클릭 시 작동
    def display_question_buttons(self):
        st.write("Please select a question:")
        for index, question in enumerate(self.sample_questions):
            if st.button(question["question"], key=f"question_{index}"):
                self.messages.append({"role": "user", "content": question["question"]})
                text, image_paths, answer_type = question["response"]
                answer = QA(question["question"])
                res = []
                for i in answer['source_documents']:
                    image_path = i.to_json()['kwargs']['metadata']['img_url']
                    res += image_path
                res = [sub.replace('./image', '/llm_image') for sub in res]
                print("Save Response when click button")
                print(answer.keys())
                response = {"text": answer['result'], "image": res}
                
                self.messages.append({"role": "assistant", "content": response, "answer_type": answer_type})
                break

    def display_chat_history(self):
        for message in self.messages:
            with st.chat_message(message["role"]):
                content = message["content"]
                if message["role"]=='assistant':
                    print("displayChat: content")
                    print(content)
                    st.markdown(content["text"])
                else:
                    st.markdown(content)
                
                if message["role"]=='assistant' and content["image"] != None and message["answer_type"] == "image":
                    image_paths = content["image"]
                    with st.expander("Click to view images"):
                        cols = st.columns(len(image_paths))
                        for i, image_path in enumerate(image_paths):
                            print("#1 Image Path")
                            print(image_path)
                            with cols[i]:
                                st.image(image_path)

    def handle_user_input(self, answer_type):
        user_input = st.text_input("Your message:", key="user_input")
        if user_input:
            st.chat_message("user").write(user_input)
            self.messages.append({"role": "user", "content": user_input})

            assistant_response = QA(user_input)
            res = []
            for i in assistant_response['source_documents']:
                image_path = i.to_json()['kwargs']['metadata']['img_url']
                res += image_path
            res = [sub.replace('./image', '/llm_image') for sub in res]

            assistant_response = {"text": assistant_response['result'], "image": res}
            self.messages.append({"role": "assistant", "content": assistant_response, "answer_type": answer_type})
            with st.chat_message("assistant"):
                st.markdown(assistant_response["text"])
                time.sleep(1)
                with st.expander("Click to view images"):
                    if assistant_response["image"]!= None:
                        image_paths = assistant_response["image"]
                        cols = st.columns(len(image_paths))
                        for i, image_path in enumerate(image_paths):
                            with cols[i]:
                                st.image(image_path)

    def run(self):
        st.title("My Small Javis")
        if len(self.messages) == 0:
            self.display_question_buttons()
        else:
            last_message = self.messages[-1]
            answer_type = last_message.get("answer_type", "image")
            if answer_type == "button":
                self.display_question_buttons()
        self.display_chat_history()
        if len(self.messages) > 0:
            last_message = self.messages[-1]
            answer_type = last_message.get("answer_type", "image")
            self.handle_user_input(answer_type)


if "chat_bot" not in st.session_state:
    st.session_state.chat_bot = ChatBot()

st.session_state.chat_bot.run()