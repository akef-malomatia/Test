from AzureBlobUploader import AzureBlobUploader
from AzureDataSource import AzureDataSource
from AzureSearchIndex import AzureSearchIndex
from AzureSearchIndexer import AzureSearchIndexer
from AzureSkillset import AzureOpenAISkillset

from azure.core.credentials import AzureKeyCredential

import os
from dotenv import load_dotenv
import logging

if __name__ == "__main__":
    load_dotenv()
    search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    openaiEndpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
    search_api_key = os.getenv("AZURE_SEARCH_API_KEY")

    sas_url = os.getenv("STORAGE_ACCOUNT_testazurestorage_write_SAS_URL")
    credential = AzureKeyCredential(search_api_key)
    index_name = "law2006"
    azure_ada_openai_config = {
        "endpoint": openaiEndpoint,
        "deployment_id": "text-embedding-ada-002",
        "model_name": "text-embedding-ada-002",
        "api_key": openai_api_key,
        "dimensions": 1536,
    }

    file_name = "LAW NO. 22 of 2006 PROMULGATING 'THE FAMILY LAW'.doc"
    file_path = os.path.join("..", "..", "..", "..", "Data Source", file_name)
    index_name="law2006"
    data_source_name = f"{index_name}-blob"
    skillset_name = f"{index_name}-skillset"
    indexer_name = f"{index_name}-indexer"

    # Step 0: upload the data
    uploader = AzureBlobUploader(sas_url)
    uploader.upload_file(file_path, file_name)

    # Step 1: Create data source
    azureSearch = AzureDataSource(search_endpoint, AzureKeyCredential(search_api_key))
    azureSearch.create_data_source(data_source_name)

    # Step 2: Create the index
    law_index = AzureSearchIndex(search_endpoint, credential, index_name, azure_ada_openai_config)
    law_index.create_index()

    # Step 3: Create the skillset
    skillset = AzureOpenAISkillset(
        search_endpoint,
        AzureKeyCredential(search_api_key),
        azure_ada_openai_config,
        index_name,
        skillset_name
    )
    skillset.create_skillset()

    # Step 4: Create the indexer
    manager = AzureSearchIndexer(
        search_endpoint,
        AzureKeyCredential(search_api_key),
        index_name,
        skillset_name,
        data_source_name,
        indexer_name
    )

    try:
        manager.create_indexer()
    except Exception as e:
        print(f"An error occurred: {e}")

    # Step 5: Run the indexer
    try:
        manager.run_indexer()
    except Exception as e:
        print(f"An error occurred: {e}")
    
    