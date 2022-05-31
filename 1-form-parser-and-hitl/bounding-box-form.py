from google.cloud import documentai_v1beta3 as documentai
from PIL import Image, ImageDraw

import pandas as pd

PROJECT_ID = "windy-site-254307"
LOCATION = "eu"  # Format is 'us' or 'eu'
PROCESSOR_ID = "bad52526b46aa2b6"  
PDF_PATH = "./public-form.pdf" # Update to path of target document

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
    document = {"content": image_content, "mime_type": "application/pdf"} ## image/tiff

    # Configure the process request
    request = {"name": name, "document": document}

    # Recognizes text entities in the PDF document
    result = client.process_document(request=request)
    document = result.document
    print("Document processing complete.\n\n")

    # For a full list of Document object attributes, please reference this page: https://googleapis.dev/python/documentai/latest/_modules/google/cloud/documentai_v1beta3/types/document.html#Document    
    document_pages = document.pages
    keys = []
    keysConf = []
    values = []
    valuesConf = []
    
    # Grab each key/value pair and their corresponding confidence scores.
    for page in document_pages:
        for form_field in page.form_fields:
            fieldName=get_text(form_field.field_name,document)
            keys.append(fieldName.replace(':', ''))
            nameConfidence = round(form_field.field_name.confidence,4)
            keysConf.append(nameConfidence)
            fieldValue = get_text(form_field.field_value,document)
            values.append(fieldValue.replace(':', ''))
            valueConfidence = round(form_field.field_value.confidence,4)
            valuesConf.append(valueConfidence)
    
    # Create a Pandas Dataframe to print the values in tabular format. 
    df = pd.DataFrame({'Key': keys, 'Key Conf': keysConf, 'Value': values, 'Value Conf': valuesConf})
    print(df)

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
PNG_PATH = "./public-form.png" 

document_image = Image.open(PNG_PATH)
draw = ImageDraw.Draw(document_image)
for form_field in doc.pages[0].form_fields:
    # Draw the bounding box around the form_fields
    # First get the co-ords of the field name
    vertices = []
    for vertex in form_field.field_name.bounding_poly.normalized_vertices:
      vertices.append({'x': vertex.x * document_image.size[0], 'y': vertex.y * document_image.size[1]})
    draw.polygon([
        vertices[0]['x'], vertices[0]['y'],
        vertices[1]['x'], vertices[1]['y'],
        vertices[2]['x'], vertices[2]['y'],
        vertices[3]['x'], vertices[3]['y']], outline='red')
    
    vertices = []
    for vertex in form_field.field_value.bounding_poly.normalized_vertices:
        vertices.append({'x': vertex.x * document_image.size[0], 'y': vertex.y * document_image.size[1]})
    draw.polygon([
        vertices[0]['x'], vertices[0]['y'],
        vertices[1]['x'], vertices[1]['y'],
        vertices[2]['x'], vertices[2]['y'],
        vertices[3]['x'], vertices[3]['y']], outline='blue')
document_image.show()