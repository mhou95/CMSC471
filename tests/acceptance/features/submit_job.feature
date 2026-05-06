Feature: Submit OCR job
  As a user
  I want to POST an imageKey to /api/jobs
  So that a Step Functions execution is started and I receive a jobId

  Scenario: POST a valid imageKey starts an execution
    Given the API is deployed
    And an image exists in the inbox bucket
    When I POST the imageKey to "/api/jobs"
    Then the response status should be 200
    And the response body should contain a "jobId"
    And the response body should contain an "executionArn"

  Scenario: POST without imageKey returns 400
    Given the API is deployed
    When I POST an empty body to "/api/jobs"
    Then the response status should be 400

  Scenario: Poll job status returns a valid status
    Given the API is deployed
    And a job has been submitted
    When I GET "/api/jobs/{jobId}"
    Then the response status should be 200
    And the response body should contain a "status" field
