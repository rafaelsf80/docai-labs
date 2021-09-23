from google.cloud import documentai_v1beta3 as documentai
from PIL import Image, ImageDraw

import os
import pandas as pd

PROJECT_ID = "windy-site-254307"
LOCATION = "eu"  # Format is 'us' or 'eu'
PROCESSOR_ID = "bad52526b46aa2b6"  
PDF_PATH = "./invoice.pdf" # Update to path of target document

def process_document_sample():
    # Instantiates a client
    client_options = {"api_endpoint": "{}-documentai.googleapis.com".format(LOCATION)}
    client = documentai.DocumentProcessorServiceClient(client_options=client_options)

    # The full resource name of the processor, e.g.:
    # projects/project-id/locations/location/processor/processor-id
    # You must create new processors in the Cloud Console first
    name = f"projects/{PROJECT_ID}/locations/{LOCATION}/processors/{PROCESSOR_ID}"

    with open(PDF_PATH, "rb") as image:
        image_content = image.read()

    # Read the file into memory
    document = {"content": image_content, "mime_type": "application/pdf"}

    # Configure the process request
    request = {"name": name, "document": document}

    # Recognizes text entities in the PDF document
    result = client.process_document(request=request)
    print(result)
    document = result.document
    entities = document.entities
    print("Document processing complete.\n\n")

    # For a full list of Document object attributes, please reference this page: https://googleapis.dev/python/documentai/latest/_modules/google/cloud/documentai_v1beta3/types/document.html#Document  
    types = []
    values = []
    confidence = []
    
    # Grab each key/value pair and their corresponding confidence scores.
    for entity in entities:
        types.append(entity.type_)
        values.append(entity.mention_text)
        confidence.append(round(entity.confidence,4))
        
    # Create a Pandas Dataframe to print the values in tabular format. 
    df = pd.DataFrame({'Type': types, 'Value': values, 'Confidence': confidence})
    print(df)
    
    if result.human_review_operation:
        print ("Triggered HITL long running operation: {}".format(result.human_review_operation))

    return document


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

doc = process_document_sample()

####################
##### Draw bounding boxes, after converting the pdf to an image
####################
JPG_PATH = "./invoice.jpeg" 

document_image = Image.open(JPG_PATH)
draw = ImageDraw.Draw(document_image)
for entity in doc.entities:
    # Draw the bounding box around the entities
    vertices = []
    for vertex in entity.page_anchor.page_refs[0].bounding_poly.normalized_vertices:
        vertices.append({'x': vertex.x * document_image.size[0], 'y': vertex.y * document_image.size[1]})
    draw.polygon([
        vertices[0]['x'], vertices[0]['y'],
        vertices[1]['x'], vertices[1]['y'],
        vertices[2]['x'], vertices[2]['y'],
        vertices[3]['x'], vertices[3]['y']], outline='blue')
document_image.show()


# def parse_form(project_id=PROJECT_ID,
#                input_uri=PDF_URI):
#     """Parse a form using the Document AI API"""

#     # Create a new Document AI client
#     client = documentai.DocumentUnderstandingServiceClient()

#     # Specify which cloud in GCS you'd like to analyze
#     gcs_source = documentai.types.GcsSource(uri=input_uri)

#     # mime_type can be application/pdf, image/tiff,
#     # and image/gif, or application/json
#     input_config = documentai.types.InputConfig(
#         gcs_source=gcs_source, mime_type='application/pdf')

#     # Optional: Improve form parsing results by providing 
#     # key-value pair hints.
#     # For each key hint, key is text that is likely to appear in the
#     # document as a form field name (i.e. "DOB").
#     # Value types are optional, but can be one or more of:
#     # ADDRESS, LOCATION, ORGANIZATION, PERSON, PHONE_NUMBER, ID,
#     # NUMBER, EMAIL, PRICE, TERMS, DATE, NAME
#     key_value_pair_hints = [
#         documentai.types.KeyValuePairHint(key='Emergency Contact',
#                                           value_types=['NAME']),
#         documentai.types.KeyValuePairHint(
#             key='Referred By')
#     ]

#     # Setting enabled=True enables form extraction
#     form_extraction_params = documentai.types.FormExtractionParams(
#         enabled=True, key_value_pair_hints=key_value_pair_hints)

#     # Location can be 'us' or 'eu'
#     parent = 'projects/{}/locations/us'.format(project_id)
#     request = documentai.types.ProcessDocumentRequest(
#         parent=parent,
#         input_config=input_config,
#         form_extraction_params=form_extraction_params)

#     document = client.process_document(request=request)
    
#     return document

# doc = parse_form(PROJECT_ID)