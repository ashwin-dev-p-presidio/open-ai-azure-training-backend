from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex, SimpleField, SearchFieldDataType
from azure.core.credentials import AzureKeyCredential
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv(dotenv_path='.env.local')

search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
search_key = os.getenv("AZURE_SEARCH_KEY")
index_name = os.getenv("AZURE_SEARCH_INDEX")

if not all([search_endpoint, search_key]):
    raise ValueError("Please set the AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY environment variables.")

# Create a SearchIndexClient
client = SearchIndexClient(endpoint=search_endpoint, credential=AzureKeyCredential(search_key))

# Define the index schema
fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
    #SimpleField(name="content", type=SearchFieldDataType.String, searchable="true") #searchable true not working
]

# Create the index
index = SearchIndex(name=index_name, fields=fields)
client.create_index(index)

print(f"Index '{index_name}' created successfully.")