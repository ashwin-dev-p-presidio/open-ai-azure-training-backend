from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
#from azure.search.documents.models import IndexDocumentsBatch, IndexAction, IndexActionType
import os
from dotenv import load_dotenv

# Load environment variables from .env.local file
load_dotenv(dotenv_path='.env.local')

search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
search_key = os.getenv("AZURE_SEARCH_KEY")
index_name = os.getenv("AZURE_SEARCH_INDEX")

if not all([search_endpoint, search_key, index_name]):
    raise ValueError("Please set the AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_KEY, and AZURE_SEARCH_INDEX environment variables.")

def index_pdf_content(doc_id, content):
    client = SearchClient(endpoint=search_endpoint,
                          index_name=index_name,
                          credential=AzureKeyCredential(search_key))

    # batch = IndexDocumentsBatch(actions=[
    #     IndexAction(
    #         action_type=IndexActionType.UPLOAD,
    #         document={"id": doc_id, "content": content}
    #     )
    # ])
    
    # result = client.index_documents(batch)
    # return result
    document = {
        "id": doc_id,  # Unique ID
        "content": content  # Storing full extracted text
    }
    
    # Upload to Azure Search
    result = client.upload_documents(documents=[document])
    
    print(f"Indexing Result: {result}")

def search_azure(question,doc_id):
    client = SearchClient(endpoint=search_endpoint,
                          index_name=index_name,
                          credential=AzureKeyCredential(search_key))

    
    filter_query = f"id eq '{doc_id}'"
    results = client.search(search_text=question, filter=filter_query,query_type="full", highlight_fields="content")
    
    relevant_content = []
    for result in results:
        if "content" in result:
            relevant_content.append(result["content"])
    return relevant_content
