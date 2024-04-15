import os
from openai import OpenAI
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Milvus
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA

from langchain.prompts import PromptTemplate
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    MessagesPlaceholder
)

def QA(query):
    client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
    embedding_model = OpenAIEmbeddings(model="text-embedding-3-large",
                                      openai_api_key=os.environ['OPENAI_API_KEY']) 
    
    nprobe = 81
    topK = 5
    db = Milvus(
        connection_args={'host':os.environ['MILVUS_HOST'], 'port':os.environ['MILVUS_PORT']},
        collection_name="ioniq5_2024_manual",  # 검색할 Milvus 컬렉션 이름
        embedding_function=embedding_model,  # 임베딩 모델
        collection_properties={
            "index_type": "IVF_FLAT", 
            "metric_type": "COSINE", 
            "params": {"nprobe": nprobe}
        },
        consistency_level= "Session",
        primary_field= 'index',
        text_field= 'contents',
        vector_field= 'vector'
    )
    retriever = db.as_retriever(search_kwargs={"k": topK})
    
    SEARCH_PARAM = {
        "index_type": "IVF_FLAT", "metric_type": "COSINE", "params": {"nprobe": nprobe}
    }
    
    
    template = """
    너는 자동차 전문가야.
    내가 {context}를 주면 해당 문맥을 고려해서 대답해줘.
    문맥의 구조는 다음과 같아.
    - 설명서 대제목
    - 설명서 중제목
    - 설명서 소제목
    - 내용
    여기서 설명서의 제목들은 너가 주제를 잘 인식하기위해 작성한 메타데이터이므로 설명서 제목에 의하면과 같은 말은 피해줘.
    그리고 내용에 표가 있을 수도 있어.
    표가 있다면 표 형식은 다음과 같아. 표가 없다면 무시해도 돼.
    표를 구분하는 구분자가 있고
    표이름으로 표간 구분할 수 있어.
    그리고 표내용은 표를 나타내는 markdown형식으로 되어있어.
    아래는 표 형식이야.
    ####### 표 ####### 
    표이름:
    표내용
    
    표이름:
    표내용
    
    ####### 표 종료 ####### 
    
    만약에 표가 있다면 표를 참고해서 대답해줘
    
    """
    
    # Create the first prompt template
    sys_prompt: PromptTemplate = PromptTemplate(
        input_variables=["context"],
        template=template
    )
    
    system_message_prompt = SystemMessagePromptTemplate(prompt=sys_prompt)
    
    user_prompt: PromptTemplate = PromptTemplate(
        input_variables=["question"],
        template="Question: {question}"
    )
    user_message_prompt = HumanMessagePromptTemplate(prompt=user_prompt)
    
    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, user_message_prompt])
    
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)  # Modify model_name if you have access to GPT-4
    
    from langchain.chains import RetrievalQA
    qa_chain = RetrievalQA.from_chain_type(llm,
                                           retriever=retriever, 
                                           chain_type_kwargs={"prompt": chat_prompt},
                                           return_source_documents=True)
    result = qa_chain({"query": query})
    return {"text":result['result'],
            "image":None,
            'table':None}