from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader, DirectoryLoader, JSONLoader, Docx2txtLoader, CSVLoader, TextLoader
import os
import cohere
from langchain.text_splitter import RecursiveCharacterTextSplitter
import base64
from mistralai import Mistral


#Function to split text into chunks
from langchain.text_splitter import RecursiveCharacterTextSplitter

def split_text(text, chunk_size=80000, chunk_overlap=100):
    """
    Splits a large text into smaller chunks.
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    )
    return text_splitter.split_text(text)


#function to load the documents
def load_document(path):
    """
    Loads documents from a directory or a single file.
    """
    documents = []

    # Check if the path is a file or directory
    if os.path.isfile(path):  # If a single file is given
        files = [path]
    elif os.path.isdir(path):  # If a directory is given
        files = [os.path.join(path, file) for file in os.listdir(path)]
    else:
        raise ValueError(f"Invalid file or directory path: {path}")

    # Load each file
    for file_path in files:
        if not os.path.isfile(file_path):
            print(f"Skipping {file_path} - Not a valid file.")
            continue

        try:
            if file_path.endswith(".doc") or file_path.endswith(".docx"):
                loader = Docx2txtLoader(file_path)
            elif file_path.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
            elif file_path.endswith(".csv"):
                loader = CSVLoader(file_path)
            elif file_path.endswith(".txt") or file_path.endswith(".md"):
                loader = TextLoader(file_path,encoding="utf-8")
            #write code in the else such that it calls the ocr function and the output of the ocr file needs to be sent to the summerizer
            else:
                result=perform_ocr(path)
                return co.summarize(text=str(result),length="short").summary

            documents.extend(loader.load())  # Extract and store content

        except Exception as e:
            print(f"Error loading {file_path}: {str(e)}")  # Catch errors

    if not documents:
        raise ValueError("No valid documents found!")

    return documents

co = cohere.Client("bR4AmUeEpAkHtzxpx3nou6a2k2w3a40tAPQBWMZu")


#function to summarize the doument
def summarize_document(docs):
    """
    Summarizes the extracted document text using Cohere.
    """
    text = " ".join([doc.page_content for doc in docs])  # Extract text from loaded documents
    chunks = split_text(text)
    
    summaries=[]
    for chunk in chunks:
    # Call Cohere Summarization API
        response = co.summarize(
            text=chunk,
            length="short",  # Options: "short", "medium", "long"
            format="paragraph",  # Options: "bullets", "paragraph"
            model="command", # Use Cohere’s Command model
            )
        summaries.append(response.summary)
    
    return " ".join(summaries)

#function for Translation
def translate_text(text, source_lang, target_lang):
    """
    Translates text using Cohere's 'command' model.
    """
    prompt = f"Translate the following text from {source_lang} to {target_lang}: \n\n{text}\n\nProvide only the translation without explanations."
    
    response = co.generate(
        model="c4ai-aya-expanse-32b", 
        prompt=prompt,
        max_tokens=500,  
        temperature=0.3,  
        stop_sequences=["\n"]
    )

    return response.generations[0].text.strip()


client = Mistral(api_key="JeGQPmkVkRdzDCvN4NbKxFGp77OrqKJg")

def encode_image(image_path):
    """Encode the image to base64."""
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except FileNotFoundError:
        print("Error: File not found.")
        return None
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None


def perform_ocr(image_path):
    """Process OCR using Mistral API."""
    if not image_path or not os.path.exists(image_path):
        print("Error: Invalid or missing image path.")
        return None

    base64_image = encode_image(image_path)
    if not base64_image:
        print("Error: Failed to encode image.")
        return None

    try:
        ocr_response = client.ocr.process(
            model="mistral-ocr-latest",
            document={
                "type": "image_url",
                "image_url": f"data:image/jpeg;base64,{base64_image}"
            }
        )
        print("OCR processed successfully!")
        return ocr_response
    except Exception as e:
        print(f"Error: OCR processing failed: {e}")
        return None
    