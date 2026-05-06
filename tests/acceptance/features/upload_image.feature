Feature: Upload image to inbox
  As a user
  I want to POST an image to /api/inbox
  So that it is stored in the S3 inbox bucket and ready for OCR processing

  Scenario: POST a JPEG to the inbox
    Given the API is deployed
    When I POST a small test image to "/api/inbox"
    Then the response status should be 200
    And the response body should contain an "objectKey"

  Scenario: GET the inbox file list
    Given the API is deployed
    When I GET "/api/inbox"
    Then the response status should be 200
    And the response body should contain a "files" list

  Scenario: DELETE a previously uploaded file
    Given the API is deployed
    And a file has been uploaded to the inbox
    When I DELETE the uploaded file from "/api/inbox/{key}"
    Then the response status should be 204
