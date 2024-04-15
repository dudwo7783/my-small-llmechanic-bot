import random
import time
import streamlit as st

class ChatBot:
    def __init__(self):
        self.messages = []
        self.sample_questions = [
    {
        "question": "What are some popular tourist destinations?", 
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
            [
                "https://postfiles.pstatic.net/20151119_284/superbin0713_1447908339382uF9ur_JPEG/Meerkat_%28Suricata_suricatta%29_Tswalu.jpg?type=w2", 
                "https://i.namu.wiki/i/bNuxf5wk6fxRGLkeC5BBEYvN1BQy4voyLmm_1DyPOZ5V5eNDwOe3zMGuBFr57vN6EZU8legoVfYh-HF_7dxL7tj-uyYBcY1PIG0_aSMRiYNF9WGyqp34yRZISFNUaGqKLO46V27_WvSfEVm8JAWXGg.webp", 
            ], "image"
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

    def response_generator(self, text, image_paths):
        response = f"{text}|{','.join(image_paths)}"
        for word in response.split():
            yield word + " "
            time.sleep(0.05)

    def display_question_buttons(self):
        st.write("Please select a question:")
        for index, question in enumerate(self.sample_questions):
            if st.button(question["question"], key=f"question_{index}"):
                self.messages.append({"role": "user", "content": question["question"]})
                text, image_paths, answer_type = question["response"]
                response = "".join(list(self.response_generator(text, image_paths)))
                content = response.split("|")
                self.messages.append({"role": "assistant", "content": response, "answer_type": answer_type})
                break

    def display_chat_history(self):
        for message in self.messages:
            with st.chat_message(message["role"]):
                content = message["content"].split("|")
                st.markdown(content[0])
                if len(content) > 1 and message["answer_type"] == "image":
                    image_paths = content[1].split(",")
                    with st.expander("Click to view images"):
                        cols = st.columns(len(image_paths))
                        for i, image_path in enumerate(image_paths):
                            with cols[i]:
                                st.image(image_path)

    def handle_user_input(self, answer_type):
        user_input = st.text_input("Your message:", key="user_input")
        if user_input:
            st.chat_message("user").write(user_input)
            self.messages.append({"role": "user", "content": user_input})
            assistant_response = "This is a sample response from the assistant."
            self.messages.append({"role": "assistant", "content": assistant_response, "answer_type": answer_type})
            st.chat_message("assistant").write(assistant_response)

    def run(self):
        st.title("Echo Bot")
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

# # Create an instance of the ChatBot class
# chat_bot = ChatBot()

# # Run the chat bot
# chat_bot.run() 
if "chat_bot" not in st.session_state:
    st.session_state.chat_bot = ChatBot()

st.session_state.chat_bot.run()