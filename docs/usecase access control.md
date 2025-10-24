
# See Also
- [application.md](application.md): End-to-end workflow, agent responsibilities, status codes, CSV schemas, audit/logging, deployment & testing guidance
- [architecture.md](architecture.md): System architecture, Agent2Agent protocol, MCP server, sequence diagrams, toolcall mappings, module responsibilities
- [flow.md](flow.md): Canonical workflow diagram
- [toolcalls.md](toolcalls.md): MCP tool call protocol and agent tool call details
- [csv_schemas.md](csv_schemas.md): Canonical CSV schemas and data model
- [README.md](README.md): Documentation index and onboarding

> **Note:** This document provides a business view and high-level explanation of the access control use case. For the most current and detailed implementation/design, refer to `application.md` and `architecture.md` in this directory. This file is not the authoritative source of truth.

It's going to be a generative AI agentic system for access control. 
This system looks at a list of changes made by users in applications and per change investigates whether the user that made that change had the rights to do so. If the user had the right to make the change the change investigation agent will set the value of the change_investigation column to 'Approved' on the hr_mutations.csv data set for that change. If there are no rights found for that user for that application the Agent will draft an email to the user that made the change asking for clarification.
When a user repond to the email for clarification the agent wil check if that reason is valid or not. The agent uses this input (lack of approval) to create an email to send to the changer in the system to request why this change was made and to receive context on the change. Then, after the agent receives a response, it checks this response based on HR systems like sick leave data, and other sources/documentation necessary to validate if this step is correct.
Then, based on these insights, the agent creates a new email, sending it to the manager of the maker of the change to ask this person if this change was authorized or not, and if they agree that this change should be accepted or not. Then, if the agent receives a response back from that manager, it validates using all the information of previous steps to generate an advisory report to the change controller stating if it was a correct change or not, advising what to do with it, which is three different options: either accept that this change should have been authorized, or this change shouldn't have been authorized and a follow up investigation needs to be started, or the change was correct, but a mistake was made, therefore a human needs to change something in a system.


This requires us to have data/csv files. We generated the files to gather the insights, read them to know what is what. Add or change if needed, tell me if you do. Create a nice abstraction function/layer/api setup for calling the data files.
Data files:
/data/authorisations.csv
/data/hr_mutations.csv
/data/role_authorisations.csv
/data/roles.csv
/data/users.csv
/data/sickLeave.csv
/data/vacation.csv
Check if we can answer the question with the data?

I want the website to have two areas/pages, one for triggering the system and chatting with it and one for the insights in the status of the change investigations. We need to mock al system interaction because we dont have email and integrations for this application. Then we want an agent to handle the repetative task of checking the changes. 

System features:
- Data .csv files

- Enter a hr_matation (full page with dropdowns from the users and applications)
- Agent gets triggered on a hr_mutation addition
- Agent checks change for existing autorization of user (tool call -> check tabels if rights are given )
- Agent approves change on valid authorixation (tool call)
- Agent sends email to the user who made the change for clarification (tool call) reply could be "my collegue X was sick so I did it"
- Agent waits for and processes email response of User and checks for validity of claim, for example by checking sick leave data (tool calls)
- Agent sends email to manager of user to verify claim of user
- Agent waits for and processes email response of Manager and gathers all information from previous steps
- Agent sends an advisory report to the Controller


________________________________________
PRODUCT OVERVIEW
Purpose: Automate the detection, investigation, and advisory process for changes through a multi-agent AI system.
Core Value: Reduce manual effort in change governance, accelerate resolution cycles, ensure compliance, and provide auditable decision trails.
Key Behavior: Investigation Agent is triggered by new change entry → Rights Check Agent checks for rights → If not approved the Request for Information Agent contact the changer for clarification and validate response → Then the Request for Information Agent contacts the manager to ask for validity of claim changer → Finally the Advisory Agent generates advisory report with recommendation to controller.
________________________________________
2. USER STORIES (implementation targets)
As a System,
I want to be triggered by a new change, so I can start the Investigation Agent

As an Investigation Agent,
I am orchestrating the investigation by updating the status in the Audit Colum based on the results I get back from other Agents I called, communication must be done with Agent2Agent Protocol,
So I can orchestrate the flow and keep track of the context and insights of the Investigation.

As a Rights Check Agent,
I want to check the user rights for a particular application using an MCP tool call,
So I can check if a change was done by a user who had the right to do so. I give my findings back to the Investigation Agent.

As an Investigation Agent,
I get back response via Agent2Agent from the Rights Check Agent and adjust status for next step,
So I can ask the Request for Information Agent to email the user for clarification.

As a Request for Information Agent.
I want to email the user asking for clarification and check with tool calls if that is correct or not,
So I can report back to the Investigation Agent what the user’s reason was and whether that is validated or not.

As an Investigation Agent,
I get back response via Agent2Agent from the Request for Information Agent for user flow and adjust status for next step,
So I can ask the Request for Information Agent to email the manager for correctness of claim user.

As a Request for Information Agent.
I want to email the manager asking for validation of user claims,
So I can report back to the Investigation Agent what the managers opinion is.

As an Investigation Agent,
I get back response via Agent2Agent from the Request for Information Agent for manager flow and adjust status for next step,
So I can ask the Advisory Agent to write a detailed report about the case by giving it a complete overview of the findings in previous steps.

As an Advisory Agent,
I want to email the Change Controller with a detailed report about the case and findings,
So the Change Controller can make a well informed decision. I report back to the Investigation Agent that the repost is send.

As an Investigation Agent,
I get back response via Agent2Agent from the Advisory Agent and adjust status to the final status,
So this concludes the flow and the agent can stop.

As a Changer,
I want a clear email asking why I made a change,
So I can respond with context efficiently.

As a Manager,
I want a simple yes/no authorization or validation question,
So I can confirm or deny without delay.

As a Change Controller,
I want an AI-generated advisory with evidence and a clear recommendation,
So I can quickly decide to accept, investigate, or correct the change.

As a Compliance Officer,
I want full audit trails and explainability in the form of a logfile what the Agents do and the statuses that change,
So I can verify the system operates ethically and within policy.
