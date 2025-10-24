# Documentation Consolidation Roadmap

This document lists the key consolidation points for merging `architecture.md` and `application.md` into a single, canonical source. Each section includes detailed action items to guide the process.

---

## 1. Agent Implementation Pattern, Responsibilities, and Workflow
[x] Review both files for agent class definitions, responsibilities, and workflow steps
[x] Create a single section describing agent roles and responsibilities
[x] Document canonical workflow steps (trigger, rights check, clarification, advisory, finalization)
[x] Describe agent interaction and context passing
[x] Remove duplicate/conflicting descriptions
[x] Ensure all agent types are covered

## 2. Diagrams & Mappings
 [x] Extract all Mermaid diagrams and mapping tables from architecture.md
 [x] Place diagrams in a dedicated section
 [x] Reference diagrams in relevant workflow/protocol sections
 [x] Ensure diagrams are up to date

 [x] Consolidate onboarding steps, environment variable setup, and contributor policies
 [x] Include quickstart steps, environment requirements, troubleshooting tips, and best practices
 [x] Remove redundant onboarding info from other sections

## 4. Agent2Agent Protocol & Audit Logging
 [x] Merge protocol definitions, message schema tables, and audit logging requirements
 [x] Ensure all required fields, message formats, and logging policies are included
 [x] Reference protocol usage in workflow and error handling
## 5. MCP Server & Tool Calls
- [ ] Combine MCP server endpoint tables, tool call definitions, and example requests/responses
- [ ] Ensure all endpoints, arguments, results, and error handling are documented
- [ ] Reference tool calls in workflow and protocol sections

## 6. Workflow Example & User Stories
- [ ] Extract step-by-step workflow example and user stories
- [ ] Place in a dedicated section
- [ ] Ensure example matches canonical workflow and status codes

## 7. Technology, Deployment & Testing
- [ ] Consolidate technology stack, deployment instructions, and testing strategy
- [ ] Include programming language, libraries, UI framework, deployment steps, and testing strategy
- [ ] Remove duplicate info from other sections

## 8. Security, Compliance & Module Mapping
- [ ] Merge security, compliance, and module responsibility tables
- [ ] Ensure all compliance requirements, audit log protection, and module responsibilities are covered

## 9. Data Model & CSV Schemas
- [ ] Create a section referencing csv_schemas.md for canonical schemas
- [ ] Avoid repeating full schema tables; link to the source file

## 10. UI Wireframes & Workflow Mapping
- [ ] Create a section referencing wireframe.md for canonical UI layouts and response flows
- [ ] Avoid duplicating wireframe content; link to the source file

---

## Next Steps
- Use this roadmap to guide the consolidation of documentation.
- As you merge content, check off each action item and ensure all unique information is preserved.
- The final consolidated document should be clear, non-redundant, and easy to maintain.