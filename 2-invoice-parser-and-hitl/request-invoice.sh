#!/bin/bash
echo 'Processing request ...'
echo 'Note request.json contains a base64 encoded doc'
curl -X POST \
 -H "Authorization: Bearer "$(gcloud auth application-default print-access-token) \
 -H "Content-Type: application/json; charset=utf-8" \
 -d @request.json \
 -H "X-Goog-User-Project: windy-site-254307" \
https://eu-documentai.googleapis.com/v1/projects/windy-site-254307/locations/eu/processors/bad52526b46aa2b6:process


