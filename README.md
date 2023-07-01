# event-manager

This is an event app repository that allows users to create, manage, and search events. Motivation behind this project was to learn about data modelling in dynamodb. 

## Features:

### User Registration and Authentication:
- Users can sign up, sign in, and manage their accounts using the Cognito service. (WIP)
- User information includes email. This is unique.

### Event Management:
- Users can create events with a title, description, date, and location.
- CRUD actions are available for managing events (create, read, update, delete).
- Event details include the title, description, location, date, creator.
- Other users can search for events based on location (city, zip code).
- Users can choose to attend events by registering for events. A user should be able to see all the registrations they have done.
- Event also maintains a list of all the people that have been registered.
  
### Email Notifications (WIP):
- Users will receive email reminders 24 hours and 2 hours before the event.
- If an event is deleted, all scheduled email notifications for that event will be canceled.


## Technologies Used:
Python based serverless backend that employs AWS Lambda. Chalice is used for write the backend in python that communicates with AWS Lambda.
Database: DynamoDB. All the functionality is modelled in a single table. PynamoDB package is used as a wrapper.
User Authentication: AWS Cognito


## Resources used:
- DynamoDB Book [https://www.dynamodbbook.com/]
- PynamoDB [https://pynamodb.readthedocs.io/]
- AWS DynamoDB [https://docs.aws.amazon.com/dynamodb/index.html]
- Boto3 DynamoDB [https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb.html]
- AWS Chalice [https://aws.github.io/chalice/]
- AWS Lambda [https://docs.aws.amazon.com/lambda/index.html]
