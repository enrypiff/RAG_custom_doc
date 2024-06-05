import tkinter as tk
import argparse
from dataclasses import dataclass
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.load import dumps, loads
from operator import itemgetter
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain import hub

CHROMA_PATH = "src/chroma"

embedding_function = OpenAIEmbeddings()
db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
retriever = db.as_retriever(search_kwargs={"k": 3})

def get_unique_union(documents: 'list[list]'):
    """ Unique union of retrieved docs """
    # Flatten list of lists, and convert each Document to string
    flattened_docs = [dumps(doc) for sublist in documents for doc in sublist]
    # Get unique documents
    unique_docs = list(set(flattened_docs))
    # Return
    return [loads(doc) for doc in unique_docs]



def create_multiple_query(query_text):
    # Multi Query: Different Perspectives
    template = """You are an AI language model assistant. Your task is to generate five 
    different versions of the given user question to retrieve relevant documents from a vector 
    database. By generating multiple perspectives on the user question, your goal is to help
    the user overcome some of the limitations of the distance-based similarity search. 
    Provide these alternative questions separated by newlines. Original question: {question}"""
    prompt_perspectives = ChatPromptTemplate.from_template(template)

    generate_queries = (
        prompt_perspectives 
        | ChatOpenAI(temperature=0) 
        | StrOutputParser() 
        | (lambda x: x.split("\n"))
    )

    # Retrieve
    retrieval_chain = generate_queries | retriever.map() | get_unique_union
    docs = retrieval_chain.invoke({"question":query_text})
    print(len(docs))
    print(docs)
    return retrieval_chain

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

def get_response(text):
    """
    Retrieves a response based on the given text.

    Args:
        text (str): The input text to generate a response for.

    Returns:
        tuple: A tuple containing the generated answer, sources, and pages.

    Raises:
        None

    Example:
        >>> get_response("What is the capital of France?")
        ("Paris is the capital of France.", ["Wikipedia"], [1])
    """
        
    # RAG
    template = """Answer the following question based on this context:

    {context}

    Question: {question}
    """

    prompt = ChatPromptTemplate.from_template(template)
    # print(prompt)

    # LLM
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    
    # prompt_hub_rag = hub.pull("rlm/rag-prompt")
    # prompt_hub_rag

    rag_chain_from_docs = (
        RunnablePassthrough.assign(context=(lambda x: format_docs(x["context"])))
        | prompt
        | llm
        | StrOutputParser()
    )

    rag_chain_with_source = RunnableParallel(
        {"context": retriever, "question": RunnablePassthrough()}
    ).assign(answer=rag_chain_from_docs)

    answer = rag_chain_with_source.invoke(text)
    answer_cleaned = answer['answer']
    sources = []
    pages = []

    for doc in answer['context']:
        sources.append(doc.metadata['source'])
        pages.append(doc.metadata['page'])

    return answer_cleaned, sources, pages


def send_message():
    query = entry.get("1.0", tk.END).strip()  # Specify the index range for getting the text and remove leading/trailing whitespace
    response, sources, pages = get_response(query)
    chatbox.insert(tk.END, f"You: {query}\n", "user")  # Set the tag "user" for the text
    chatbox.insert(tk.END, f"Bot: {response}\n", "bot")  # Set the tag "bot" for the text
    for source, page in zip(sources, pages):
        chatbox.insert(tk.END, f"Source: {source}, Page: {page + 1}\n", "source") # Set the tag "source" for the text
    chatbox.insert(tk.END, f"\n")
    entry.delete("1.0", tk.END)  # Specify the index range for deleting the text

# Create the main window
window = tk.Tk()
window.title("Chatbot UI")

# Create a text widget to display the chat history
chatbox = tk.Text(window, height=20, width=100, wrap=tk.WORD)  # Adjust the height and width as desired, set wrap option to WORD
# Configure the text widget tags for color and style
chatbox.tag_configure("user", foreground="black", font=("Arial", 12, "bold"))
chatbox.tag_configure("bot", foreground="black", font=("Arial", 12, "italic"))
chatbox.tag_configure("source", foreground="black", font=("Arial", 9, "italic"))
chatbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)  # Automatically resize with the window and add margin

# Create a text widget for user input
entry = tk.Text(window, height=5, width=100)  # Adjust the height and width as desired
entry.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)  # Automatically resize with the window and add margin

# Create a button to send the message
send_button = tk.Button(window, height=2, width=30, text="Send", command=send_message)
send_button.pack(pady=10)

# Configure the window to be resizable
window.resizable(True, True)

# Start the main event loop
window.mainloop()