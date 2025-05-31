from pymongo import MongoClient
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document

import os
from dotenv import load_dotenv

class VectorSearch:
    def __init__(self):

        # Initialize embedding model
        self.embeddings = AzureOpenAIEmbeddings(
            model=os.getenv("EMBEDDING_MODEL"),
            api_key=os.getenv("EMBEDDING_API_KEY"),
            azure_endpoint=os.getenv("EMBEDDING_ENDPOINT"),
            chunk_size=2048
        )

        # Initialize MongoDB client
        self.client = MongoClient(os.getenv("MONGO_URI"))
        self.collection = self.client[os.getenv("DB_NAME")][os.getenv("COLLECTION_NAME")] #Database and collection name
        
        print("Connected to MongoDB:", self.collection)

        # Initialize vector store
        self.vectorStore = MongoDBAtlasVectorSearch(self.collection, self.embeddings)

        # Initialize text splitter
        self.text_splitter = CharacterTextSplitter(chunk_size=2048, chunk_overlap=50)

    def search(self, query, threshold=0.6):
        results = self.vectorStore.similarity_search_with_score(query, k=5) 
        filtered_results = [
            (doc, score) for doc, score in results if score >= threshold
        ]
        ragcontent = ""
        for doc, score in filtered_results:
            ragcontent += f"{doc.page_content}\n"
            ragcontent += f"Source: {doc.metadata.get('source', 'Unknown')}, page: {doc.metadata.get('page', 'Unknown')}\n"
            ragcontent += f"Score: {score:.2f}\n\n"
        if not ragcontent:
            ragcontent = None
        return ragcontent




    def store(self, file_path):
        loader = PyPDFLoader(file_path)
        pages = []
        
        for page in loader.lazy_load():
            # Modify the source metadata to include only the file name
            if "source" in page.metadata:
                page.metadata["source"] = os.path.basename(page.metadata["source"])  # Extract file name
            # Split at newline
            chunks = self.text_splitter.split_text(page.page_content)
            for chunk in chunks:
                # Create Document instances instead of dictionaries
                pages.append(Document(page_content=chunk, metadata=page.metadata))
        
        self.vectorStore.add_documents(pages)
        return "Documents added to the vector store."


    def store_folder(self, folder_path):
        # Iterate through all files in the folder
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            
            # Process only PDF files
            if os.path.isfile(file_path) and file_name.lower().endswith('.pdf'):
                # Call the existing `store` method on each file
                self.store(file_path)
        
        return "All files in the folder have been processed and added to the vector store."



