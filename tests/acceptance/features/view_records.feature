Feature: View extracted-text records
  As a user
  I want to GET /api/records
  So that I can see previously completed OCR jobs

  Scenario: GET /api/records returns a JSON list
    Given the API is deployed
    When I GET "/api/records"
    Then the response status should be 200
    And the response body should be a JSON array

  Scenario: DELETE a record removes it from the list
    Given the API is deployed
    And a completed job record exists in DynamoDB
    When I DELETE the record via "/api/records/{jobId}"
    Then the response status should be 204
    And the record is no longer returned by GET /api/records
