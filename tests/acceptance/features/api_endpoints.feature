Feature: API Endpoints - Compute Tier
  As a frontend developer
  I want to verify that all API endpoints are correctly configured
  So that the SPA can communicate with the backend

  Scenario: Verify API Gateway exists
    Given the SAM template is initialized
    When the stack is deployed
    Then the API Gateway must exist
    And the API Gateway must have an endpoint URL

  Scenario: Verify GET / endpoint returns index page
    Given the API is deployed
    When I make a GET request to "/"
    Then the response status should be 200
    And the response should contain HTML

  Scenario: Verify POST /api/jobs endpoint exists
    Given the API is deployed
    When the template defines a POST /api/jobs route
    Then the route must be mapped to submit_handler Lambda

  Scenario: Verify GET /api/jobs/{id} endpoint exists
    Given the API is deployed
    When the template defines a GET /api/jobs/{id} route
    Then the route must be mapped to poll_handler Lambda

  Scenario: Verify GET /api/records endpoint exists
    Given the API is deployed
    When the template defines a GET /api/records route
    Then the route must be mapped to records_handler Lambda
