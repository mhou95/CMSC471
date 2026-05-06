Feature: Orchestration Tier - Step Functions Workflow
  As a data engineer
  I want to verify that the Step Functions state machine is correctly configured
  So that image transcription jobs execute reliably

  Scenario: Verify Step Functions state machine exists
    Given the SAM template is initialized
    When the stack is deployed
    Then the Step Functions state machine "TextractWorkflowStateMachine" must exist
    And the state machine must have three states: FetchImage, CallTextract, SaveResults

  Scenario: Verify state machine has retry policy
    Given the state machine is deployed
    Then each state must have a retry policy
    And max attempts should be 3
    And backoff rate should be 2.0

  Scenario: Verify state machine has error handling
    Given the state machine is deployed
    Then each state must have a Catch block for error handling
    And errors must route to HandleError state
    And HandleError must update DynamoDB with FAILED status

  Scenario: Verify Textract Lambda function exists
    Given the SAM template is initialized
    When the stack is deployed
    Then the Lambda function "CallTextractFunction" must exist
    And the function must have textract:DetectDocumentText permission
