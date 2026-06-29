# Expense Approval Workflow API - Implementation Plan

## Problem Statement

Organizations need an efficient way to manage employee expense claims through an approval workflow. Currently, there's no structured system to handle submission, approval, and processing of expenses across different roles (employees, managers, finance). This leads to:
- Manual tracking and communication overhead
- Lack of visibility into approval status
- Inconsistent approval processes
- No audit trail for compliance

## Solution

Build a FastAPI-based Expense Approval Workflow API that automates the entire expense claim lifecycle:
- Employees submit expense claims with supporting documentation
- Managers approve/reject claims from their team members
- Finance processes approved claims
- Real-time visibility into claim status for all stakeholders
- Complete audit logging and analytics for administration

## User Stories

1. As an employee, I want to submit an expense claim, so that I can be reimbursed for business expenses
2. As an employee, I want to save my expense claim as a draft, so that I can complete it later
3. As an employee, I want to submit my draft expense claim, so that it goes to my manager for review
4. As an employee, I want to view the status of my submitted claims, so that I know where they are in the approval process
5. As an employee, I want to view the rejection reason for my rejected claim, so that I can correct it and resubmit
6. As an employee, I want to cancel my draft or submitted claim, so that I can remove unwanted expense submissions
7. As an employee, I want to edit my draft claim before submitting, so that I can correct mistakes
8. As an employee, I want to receive confirmation of my claim submission, so that I know it was successfully submitted
9. As a manager, I want to see all pending claims from my team members, so that I can review and approve/reject them
10. As a manager, I want to approve an expense claim, so that it moves to finance for payment processing
11. As a manager, I want to reject an expense claim with a reason, so that the employee knows why it was rejected
12. As a manager, I want to view the approval history of claims, so that I can track what has been approved
13. As a manager, I want to be notified of new pending claims from my team, so that I can process them promptly
14. As a finance person, I want to see all approved claims, so that I can process payments
15. As a finance person, I want to mark claims as processed, so that employees know they have been paid
16. As a finance person, I want to view the complete audit trail of each claim, so that I have full visibility for reconciliation
17. As an admin, I want to see total expenses by time period, so that I can understand spending trends
18. As an admin, I want to see approval and rejection metrics, so that I can identify bottlenecks
19. As an admin, I want to view ticket volume trends (weekly/monthly), so that I can predict workload
20. As an admin, I want to see which managers are processing claims fastest, so that I can identify best practices
21. As an admin, I want to view the complete audit log, so that I have full compliance tracking
22. As an admin, I want to access user management, so that I can set up reporting relationships and roles

## Implementation Decisions

### 1. Data Model & Schema

**Expense Claim Entity:**
- `id` (UUID): Unique identifier
- `employee_id` (UUID): Who submitted the claim
- `manager_id` (UUID): The employee's direct manager
- `amount` (Decimal): Expense amount (0.01 to 100,000)
- `description` (String): What the expense was for (10-500 characters)
- `category` (Enum): travel, meals, supplies, other
- `receipt_url` (Optional String): URL to receipt/documentation
- `status` (Enum): draft, submitted, pending_manager_review, approved, rejected, processed, cancelled
- `rejection_reason` (Optional String): Why manager rejected (mandatory if rejected)
- `submitted_at` (DateTime): When claim was submitted
- `created_at` (DateTime): When claim was created
- `updated_at` (DateTime): Last modification timestamp
- `processed_at` (Optional DateTime): When finance processed the claim

**User Entity:**
- `id` (UUID): Unique identifier
- `email` (String): User email
- `name` (String): User name
- `role` (Enum): employee, manager, finance, admin
- `manager_id` (Optional UUID): Direct manager for employees

**Budget Entity:**
- `id` (UUID): Unique identifier
- `employee_id` (UUID): Employee for this budget
- `period` (String): "monthly" or "annual"
- `limit` (Decimal): Budget limit
- `start_date` (DateTime): When budget period starts
- `end_date` (DateTime): When budget period ends

**Audit Log Entity:**
- `id` (UUID): Unique identifier
- `claim_id` (UUID): Associated claim
- `actor_id` (UUID): Who performed the action
- `action` (String): What was done (submitted, approved, rejected, processed, etc.)
- `timestamp` (DateTime): When action occurred
- `details` (JSON): Additional context (e.g., rejection reason)

### 2. Workflow States & Transitions

```
DRAFT → SUBMITTED → PENDING_MANAGER_REVIEW → APPROVED → PROCESSED
                                           → REJECTED (new submission required)
DRAFT → CANCELLED
SUBMITTED → CANCELLED
```

**State Transition Rules:**
- Draft: Employee creates and edits claims
- Submitted: Employee submits; claim awaits manager review
- Pending_Manager_Review: Manager queue state (for tracking)
- Approved: Manager approved; awaiting finance processing
- Rejected: Manager rejected with mandatory comment; requires new submission
- Processed: Finance marked as processed/paid
- Cancelled: Employee cancelled in draft or submitted state

