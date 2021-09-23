# Make sure the processor is available

echo 'Calling Document AI to trigger HITL'
# This triggers the human review
curl -X POST \
    -H "Authorization: Bearer "$(gcloud auth application-default print-access-token) \
    -H "Content-Type: application/json; charset=utf-8" \
    -d @request.json \
    https://eu-documentai.googleapis.com/v1/projects/655797269815/locations/us/processors/bad52526b46aa2b6:process

# This does NOT trigger the human review
#curl -X POST \
#    -H "Authorization: Bearer "$(gcloud auth application-default print-access-token) \
#    -H "Content-Type: application/json; charset=utf-8" \
#    -d @request.json \
#    https://documentai.googleapis.com/v1beta3/projects/655797269815/locations/us/processors/a924a188a8e8d71e/humanReviewConfig:reviewDocument

# This gets state of the operation
#curl -X GET \
#    -H "Authorization: Bearer "$(gcloud auth application-default print-access-token) \
#    https://documentai.googleapis.com/v1beta3/projects/655797269815/locations/us/operations/6169536329637141264



