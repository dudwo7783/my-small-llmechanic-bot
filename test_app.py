import streamlit as st
import requests

def send_request_to_llm(text):
    url = "http://llm_model_container:8889/test"
    payload = {"text": text}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        return response.json()["test_text"]
    else:
        return None

def main():
    st.title("Streamlit-LLM 통신 테스트")
    
    input_text = st.text_input("입력 텍스트를 입력하세요:")
    
    if st.button("테스트"):
        if input_text.strip():
            test_text = send_request_to_llm(input_text)
            if test_text:
                st.success(f"테스트 결과: {test_text}")
            else:
                st.error("테스트 요청 실패")
        else:
            st.warning("입력 텍스트를 입력해주세요.")

if __name__ == "__main__":
    main()