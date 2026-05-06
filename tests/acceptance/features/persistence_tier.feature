Feature: Persistence Tier - Data Storage
  As a platform engineer
  I want to verify that all data storage components are properly configured
  So that job state, extracted text, and raw images are persisted reliably

  Scenario: Verify DynamoDB Job State table exists
    Given the SAM template is initialized
    When the stack is deployed
    Then the DynamoDB table "cmsc471-job-state" must exist
    And the table must have partition key "jobId" of type String
    And the table must have billing mode "PAY_PER_REQUEST"

  Scenario: Verify S3 Inbox bucket exists with lifecycle rule
    Given the SAM template is initialized
    When the stack is deployed
    Then the S3 bucket "InboxBucket" must exist
    And the bucket must have a lifecycle rule transitioning to Glacier after 30 days
    And the bucket must have public access blocked

  Scenario: Verify S3 Static Site bucket exists
    Given the SAM template is initialized
    When the stack is deployed
    Then the S3 bucket "StaticSiteBucket" must exist
    And the bucket must be encrypted with AES256
    And the bucket must have public access blocked

  Scenario: Verify RDS MySQL results database exists (S10)
    Given the SAM template is initialized
    Then the RDS instance "ResultsDatabase" must exist in the template
    And the database must be named "cmsc471results"
    And the database engine must be "mysql"
    And the database must reside in private subnets