### 3. Role-Based Access Control

**Employee:**
- Create, read, update (draft only), delete (draft/submitted only) own claims
- Submit own draft claims
- View own claims and their status
- Cannot view other employees' claims

**Manager:**
- View submitted claims from direct reports only
- Approve claims from direct reports
- Reject claims from direct reports (with mandatory comment)
- View audit trail for own team's claims

**Finance:**
- View all approved claims
- Mark approved claims as processed
- View all claims and audit trails
- Cannot approve/reject claims

**Admin:**
- Full read access to all claims and audit logs
- Access to dashboard analytics
- User and budget management
- Cannot submit or approve claims

### 4. Multi-Approver Logic for High-Value Claims

**Claims > $10,000:**
- Require manager approval first
- Automatically escalate to Finance Director (special role) if total approvals exceed budget threshold
- Implementation: Store approval chain on claim, track each approval separately in audit log

### 5. Budget Constraints

**Budget Management:**
- Each employee has a monthly budget limit (configurable per user)
- System validates claims against remaining budget before allowing submission
- Budget constraints are checked at submission time, not at approval
- Validation: `claim_amount + sum(approved_claims_this_period) <= budget_limit`
- Budget periods reset monthly (configurable to yearly)

### 6. API Endpoints & Structure

**Expense Claims:**
- `POST /api/v1/claims` - Create new claim (draft)
- `GET /api/v1/claims` - List claims (filtered by role)
- `GET /api/v1/claims/{id}` - Get claim details
- `PUT /api/v1/claims/{id}` - Update claim (draft only)
- `DELETE /api/v1/claims/{id}` - Cancel claim (draft/submitted)
- `POST /api/v1/claims/{id}/submit` - Submit claim (draft → submitted)
- `POST /api/v1/claims/{id}/approve` - Approve claim (manager only)
- `POST /api/v1/claims/{id}/reject` - Reject claim with reason (manager only)
- `POST /api/v1/claims/{id}/process` - Process claim (finance only)

**Admin Dashboard:**
- `GET /api/v1/admin/stats` - Analytics (total expenses, counts, trends)
- `GET /api/v1/admin/audit-logs` - Full audit trail with pagination
- `GET /api/v1/admin/users` - User management
- `GET /api/v1/admin/budgets` - Budget configuration

**Authentication:**
- `POST /api/v1/auth/login` - Mocked login (returns JWT with role info)

### 7. Validation Rules

**Claim Submission Validation:**
- Amount: $0.01 to $100,000
- Description: 10-500 characters, required
- Category: Must be from enum (travel, meals, supplies, other)
- Receipt URL: Optional, but if provided must be valid URL
- Budget check: Total including this claim must not exceed employee's budget
- Employee can only submit for themselves
- Manager can only approve/reject own team's claims
- Rejection requires comment (mandatory, min 10 characters)
- Claims can only be edited in draft state

**Workflow Validation:**
- Can only submit from draft state
- Can only approve/reject from submitted state
- Can only process from approved state
- Multi-approval: Claims > $10k tracked with approval chain

### 8. Pagination & Filtering

**List Endpoints Pagination:**
- Default page size: 20
- Max page size: 100
- Offset-based pagination with `offset` and `limit` query parameters

**Filtering Options:**
- By status (comma-separated values)
- By date range (created_from, created_to)
- By amount range (min_amount, max_amount)
- By category
- Search by employee name or claim ID

### 9. Audit Logging

**Audit Log Captures:**
- Who performed the action
- What action was performed (create, submit, approve, reject, process, cancel)
- When the action occurred
- Details (e.g., approval reason, rejection reason, amount)
- For state transitions: old state → new state

**Audit Trail Immutable:**
- Cannot be modified after creation
- Finance and Admin have read access
- Managers can see own team's audit logs

### 10. Error Handling & Response Codes

**Standard HTTP Status Codes:**
- `200 OK` - Successful GET, successful state transition
- `201 Created` - Successful POST (claim created)
- `400 Bad Request` - Validation error (amount out of range, invalid category, etc.)
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions (e.g., manager trying to approve non-team claim)
- `404 Not Found` - Claim not found
- `409 Conflict` - Invalid state transition (e.g., trying to approve draft claim)
- `422 Unprocessable Entity` - Business logic violation (e.g., budget exceeded)

**Error Response Format:**
```json
{
  "error": "error_code",
  "message": "Human readable message",
  "details": {}
}
```

### 11. Authentication (Mocked)

**Mocked Authentication:**
- No external identity provider
- Login endpoint accepts username/password
- Returns JWT token with payload: `{user_id, email, name, role}`
- Token included in Authorization header: `Bearer <token>`
- For testing: Pre-configured test users in memory

