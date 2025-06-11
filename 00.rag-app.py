import os
from dotenv import load_dotenv ## 환경변수(.env) 정보 가져옴
from openai import AzureOpenAI


def main():
    os.system('cls' if os.name == 'nt' else 'clear')  ##윈도우면 cls, 다른거면 clear
    load_dotenv() ## 환경변수 읽어옴

    openai_endpoint = os.getenv("OPENAI_ENDPOINT")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    chat_model= os.getenv("CHAT_MODEL")
    embedding_model= os.getenv("EMBEDDING_MODEL")
    search_endpoint= os.getenv("SEARCH_ENDPOINT")
    search_api_key = os.getenv("SEARCH_API_KEY")
    index_name = os.getenv("INDEX_NAME")

    ## Initialize Azure OpenAI Client
    chat_client = AzureOpenAI(
        api_version = "2024-12-01-preview",
        azure_endpoint=openai_endpoint,
        api_key=openai_api_key
    )

    # 시스템 프롬프트 작성
    prompt = [
        {
            "role" : "system",
            "content" : "Your are a travel assistant that provides information on travel service availavle from Margie's Travel."
        },
    ]

    while True : 
        input_text = input("Enter your question (or type 'exit' to quit): ")
        if input_text.lower() == "exit" : 
            print("Exiting the application...")
            break
        elif input_text.strip() == "": ##strip() 공백제거
            print("Please enter a valid question...")
            continue

        ## user 입력데이터를 prompt에 추가
        prompt.append({"role":"user", "content": input_text})
        print(prompt)

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


        # # Additional parameters to apply RAG pattern using the AI Search index
        # rag_params = {
        #     "data_sources": [
        #         {
        #             # he following params are used to search the index
        #             "type": "azure_search",
        #             "parameters": {
        #                 "endpoint": search_endpoint,
        #                 "index_name": index_name,
        #                 "authentication": {
        #                     "type": "api_key",
        #                     "key": search_api_key,
        #                 },
        #                 # The following params are used to vectorize the query
        #                 "query_type": "vector",
        #                 "embedding_dependency": {
        #                     "type": "deployment_name",
        #                     "deployment_name": embedding_model,
        #                 },
        #             }
        #         }
        #     ],
        # }

        ## submit the chat request with RAG parameters
        response = chat_client.chat.completions.create(
            model= chat_model,
            messages=prompt,
            extra_body = rag_params  ##RAG 파라미터
        )

        completion = response.choices[0].message.content
        print(completion)

        ## Add the response to the chat history
        prompt.append({"role": "assistant", "content": completion})




if __name__ == "__main__" :   ## 메인실행
    main()