import os
from langchain.document_loaders import UnstructuredFileLoader
from langchain.embeddings.huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders.csv_loader import CSVLoader
from configs.config import *
import sentence_transformers
from typing import List
import datetime

"""
  知识库向量化服务
"""
class SourceService:
    def __init__(self,
                 embedding_model: str = EMBEDDING_MODEL,
                 embedding_device=LOCAL_EMBEDDING_DEVICE):
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model_dict[embedding_model], )
        self.embeddings.client = sentence_transformers.SentenceTransformer(self.embeddings.model_name,
                                                                           device=embedding_device)
        self.vector_store = None
        self.vector_store_path = VECTOR_STORE_PATH

    def init_source_vector(self, docs_path):
        """
        初始化本地知识库向量
        :return:
        """
        docs = []
        for doc in os.listdir(docs_path):
            if doc.endswith('.txt'):
                print(doc)
                loader = UnstructuredFileLoader(f'{docs_path}/{doc}', mode="elements")
                doc = loader.load()
                docs.extend(doc)
        self.vector_store = FAISS.from_documents(docs, self.embeddings)
        self.vector_store.save_local(self.vector_store_path)

    def init_knowledge_vector_store(self,
                                    filepath: str or List[str]):
        if isinstance(filepath, str):
            if not os.path.exists(filepath):
                print("路径不存在")
                return None
            elif os.path.isfile(filepath):
                file = os.path.split(filepath)[-1]
                try:
                    loader = UnstructuredFileLoader(filepath, mode="elements")
                    docs = loader.load()
                    print(f"{file} 已成功加载")
                except Exception as e:
                    print(f"{file} 未能成功加载", e)
                    return None
            elif os.path.isdir(filepath):
                docs = []
                for file in os.listdir(filepath):
                    fullfilepath = os.path.join(filepath, file)
                    try:
                        loader = UnstructuredFileLoader(fullfilepath, mode="elements")
                        docs += loader.load()
                        print(f"{file} 已成功加载")
                    except Exception as e:
                        print(f"{file} 未能成功加载", e)
        else:
            docs = []
            for file in filepath:
                try:
                    loader = UnstructuredFileLoader(file, mode="elements")
                    docs += loader.load()
                    print(f"{file} 已成功加载")
                except Exception as e:
                    print(f"{file} 未能成功加载", e)

        vector_store = FAISS.from_documents(docs, self.embeddings)
        vs_path = f"""{VECTOR_STORE_PATH}/{os.path.splitext(file)[0]}_FAISS_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}"""
        vector_store.save_local(vs_path)
        return vs_path if len(docs) > 0 else None

    def add_document(self, document_path):
        loader = UnstructuredFileLoader(document_path, mode="elements")
        doc = loader.load()
        self.vector_store.add_documents(doc)
        self.vector_store.save_local(self.vector_store_path)

    def load_vector_store(self, path):
        if path is None:
            self.vector_store = FAISS.load_local(self.vector_store_path, self.embeddings)
        else:
            self.vector_store = FAISS.load_local(path, self.embeddings)
        return self.vector_store

    def add_csv(self, document_path):
        loader = CSVLoader(file_path=document_path)
        doc = loader.load()
        print("doc:", doc)

