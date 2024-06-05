__import__('pysqlite3')
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

from flask import Flask, request, jsonify
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain.load import dumps, loads
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableParallel

app = Flask(__name__)
app.config["DEBUG"] = True

CHROMA_PATH = "chroma"

embedding_function = OpenAIEmbeddings()
db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
retriever = db.as_retriever(search_kwargs={"k": 3})

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
    # Rest of the code...
def get_response(text):

    # RAG
    template = """Answer the following question based on this context:

    {context}

    Question: {question}
    """

    prompt = ChatPromptTemplate.from_template(template)

    # LLM
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)

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


@app.route('/', methods=['GET'])
def home():
    return '''<h1>Test</h1>
                <p>A flask api implementation   </p>'''


@app.route('/chatbot', methods=['POST'])
def chatbot_api():
    app.logger.info('Received request to /chatbot')
    data = request.get_json()
    message = data['message']

    response, sources, pages = get_response(message)

    app.logger.info('Successfully processed request to /chatbot')

    return jsonify({'response': response, 'sources': sources, 'pages': pages})
    


if __name__ == "__main__":
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=5000)
