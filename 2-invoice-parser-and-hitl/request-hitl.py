# POST https://documentai.googleapis.com/v1beta3/{humanReviewConfig=projects/*/locations/*/processors/*/humanReviewConfig}:reviewDocument

from google.cloud import documentai_v1beta3 as documentai
import base64

# It's always better if you use a bad quality example in order to trigger HITL
LOCAL_FILE = '/Users/rafaelsanchez/git/docai-labs-EXTERNAL/2-invoice-parser-and-hitl/invoice.pdf'
PROJECT_ID = '655797269815' # windy-site-254307
LOCATION = 'eu'
PROCESSOR_ID = 'bad52526b46aa2b6'

def process_document_sample(
    project_id: str, location: str, processor_id: str, file_path: str
):
    # Instantiates a client
    client_options = {"api_endpoint": "eu-documentai.googleapis.com"}
    client = documentai.DocumentProcessorServiceClient(client_options=client_options)
    
    # operation = client._transport.operations_client.get_operation(lro)
    # if operation.done:
    #     print("HITL location: {} ".format(str(operation.response.value)[5:-1]))
    # else:
    #     print('Waiting on human review.')

    # The full resource name of the processor, e.g.:
    # projects/project-id/locations/location/processor/processor-id
    # You must create new processors in the Cloud Console first
    name = f"projects/{project_id}/locations/{location}/processors/{processor_id}"

    with open(file_path, "rb") as image:
        image_content = image.read()

    #with open("./FACTA_BASE64.txt", "w") as new_file:
    #    new_file.write(str(base64.b64encode(image_content)))

    # Read the file into memory
    #document = {"content": base64.b64encode(image_content), "mime_type": "application/pdf"}
    document = {"content": image_content, "mime_type": "application/pdf"}

    # Configure the process request
    request = {"name": name, "document": document}
    print(request['name'])

    # Recognizes text entities in the PDF document
    result = client.process_document(request=request)

    document = result.document

    print(result.human_review_status)

    print("Document processing complete.")

    # For a full list of Document object attributes, please reference this page: https://googleapis.dev/python/documentai/latest/_modules/google/cloud/documentai_v1beta3/types/document.html#Document

    document_pages = document.pages

    # Read the text recognition output from the processor
    print("The document contains the following paragraphs:")
    for page in document_pages:
        paragraphs = page.paragraphs
        for paragraph in paragraphs:
            paragraph_text = get_text(paragraph.layout, document)
            #print(f"Paragraph text: {paragraph_text}")


# Extract shards from the text field
def get_text(doc_element: dict, document: dict):
    """
    Document AI identifies form fields by their offsets
    in document text. This function converts offsets
    to text snippets.
    """
    response = ""
    # If a text segment spans several lines, it will
    # be stored in different text segments.
    for segment in doc_element.text_anchor.text_segments:
        start_index = (
            int(segment.start_index)
            if segment in doc_element.text_anchor.text_segments
            else 0
        )
        end_index = int(segment.end_index)
        response += document.text[start_index:end_index]
    return response

process_document_sample(PROJECT_ID, LOCATION, PROCESSOR_ID, LOCAL_FILE)