**Test Users:**
- employee1@company.com (Employee)
- employee2@company.com (Employee, reports to manager1)
- manager1@company.com (Manager, manages employee2)
- finance1@company.com (Finance)
- admin1@company.com (Admin)

### 12. Data Persistence

**In-Memory Storage:**
- All data stored in Python dictionaries/lists in memory
- No database required
- Data lost when server restarts (acceptable for MVP)
- Structure: Collections for users, claims, budgets, audit_logs

### 13. API Response Format

**Standard Response Wrapper:**
```json
{
  "success": true,
  "data": {},
  "message": "Optional message",
  "timestamp": "ISO8601 timestamp"
}
```

**List Response with Pagination:**
```json
{
  "success": true,
  "data": [],
  "pagination": {
    "offset": 0,
    "limit": 20,
    "total": 150,
    "has_more": true
  },
  "timestamp": "ISO8601 timestamp"
}
```

## Testing Decisions

### Testing Strategy

**What Makes a Good Test:**
- Tests external behavior through API endpoints (not implementation details)
- Tests real business logic flows (submit → approve → process)
- Tests role-based access control (only managers can approve own team)
- Tests validation rules (budget constraints, amount limits)
- Tests error conditions and edge cases
- Uses in-memory data store (same as production)

### Test Coverage

**Unit Tests:**
- Validation functions (budget calculation, status transitions, amount validation)
- Business logic (who can perform which actions, approval chains)
- Permission checks (role-based access)

**Integration Tests:**
- Full claim submission flow (create → submit → approve → process)
- Role-based workflows (employee creates, manager approves, finance processes)
- Multi-approver scenarios (claims > $10k)
- Budget constraint enforcement
- Audit logging for each action
- Error cases (invalid state transitions, insufficient permissions)

**API Tests:**
- All endpoints respond with correct status codes
- Pagination works correctly
- Filtering and search functionality
- Authentication and authorization
- Request/response validation

### Test Structure

- Use `pytest` for test framework
- Use `pytest-asyncio` for async test support
- Use `TestClient` from FastAPI for API testing
- Fixtures for: test users, test claims, test data setup
- Fixtures reset data between tests

### Test Seams

**Primary Testing Seam:** API endpoint layer
- Test entire claim workflow through HTTP endpoints
- Validates entire stack: routing, validation, authorization, business logic, persistence
- Single high-level seam covers all behavior

## Out of Scope

1. **Email Notifications**: No email sending for approvals/rejections (can be added via webhooks)
2. **File Upload**: Receipt URLs are text input only (not actual file storage)
3. **Multi-Currency Support**: All amounts in single currency
4. **Approval Delegation**: Managers cannot delegate their approvals
5. **Bulk Operations**: No bulk claim upload or batch processing
6. **Export Functionality**: No CSV/Excel export (can be added)
7. **Scheduled Tasks**: No background jobs or scheduled processing
8. **Real Authentication**: No OAuth/LDAP/SSO integration
9. **Database Persistence**: In-memory only for MVP
10. **Mobile App**: API only, no UI/mobile client
11. **Real-time Updates**: No WebSocket support for live notifications
12. **Cost Allocation**: No project or cost center tracking
13. **Recurring Expenses**: Single expense per submission
14. **Approval Levels**: No hierarchical approval chains beyond manager → finance

## Further Notes

### Architecture Overview

The system will be structured as a single FastAPI application with clear layer separation:

1. **Routing Layer** (`routers/`): API endpoints, request/response handling
2. **Schema Layer** (`schemas/`): Pydantic models for validation
3. **Service Layer** (`services/`): Business logic (claim workflow, budget checks, permissions)
4. **Repository Layer** (`repositories/`): Data access (in-memory storage)
5. **Models Layer** (`models/`): Data models (Expense, User, Budget, AuditLog)
6. **Middleware** (`middleware/`): Authentication, error handling
7. **Utilities** (`utils/`): Helpers (JWT, decorators, validators)

### Key Technical Decisions

1. **Async FastAPI**: Full async/await for scalability
2. **Pydantic Validation**: Strong input validation at schema level
3. **JWT for Auth**: Stateless mocked authentication with JWT tokens
4. **In-Memory Storage**: Dict-based repositories for simplicity
5. **Decorators for RBAC**: Custom decorators for role-based access control
6. **Comprehensive Logging**: All actions logged to audit trail
7. **Enums for States**: Type-safe status and role management

### Success Criteria

- ✅ All user stories implemented and tested
- ✅ API endpoints follow REST conventions
- ✅ 85%+ test coverage
- ✅ All validation rules enforced
- ✅ Audit trail complete and immutable
- ✅ Role-based access control working correctly
- ✅ Budget constraints enforced
- ✅ Multi-approver logic for high-value claims
- ✅ Comprehensive error handling
- ✅ Production-ready code quality
