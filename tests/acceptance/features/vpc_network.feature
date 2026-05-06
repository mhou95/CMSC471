Feature: VPC Network Foundation
  As a platform engineer
  I want a properly configured VPC with public and private subnets
  So that all workloads run in isolated, routable network boundaries

  Scenario: Verify VPC CIDR block (S1)
    Given the SAM template is initialized
    Then the AWS::EC2::VPC resource must have CidrBlock "10.0.0.0/16"

  Scenario: Verify two public and two private subnets across two AZs (S2)
    Given the SAM template is initialized
    Then the template must define 2 public subnets
    And the template must define 2 private subnets

  Scenario: Verify NAT Gateway exists for private subnet internet access (S3)
    Given the SAM template is initialized
    Then the template must define an AWS::EC2::NatGateway resource
    And the NAT Gateway must be in a public subnet
