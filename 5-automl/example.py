# Sources: https://cloud.google.com/document-ai/docs/automl-model
# Source: https://cloud.google.com/document-ai/docs/invoice-parser

# THIS CODE DOES NOT WORK: NEED SOME FIXING
from google.cloud import documentai_v1beta2 as documentai


client = documentai.DocumentUnderstandingServiceClient()

gcs_source = documentai.types.GcsSource(uri=input_uri)

# mime_type can be application/pdf, image/tiff,
# and image/gif, or application/json
input_config = documentai.types.InputConfig(
    gcs_source=gcs_source, mime_type='application/pdf')

automl_params = documentai.types.AutoMlParams(model=automl_model_name)

# Location can be 'us' or 'eu'
parent = 'projects/{}/locations/us'.format(project_id)
request = documentai.types.ProcessDocumentRequest(
    parent=parent,
    input_config=input_config,
    automl_params=automl_params
    )


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
        start_index = segment.start_index
        end_index = segment.end_index
        response += document.text[start_index:end_index]
    return response
    for entity in document.entities:
        print('entity type: {}'.format(entity.type_))
        print('Text;  {}'.format(_get_text(entity)))