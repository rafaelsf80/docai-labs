# type: ignore[1]
# pylint: skip-file
"""
Makes a Online Processing Request to Document AI
"""
from typing import List, Sequence
import pandas as pd

from google.api_core.client_options import ClientOptions
from google.cloud import documentai_v1 as documentai


def online_process(
    project_id: str,
    location: str,
    processor_id: str,
    file_path: str,
    mime_type: str,
) -> documentai.Document:
    """
    Processes a document using the Document AI Online Processing API.
    """

    # Instantiates a client
    docai_client = documentai.DocumentProcessorServiceClient(
        client_options=ClientOptions(
            api_endpoint=f"{location}-documentai.googleapis.com"
        )
    )

    # The full resource name of the processor, e.g.:
    # projects/project-id/locations/location/processor/processor-id
    # You must create new processors in the Cloud Console first
    resource_name = docai_client.processor_path(project_id, location, processor_id)

    # Read the file into memory
    with open(file_path, "rb") as file:
        file_content = file.read()

    # Load Binary Data into Document AI RawDocument Object
    raw_document = documentai.RawDocument(content=file_content, mime_type=mime_type)

    # Configure the process request
    request = documentai.ProcessRequest(name=resource_name, raw_document=raw_document)

    # Use the Document AI client to process the sample form
    result = docai_client.process_document(request=request)

    return result.document


def get_table_data(
    rows: Sequence[documentai.Document.Page.Table.TableRow], text: str
) -> List[List[str]]:
    """
    Get Text data from table rows
    """
    all_values: List[List[str]] = []
    for row in rows:
        current_row_values: List[str] = []
        for cell in row.cells:
            current_row_values.append(
                text_anchor_to_text(cell.layout.text_anchor, text)
            )
        all_values.append(current_row_values)
    return all_values


def text_anchor_to_text(text_anchor: documentai.Document.TextAnchor, text: str) -> str:
    """
    Document AI identifies table data by their offsets in the entirity of the
    document's text. This function converts offsets to a string.
    """
    response = ""
    # If a text segment spans several lines, it will
    # be stored in different text segments.
    for segment in text_anchor.text_segments:
        start_index = int(segment.start_index)
        end_index = int(segment.end_index)
        response += text[start_index:end_index]
    return response.strip().replace("\n", " ")


PROJECT_ID = 'argolis-rafaelsanchez-ml-dev'
LOCATION = 'eu' # Format is 'us' or 'eu'
PROCESSOR_ID = '8f20926906a787ec' # Create processor in Cloud Console
FILE_PATH = './868.pdf'
MIME_TYPE = 'application/pdf'

document = online_process(
    project_id=PROJECT_ID,
    location=LOCATION,
    processor_id=PROCESSOR_ID,
    file_path=FILE_PATH,
    mime_type=MIME_TYPE,
)

header_row_values: List[List[str]] = []
body_row_values: List[List[str]] = []

i=0
for page in document.pages:
    for table in page.tables:
        header_row_values = get_table_data(table.header_rows, document.text)
        body_row_values = get_table_data(table.body_rows, document.text)
        # Create a Pandas Dataframe to print the values in tabular format.
        df = pd.DataFrame(
            data=body_row_values,
            columns=pd.MultiIndex.from_arrays(header_row_values),
        )

        print(df)

        df.to_csv(f"table_data_{i}.csv", index=False)
        i=i+1
        
    

# Create a Pandas Dataframe to print the values in tabular format.
df = pd.DataFrame(
    data=body_row_values,
    columns=pd.MultiIndex.from_arrays(header_row_values),
)

print(df)

df.to_csv("table_data.csv", index=False)