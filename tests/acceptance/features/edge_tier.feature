Feature: Edge and Presentation Tier
  As an end user
  I want a static site served through API Gateway backed by S3
  So that I can access the application from a browser without configuring CloudFront

  Scenario: Verify S3 static site bucket exists (S4)
    Given the SAM template is initialized
    Then the S3 bucket "StaticSiteBucket" must exist
    And the bucket must be encrypted with AES256
    And the bucket must have public access blocked

  Scenario: Verify GET / route is mapped to index handler (S5)
    Given the SAM template is initialized
    Then the template must define an IndexHandler Lambda
    And the IndexHandler must handle GET / events
    And the IndexHandler must read from the StaticSiteBucket

  Scenario: Verify API Gateway is the public entry point (S5)
    Given the SAM template is initialized
    Then the API Gateway must exist
    And the API Gateway must have an endpoint URL
