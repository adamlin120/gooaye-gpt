import os
import re
import time
import json

import pinecone
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate,
)
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Pinecone, Chroma
from langchain.document_loaders.csv_loader import CSVLoader

loader = CSVLoader(file_path="./transcript_clean.csv", source_column="id")

documents = loader.load()

with open("episode_to_youtube_id.json", "r") as f:
    episode_to_youtube_id = json.load(f)

# strip "id", "transcirpt" in page_content
for doc in documents:
    doc.page_content = doc.page_content.split("transcript: ", 1)[-1].strip()
    episode, start_in_sec = doc.metadata['source'].split("_", 1)

    episode = re.findall(r"\d+", episode)[0]

    episode_youtube_id = episode_to_youtube_id[episode]

    doc.metadata = {
        "episode": episode,
        "start_in_sec": start_in_sec,
        "title": f"第 {episode} 集",
        "link": f"https://www.youtube.com/watch?v={episode_youtube_id}&t={start_in_sec}s",
    }

text_splitter = CharacterTextSplitter(chunk_size=200, chunk_overlap=0)
texts = text_splitter.split_documents(documents)

# print how many documents we have
print(f"Number of documents: {len(texts)}")

use_openai_embeddings = True
if use_openai_embeddings:
    embeddings = embeddings = OpenAIEmbeddings()
else:
    embeddings = HuggingFaceEmbeddings(model_name="distiluse-base-multilingual-cased-v1")

use_pincone = True
if use_pincone:
    # initialize pinecone
    pinecone.init(
        api_key=os.environ["PINECONE_API_KEY_CSIE"],
        environment="eu-west1-gcp",  # next to api key in console
    )

    index_name = "gooaye-gpt"

    index = pinecone.Index(index_name)


    create_new = True
    # Delete vectors if it already exists
    if create_new:
        try:
            print("Deleting index")
            pinecone.delete_index(index_name)
            print("Deleted index")
        except pinecone.exceptions.PineconeException as e:
            print("Index does not exist")
            print(e)
            pass

        print("Creating index")
        docsearch = Pinecone.from_documents(texts, embeddings, index_name=index_name)
        print("Created index")
    else:
        docsearch = Pinecone(index, embeddings.embed_query, "text")
else:
    docsearch = Chroma.from_documents(texts, embeddings)

query = "大盤ETF？"
# time the query
start = time.time()
docs = docsearch.similarity_search(query)
end = time.time()
print(f"Query time: {end - start}")

# print(docs)

system_template = """使用以下 podcast 片段來回答用戶的問題。如果您不知道答案，只需說不知道即可，不要試圖編造答案。將您的答案保持在五句以下。答案要是繁體中文、要準確、有幫助、簡明明確。使用以下段落來回答查詢
----------------
{context}"""
messages = [
    SystemMessagePromptTemplate.from_template(system_template),
    HumanMessagePromptTemplate.from_template("{question}"),
]
prompt = ChatPromptTemplate.from_messages(messages)

chain_type_kwargs = {"prompt": prompt}
qa = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(),
    chain_type="stuff",
    retriever=docsearch.as_retriever(),
    chain_type_kwargs=chain_type_kwargs,
)

print("-" * 80)
print(f"Query: {query}")
# time the query
start = time.time()
print(qa.run(query))
end = time.time()
print(f"Query time: {end - start}")
