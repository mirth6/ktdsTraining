## streamlit 에서 실행 가능한 코드로 변환
## streamlit run .

import os
from dotenv import load_dotenv ## 환경변수(.env) 정보 가져옴
from openai import AzureOpenAI
import streamlit as st



load_dotenv() ## 환경변수 읽어옴

openai_endpoint = os.getenv("OPENAI_ENDPOINT")
openai_api_key = os.getenv("OPENAI_API_KEY")
chat_model= os.getenv("CHAT_MODEL")
embedding_model= os.getenv("EMBEDDING_MODEL")
search_endpoint= os.getenv("SEARCH_ENDPOINT")
search_api_key = os.getenv("SEARCH_API_KEY")
index_name = os.getenv("INDEX_NAME")

#Initialize Azure OpenAI Client
chat_client = AzureOpenAI(
    api_version = "2024-12-01-preview",
    azure_endpoint=openai_endpoint,
    api_key=openai_api_key
)

st.title("Margie's Travel Assistant")
st.write("Ask your travel-related questions below: ")

## 상태를 유지하기 위해 st.session_state에 저장
if "messages" not in st.session_state:
    st.session_state.messages = [
        # 시스템 프롬프트
        {
            "role" : "system",
            "content" : "Your are a travel assistant that provides information on travel service availavle from Margie's Travel."
        },
    ]

## Display chat history
for message in st.session_state.messages : 
    st.chat_message(message["role"]).write(message["content"])




## openai 호출 함수
def get_openai_response(messages):
    ## Additional parameters to apply RAG pattern using the AI Search index
    ## 아래 형태가 거의 표준
    rag_params = {
        "data_sources" : [
            {
                "type":"azure_search",
                "parameters" : {
                    "endpoint" : search_endpoint,
                    "index_name" : index_name,
                    "authentication" : {  ## 인증방법 apikey
                        "type" : "api_key",
                        "key" : search_api_key
                    },
                    "query_type" : "vector", ## text / vector / hybrid
                    "embedding_dependency" : { ##질문할때도 db와 동일한 모델로 임베딩되도록
                        "type" : "deployment_name",
                        "deployment_name" : embedding_model
                    }
                },
            }
        ]
    }
   
    ## submit the chat request with RAG parameters
    response = chat_client.chat.completions.create(
        model= chat_model,
        messages=messages,
        extra_body = rag_params  ##RAG 파라미터
    )

    print ("respnse messages....\n",response.choices[0].message)
    completion = response.choices[0].message.content
    return completion




## user input
if user_input := st.chat_input("Enter your question: "):   ## :=(월러스 연산자) user_input에 값을 할당과 동시에 값 반환
    st.session_state.messages.append({"role":"user", "content": user_input})
    st.chat_message("user").write(user_input)

    with st.spinner("응답을 기다리는 중..."):
         response = get_openai_response(st.session_state.messages)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)

    



