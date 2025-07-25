'''
This code contains helper functions for the 07. RAG_SDK.ipynb notebook.
'''
from vector_pdf6 import create_vector_db_from_pdf
from openai import AzureOpenAI

def get_information(questions,
                    question_formats,
                    openai_endpoint,
                    openai_key,
                    document_fpath = "./Data/testContract1.pdf",
                    collection_name = "pdf_vectors",
                    system_message = '''
                    You are an assistant that tries to get information out of text chunks.
                    Answer the query using only the sources provided below.
                    Answer ONLY with the facts listed in the list of sources below.
                    Do not repeat the question to me, just provide the answer in a concise way.
                    If there isn't enough information provided, respond with NULL.
                    Do not generate answers that don't use the provided text.
                    '''):
    '''
    Inputs: 
        - questions (list)
        collection (chroma collection name. Have a default -- or create new collection name based on doc name),
        Document_fpath
    Goal: take in a list of text questions and document to retrieve a set of answers
    '''

    #get vector db & cooresponding retreiver created
    retriever = create_vector_db_from_pdf(
    pdf_path = document_fpath,
    collection_name = collection_name,
    embedding_model_name = "mxbai-embed-large",
    knn = 7
    )

    #establish an openAI client
    client = AzureOpenAI(
        api_key=openai_key,  
        api_version="2023-05-15",
        azure_endpoint=openai_endpoint
    )

    

    #create an empty list to hold our question/answer pairs
    results = []
    for i in range(len(questions)):
        #get relevant info from our document
        documents = retriever.invoke(questions[i]) #pass query to our vector db to get closest "k" vectors of info
        top_chunks = "\n\n".join([x.page_content for x in documents])

        #get a response from openAI
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"""Using the following document excerpts, answer this question: 
                {questions[i]}
                {question_formats[i]}

                DOCUMENT:
                {top_chunks}
                """}
            ],
            temperature=0
            )
        
        #save that question/response pair to a list
        results.append([questions[i], response.choices[0].message.content])
        

    return results
