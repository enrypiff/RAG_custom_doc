from langchain_community.document_loaders import DirectoryLoader, PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter
from langchain.schema import Document
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
import os
import shutil

# Define the path for Chroma and data
CHROMA_PATH = "src/chroma/"
DATA_PATH = "books/"

# Get the OpenAI API key from environment variables
api_key = os.environ.get('OPENAI_API_KEY')
# If the API key is not set, raise an error
if api_key is None:
    raise ValueError("OPENAI_API_KEY environment variable not set")

def main():
    generate_data_store()

# Define the function to generate the data store
def generate_data_store():
    # Load the documents
    documents = load_documents()
    
    chunks = split_text(documents)
    save_to_chroma(chunks)


def load_documents():
    # Get a list of all PDF files in the specified directory
    pdf_files = [file for file in os.listdir(DATA_PATH) if file.endswith(".pdf")]

    # Create an empty list to store the loaded documents
    documents = []

    # Load each PDF file and append the document to the list
    for pdf_file in pdf_files:
        # Join the directory and filename to create the full path
        pdf_path = os.path.join(DATA_PATH, pdf_file)

        # Create an instance of PyMuPDFLoader with the full path
        loader = PyMuPDFLoader(pdf_path)
        loaded_documents = loader.load()
        print(loaded_documents[0])
        print(loaded_documents[1])
        documents.extend(loaded_documents)

    return documents

# 
def split_text(data):
    # Create a RecursiveCharacterTextSplitter object with specified parameters
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    
    # Create an empty list to store the chunks
    chunks = []
    document_chunks = text_splitter.split_documents(data)
    chunks.extend(document_chunks)
    # Split each document into chunks using the text splitter
    # for page in data:
    #     if page.page_content is not None:   
    #         print(page)
    #         document_chunks = text_splitter.split_documents(page)
    #         chunks.extend(document_chunks)
    #     # Print the number of documents and chunks
    #     print(f"Split {len(document)} documents into {len(chunks)} chunks.")
    
    # Print the content and metadata of a specific chunk (in this case, the 10th chunk)
    document = chunks[0]
    print(document.page_content)
    print(document.metadata)
    
    # Return the list of chunks
    return chunks

# Define a function to save chunks to Chroma
def save_to_chroma(chunks: 'list[Document]'):
    # If the Chroma path exists, clear out the database first.
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)

    # Create a new Chroma database from the documents.
    # OpenAIEmbeddings() is used for embedding the documents.
    # The database is persisted in the directory specified by CHROMA_PATH.
    db = Chroma.from_documents(
        chunks, OpenAIEmbeddings(), persist_directory=CHROMA_PATH
    )
    # Persist the database
    db.persist()
    # Print the number of chunks saved and the path where they are saved
    print(f"Saved {len(chunks)} chunks to {CHROMA_PATH}.")


if __name__ == "__main__":
    main()