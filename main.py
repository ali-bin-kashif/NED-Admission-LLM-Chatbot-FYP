from langchain.prompts import PromptTemplate
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores.faiss import FAISS
from langchain_community.llms.ctransformers import CTransformers
from langchain.chains import RetrievalQA
from fastapi import FastAPI
from pydantic import BaseModel
# import chainlit as cl

DB_FAISS_PATH = 'vectorstore/db_faiss'

custom_prompt_template = """Use the following pieces of information to answer the user's question.
If you don't know the answer, just say this text
"Sorry I can't help you on this query, Please see the guidelines and FAQs on the following link: https://www.neduet.edu.pk/admission, or if you have some special query you can contact the administrator".

Context: {context}
Question: {question}

Only return the helpful answer below and nothing else.
Helpful answer:
"""

def set_custom_prompt():
    """
    Prompt template for QA retrieval for each vectorstore
    """
    prompt = PromptTemplate(template=custom_prompt_template,
                            input_variables=['context', 'question'])
    return prompt

#Retrieval QA Chain
def retrieval_qa_chain(llm, prompt, db):
    qa_chain = RetrievalQA.from_chain_type(llm=llm,
                                       chain_type='stuff',
                                       retriever=db.as_retriever(search_kwargs={'k': 2}),
                                       return_source_documents=True,
                                       chain_type_kwargs={'prompt': prompt}
                                       )
    return qa_chain

#Loading the model
def load_llm():
    # Load the locally downloaded model here
    llm = CTransformers(
        model = "./llama-2-7b-chat.ggmlv3.q8_0.bin",
        model_type="llama",
        max_new_tokens = 512,
        temperature = 0.5
    )
    return llm

#QA Model Function
def qa_bot():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2",
                                       model_kwargs={'device': 'cpu'})
    db = FAISS.load_local(DB_FAISS_PATH, embeddings)
    llm = load_llm()
    qa_prompt = set_custom_prompt()
    qa = retrieval_qa_chain(llm, qa_prompt, db)

    return qa

#Pydantic object
class validation(BaseModel):
    prompt: str
#Fast API
app = FastAPI()

@app.get("/llm_on_cpu/{query}")
#output function
async def final_result(query):
        qa_result = qa_bot()
        response = qa_result({'query': query})
        return response
 

# print(final_result('Background history of NED?'))
#chainlit code
# @cl.on_chat_start
# async def start():
#     chain = qa_bot()
#     msg = cl.Message(content="Starting the bot...")
#     await msg.send()
#     msg.content = "Hi, Welcome to Medical Bot. What is your query?"
#     await msg.update()

#     cl.user_session.set("chain", chain)

# @cl.on_message
# async def main(message: cl.Message):
#     chain = cl.user_session.get("chain") 
#     cb = cl.AsyncLangchainCallbackHandler(
#         stream_final_answer=True, answer_prefix_tokens=["FINAL", "ANSWER"]
#     )
#     cb.answer_reached = True
#     res = await chain.acall(message.content, callbacks=[cb])
#     answer = res["result"]
#     await cl.Message(content=answer).send()

