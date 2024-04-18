import random
import time
import streamlit as st
from code_rag.rag import QA

class ChatBot:
    def __init__(self):
        self.messages = []
        self.depth=0
        self.sample_questions = [
            {
                "question": "시동 및 도어", 
                "index": 0,
                "subquestion":["시동버튼 위치","스마트키 원격시동","차 밖에서 문열기","차 안에서 문열기"],
                "response": [('시동버튼은 여기 있습니다',['https://mblogthumb-phinf.pstatic.net/MjAxODA0MTZfNTAg/MDAxNTIzODY3ODcyMzI5.IqNbzCXP56JI5G1cF3YpnqLn2lrbokipOq3Hdnac4T8g.tNVb_rGeukIDA46b-_cNvkaAI9Ut1UacE_b5OMR7Sokg.PNG.0323lena/image_5131097701523867771893.png?type=w800'],'image'),
                ('스마트키 원격시동은 이렇게 하십쇼',['https://i.ytimg.com/vi/fImEZifLV9U/maxresdefault.jpg'],'image'),
                ('차 밖에서 문열기는 요러케',['https://mblogthumb-phinf.pstatic.net/MjAyMzA0MTJfNCAg/MDAxNjgxMjc5OTEwMTkx.I2hdGumdsJlugAhkRm5WVGFhYnHOw0G-uDI2fXr90aQg.W8Bf8KL6gcHf_96ZAtXmLekQcdqvP88ee0Rd4PgweyUg.JPEG.cyg0703nani/IMG_7052.jpg?type=w800'],'image'),
                ('차 안에서 문열기는 요러케',['https://i.ytimg.com/vi/kxslSjObGD8/maxresdefault.jpg'],'image'),
                
                ]
            },
            {
                "question": "장치", 
                "index": 1,
                "subquestion":["후면 트렁크 열고닫기","전면 트렁크 열고닫기","변속기 조절하기"],
                "response": [('후면 트렁크 열기 버튼을 누르고 위로 올리면 열려요',['https://www.tesla.com/ownersmanual/images/GUID-0C9CE425-C8ED-4ACB-8178-94BB7CF46C3E-online-en-US.png'],'image'),
                ('전면 트렁크 열기 버튼을 누르고 위로 올리면 열려요',['https://www.tesla.com/ownersmanual/images/GUID-64C680DF-1B33-4182-9D23-E0E33CBAF8BB-online-en-US.png'],'image'),
                ('변속기 다이얼 돌리쇼',['https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSSbqUmq4ZVKPhtDzcEG1US0OHDdYN2lwrFQT95txr21A&s'],'image'),
                ]
            },
            {
                "question": "주유/충전", 
                "index": 2,
                "subquestion":["충전 도어 열고닫기","충전방법"],
                "response": [('번호판 옆 등같은거 불쑥 튀어나온거 있음',['https://image.edaily.co.kr/images/Photo/files/NP/S/2021/03/PS21031900347.jpg'],'image'),
                ('충전단자에 충전기 연결하자',['https://image.kmib.co.kr/online_image/2022/1111/2022111115563193052_1668149791_0017662886.jpg'],'image'),
                ]
            },
            {
                "question": "주행", 
                "index": 3,
                "subquestion":["예시1","예시2",'예시3'],
                "response": [('예시1에 대한 답변',['https://wimg.mk.co.kr/meet/neds/2021/04/image_readtop_2021_394003_16191864794622251.jpg'],'image'),
                ('예시2에 대한 답변',['https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSFx7KFdMLb_2xlP2c9HejBVm_0dBmhoUnljbgSF3BwNGCz4CR8Ne0awnO8wpKj7AVGfvE&usqp=CAU'],'image'),
                ('예시3에 대한 답변',['https://img.newspim.com/news/2021/02/24/2102241101533320.jpg'],'image'),
                ]
        
            }      
        ]

    def stream_data(self, text):
        st.toast("답변 생성중입니다......")
        for word in text.split(" "):
            yield word + " "
            time.sleep(0.2)

    def display_subquestion_buttons(self):
        if "selected_question" not in st.session_state:
            return
        selected_question = st.session_state.selected_question
        par_ind = selected_question["index"]

        if selected_question is None:
            return
        subquelist = selected_question["subquestion"]
        for ind2, subquestion in enumerate(subquelist):
            ind = f'{par_ind}_{ind2}'
            print(ind)
            print(subquestion)
            if st.button(subquestion, key=f"subquestion_{ind}"):
                print('isin?')
                self.messages.append({"role": "user", "content": subquestion})
                # assistant_response = QA(subquestion)
                text, image_paths, answer_type = selected_question["response"][ind2]
                response = {"text": text, "image": image_paths}
                self.messages.append({"role": "assistant", "content": response, "answer_type": answer_type})

    # Button 클릭 시 작동
    def display_question_buttons(self):
        st.write("Please select a question:")
        for index, question in enumerate(self.sample_questions):
            ind = question["index"]

            if st.button(question["question"], key=f"question_{ind}", type="primary"):
                if "selected_question" not in st.session_state:
                    st.session_state.selected_question = None
                st.session_state.selected_question = question
                self.depth = 1
                self.display_subquestion_buttons()
                

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
                    if len(image_paths) != 0:
                        with st.expander("Click to view images"):
                            cols = st.columns(len(image_paths))
                            for i, image_path in enumerate(image_paths):
                                print("#1 Image Path")
                                print(image_path)
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
        st.title("My Small Javis")
        if len(self.messages) == 0 and self.depth==0:
            self.display_question_buttons()
            answer_type = "image"
        elif len(self.messages)==0 and self.depth==1:
            self.display_subquestion_buttons()
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