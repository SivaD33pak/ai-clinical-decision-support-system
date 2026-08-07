# 02 - Backend Foundation

> **Project:** AI Clinical Decision Support System (AI-CDSS)
>
> **Version:** 1.0
>
> **Document:** Backend Foundation
>
> **Part:** 1
>
> **Status:** Development Specification

---

# Purpose

This document defines the backend architecture for Version 1 of the AI Clinical Decision Support System.

This document serves as the official implementation guide for backend development.

It defines:

- Project architecture
- Backend responsibilities
- Folder structure
- Feature organization
- Request lifecycle
- Configuration
- API versioning
- Development standards

This document does **not** implement business logic or AI models.

---

# Objectives

At the end of this phase the backend should:

- expose a scalable REST API
- follow Feature-Based Architecture
- isolate business logic from infrastructure
- isolate AI from business logic
- isolate database operations from services
- be ready for AI integration

No AI model should be implemented during this phase.

---

# Backend Responsibilities

The backend is responsible for:

- API endpoints
- Authentication
- Image upload
- Prediction orchestration
- Validation
- Database communication
- File storage
- Logging
- Error handling
- Configuration

The backend is **NOT** responsible for:

- Flutter UI
- AI model training
- Medical diagnosis
- Image annotation

---

# Backend Design Principles

The backend follows several software engineering principles.

---

# 1. Feature-Based Architecture

The project follows a **Vertical Slice (Feature-Based) Architecture**.

Instead of grouping files by technical responsibility:

```
routes/

services/

schemas/
```

each business feature owns everything it needs.

Example

```
prediction/

router.py

service.py

repository.py

schemas.py
```

Every feature is independent.

Advantages

- Easier maintenance
- Better scalability
- Better readability
- Easier testing
- Easier onboarding

---

# 2. Separation of Concerns

Each layer has only one responsibility.

```
Router

↓

Service

↓

Repository

↓

Supabase
```

The Router never communicates directly with the Repository.

The Repository never communicates directly with Flutter.

The Service coordinates the application's business logic.

---

# 3. Repository Pattern

Repositories own every interaction with persistent storage.

```
Prediction Service

↓

Prediction Repository

↓

Supabase
```

Benefits

- Database independence
- Easier testing
- Cleaner services

If Supabase is replaced later, only the Repository changes.

---

# 4. AI Abstraction

Business logic must never communicate directly with AI models.

Instead

```
Prediction Service

↓

Inference Manager

↓

AI Model
```

Future

```
Prediction Service

↓

Inference Manager

↓

DenseNet

↓

Blood Predictor

↓

Symptoms Predictor

↓

Fusion Predictor
```

Adding new AI models should never require modifications to Prediction Service.

---

# 5. Single Responsibility Principle

Every module has exactly one responsibility.

Example

Prediction Service

Responsible for

- prediction workflow

Not responsible for

- uploading images
- database queries
- authentication

---

# 6. API First Design

Everything begins with API contracts.

Flutter communicates only through REST APIs.

Flutter never communicates directly with

- Supabase
- AI Model
- Database

---

# High Level Architecture

```
                     Flutter Application

                              │

                              ▼

                     FastAPI Backend

                              │

               ┌──────────────┴──────────────┐

               ▼                             ▼

        Feature Routers                 Middleware

               │

               ▼

        Application Services

        ┌───────────────┬───────────────┐

        ▼                               ▼

Repositories                  Inference Manager

        ▼                               ▼

Supabase Database             AI Model Registry

                                      ▼

                            DenseNet121 (Version 1)

                                      ▼

                     Blood Model (Future)
```

---

# Backend Folder Structure

The backend follows a Feature-Based Architecture.

```text
backend/
├── app/
│   ├── features/
│   │   ├── auth/
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   └── schemas.py
│   │   ├── prediction/
│   │   │   ├── router.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   └── schemas.py
│   │   └── history/
│   │       ├── router.py
│   │       ├── service.py
│   │       ├── repository.py
│   │       └── schemas.py
│   ├── database/
│   ├── middleware/
│   ├── dependencies/
│   ├── core/
│   └── main.py
│
├── ai_core/
│   ├── inference/
│   ├── models/
│   ├── preprocessing/
│   ├── explainability/
│   └── training/
│
├── tests/
│   └── test_endpoints.py
│
├── requirements.txt
├── .env
├── .env.example
└── README.md
```

This structure should remain unchanged throughout Version 1.

---

# Folder Responsibilities

---

## features/

Contains all business capabilities.

Each feature owns:

- router
- service
- repository
- schemas

No feature should depend directly on another feature's internal files.

---

## ai/

Contains every AI-related implementation.

Subfolders

```
inference/

models/

preprocessing/

explainability/

common/
```

Business logic should never exist inside the AI folder.

---

## database/

Contains shared database configuration.

Responsibilities

- Supabase Client
- Shared database utilities

Business logic is not allowed here.

---

## middleware/

Contains FastAPI middleware.

Examples

- Logging Middleware
- CORS
- Request Timing
- Authentication Middleware (Future)

---

## dependencies/

Contains Dependency Injection providers.

Every feature receives dependencies through this module.

No manual object creation inside routers.

---

## core/

Application-wide configuration.

Contains

- Config
- Logging
- Exceptions
- Security

---

## utils/

Shared helper functions.

Examples

- File helpers
- Validators
- Date formatting
- Utility functions

No business logic.

---

# Request Lifecycle

Every request follows exactly this path.

```
Flutter

↓

HTTP Request

↓

FastAPI Router

↓

Schema Validation

↓

Application Service

↓

Repository / Inference Manager

↓

Supabase / AI Model

↓

Application Service

↓

Response Schema

↓

JSON Response
```

Every request must follow this lifecycle.

No shortcuts are allowed.

---

# Configuration Layer

Every configurable value must be centralized.

Never hardcode

- URLs
- API Keys
- Model Paths
- Upload Directories
- API Versions
- Secrets

Create

```
core/config.py
```

Responsibilities

- Load environment variables
- Validate configuration
- Expose configuration objects

---

# Environment Variables

Create

```
.env
```

Example

```
APP_NAME=AI Clinical Decision Support System

APP_VERSION=1.0.0

API_VERSION=v1

DEBUG=True

SUPABASE_URL=

SUPABASE_KEY=

SECRET_KEY=

MODEL_PATH=models/xray_model.pth

UPLOAD_DIRECTORY=uploads/
```

Never commit this file.

---

Create

```
.env.example
```

Purpose

Allow another developer to configure the project without exposing secrets.

---

# API Versioning

Every endpoint must begin with

```
/api/v1/
```

Examples

```
GET /api/v1/health

POST /api/v1/prediction

GET /api/v1/history

POST /api/v1/auth/login
```

Never expose

```
/predict

/upload
```

Future versions

```
/api/v2/

api/v3/
```

This prevents breaking existing Flutter clients.

---

# Feature Routing

Every feature owns its own router.

Example

```
prediction/router.py
```

Authentication

```
auth/router.py
```

History

```
history/router.py
```

main.py should only register feature routers.

---

# main.py Responsibilities

main.py should remain minimal.

Responsibilities

- Create FastAPI application
- Register middleware
- Register feature routers
- Register exception handlers
- Register startup events

main.py should never contain business logic.

---

# Backend Rules

The following rules are mandatory.

Router

- Receives requests
- Validates input
- Calls Service
- Returns response

Service

- Applies business logic
- Coordinates repositories
- Coordinates AI inference

Repository

- Reads data
- Writes data
- Deletes data

Inference Manager

- Selects AI model
- Executes inference
- Returns prediction

AI Model

- Runs prediction only

---

# Definition of Done

Before continuing to Part 2, the backend must satisfy the following.

- [ ] Backend folder structure created
- [ ] Feature-Based Architecture established
- [ ] Configuration module planned
- [ ] Environment variables documented
- [ ] API versioning strategy finalized
- [ ] Request lifecycle defined
- [ ] Folder responsibilities documented
- [ ] Repository Pattern documented
- [ ] Inference Manager documented
- [ ] main.py responsibilities documented

No endpoints should exist yet.

The objective of Part 1 is to build a scalable backend architecture that is ready for implementation.

---

# Next Part

Part 2 will implement:

- Request & Response Schemas
- Service Layer
- Repository Layer
- Dependency Injection
- Logging
- Exception Handling
- Health Endpoint
- Prediction Endpoint
- Upload Endpoint
- API Contracts
- AI Coding Agent Tasks

# 02 - Backend Foundation

> **Project:** AI Clinical Decision Support System (AI-CDSS)
>
> **Version:** 1.0
>
> **Document:** Backend Foundation
>
> **Part:** 2
>
> **Status:** Development Specification

---

# Purpose

This document defines the implementation of the **Application Layer**.

The Application Layer is responsible for coordinating all business logic.

It acts as the bridge between:

- API Routers
- Repository Layer
- AI Inference Layer

At the end of this phase, the backend should expose its first functional REST APIs while remaining completely independent from the AI implementation.

---

# Objectives

By the end of this phase the backend should have:

- Feature Routers
- Request Validation
- Response Validation
- Service Layer
- Repository Layer
- Dependency Injection
- Logging
- Exception Handling
- REST API Standards
- Health Endpoint
- Upload Endpoint
- Prediction Endpoint (Mock)
- History Endpoint

No real AI prediction should be implemented yet.

---

# Application Layer Overview

The Application Layer coordinates every request.

Every request follows this lifecycle.

```
Flutter

↓

HTTP Request

↓

Feature Router

↓

Schema Validation

↓

Service

↓

Repository

↓

Database

↓

Service

↓

Response Schema

↓

JSON Response
```

If AI is required

```
Service

↓

Inference Manager

↓

AI Model

↓

Service

↓

Response Schema
```

---

# Feature Structure

Each business feature owns its own components.

```
features/

prediction/

│

├── router.py

├── service.py

├── repository.py

└── schemas.py
```

No feature should directly access another feature's internals.

Communication between features must happen through Services.

---

# Router Layer

## Purpose

Routers expose REST endpoints.

They are the entry point into the backend.

Responsibilities

- Receive HTTP request
- Validate Request Schema
- Call Service
- Return Response Schema

Routers must NEVER

- Query database
- Run AI
- Upload files
- Apply business rules

Routers should remain extremely small.

---

# Router Example Flow

```
POST /prediction

↓

Prediction Router

↓

Prediction Service

↓

Return Response
```

---

# Service Layer

## Purpose

Services contain all business logic.

Every business decision belongs here.

Responsibilities

- Coordinate repositories
- Coordinate AI
- Validate business rules
- Transform data
- Coordinate storage

Services NEVER

- Receive HTTP requests
- Return HTTP responses
- Communicate directly with Flutter

---

# Prediction Service

Responsibilities

- Validate prediction workflow
- Call Inference Manager
- Save prediction
- Return Prediction Result

Prediction Service should never know

- DenseNet
- Blood Model
- Future AI Models

It communicates only with the Inference Manager.

---

# History Service

Responsibilities

- Retrieve history
- Retrieve prediction details
- Delete history (Future)

History Service must never communicate directly with Flutter.

---

# Authentication Service

Responsibilities

- Login
- Register
- Logout
- Session Validation

Authentication should use Supabase Auth.

---

# Repository Layer

Repositories communicate with persistent storage.

Repositories NEVER contain business logic.

Responsibilities

- Insert
- Update
- Delete
- Query

Repositories communicate only with

- Supabase Database
- Supabase Storage

---

# Prediction Repository

Responsibilities

Store

- Prediction
- Confidence
- Image URL
- Timestamp

Retrieve

- Prediction
- Prediction Details

No prediction logic exists here.

---

# History Repository

Responsibilities

Retrieve

- Previous Predictions

Delete

- Prediction

Search

- Predictions

---

# Storage Repository

Responsibilities

Upload

- Images
- Heatmaps (Future)

Return

Public URL

No prediction logic.

---

# Dependency Injection

Every Service should be injected.

Never create

```
PredictionService()
```

inside a Router.

Instead

```
Router

↓

Dependency Injection

↓

Prediction Service
```

Benefits

- Easier testing
- Easier mocking
- Loose coupling
- Cleaner architecture

---

# Request Schemas

Every endpoint must have a Request Schema.

Responsibilities

- Validate input
- Define required fields
- Reject invalid requests

Never accept raw JSON without validation.

---

# Response Schemas

Every endpoint must return a Response Schema.

Never return

```
dict
```

Return

```
PredictionResponse

HistoryResponse

HealthResponse
```

Benefits

- Consistent API
- Automatic Swagger
- Type safety

---

# Validation

Every request should be validated before entering the Service Layer.

Validation includes

Image

- Supported format
- Maximum size
- Empty file

Authentication

- Valid token
- Authorized user

Prediction

- Existing upload
- Valid request

Invalid requests should never reach business logic.

---

# Logging

Every request should generate logs.

Required logs

Application Startup

↓

Incoming Request

↓

Business Logic Started

↓

Business Logic Completed

↓

Database Updated

↓

Response Sent

Errors should always include

- Timestamp
- Endpoint
- Error Message

Never use

```
print()
```

Always use Python logging.

---

# Exception Handling

All exceptions should be centralized.

Never expose Python tracebacks.

Bad

```
FileNotFoundError

Traceback...
```

Good

```
{
    "success": false,
    "message": "Uploaded image not found."
}
```

Exceptions should be transformed into standardized responses.

---

# Standard API Response

Every endpoint should follow the same response structure.

Successful

```
{
    "success": true,
    "message": "Prediction completed successfully.",
    "data": {}
}
```

Failure

```
{
    "success": false,
    "message": "Prediction failed.",
    "errors": []
}
```

Never invent different response formats.

---

# API Versioning

Every endpoint must begin with

```
/api/v1/
```

Examples

```
GET /api/v1/health

POST /api/v1/prediction

GET /api/v1/history

POST /api/v1/auth/login
```

Future

```
/api/v2/
```

must not break Version 1.

---

# API Endpoints

## Health

```
GET /api/v1/health
```

Purpose

Verify backend availability.

Returns

- Backend Status
- Version
- Timestamp

No authentication.

---

## Prediction

```
POST /api/v1/prediction
```

Purpose

Trigger prediction workflow.

Current Implementation

Returns mocked prediction.

Future

Calls AI through Inference Manager.

---

## Upload

```
POST /api/v1/prediction/upload
```

Purpose

Receive Chest X-ray.

Responsibilities

- Validate image
- Upload image
- Return upload identifier

Prediction is NOT performed here.

---

## History

```
GET /api/v1/history
```

Purpose

Return previous predictions.

Supports

- Pagination (Future)
- Filtering (Future)

---

## Authentication

```
POST /api/v1/auth/login

POST /api/v1/auth/register
```

Uses Supabase Authentication.

---

# HTTP Status Codes

Use proper status codes.

Success

```
200 OK
```

Created

```
201 Created
```

Validation Failure

```
400 Bad Request
```

Unauthorized

```
401 Unauthorized
```

Not Found

```
404 Not Found
```

Unexpected Error

```
500 Internal Server Error
```

Never return

```
200
```

for failed requests.

---

# AI Coding Agent Tasks

The coding agent should complete the following tasks in order.

1. Create feature routers.

2. Create request schemas.

3. Create response schemas.

4. Create services.

5. Create repositories.

6. Configure Dependency Injection.

7. Configure Logging.

8. Configure Exception Handling.

9. Implement Health endpoint.

10. Implement Upload endpoint.

11. Implement Prediction endpoint (Mock Response).

12. Implement History endpoint.

13. Verify Swagger Documentation.

The AI model should NOT be integrated yet.

Prediction endpoint should return mocked data.

---

# Definition of Done

This phase is complete when

- [ ] Feature Routers exist
- [ ] Services exist
- [ ] Repositories exist
- [ ] Dependency Injection configured
- [ ] Logging configured
- [ ] Exception Handling configured
- [ ] Request Schemas implemented
- [ ] Response Schemas implemented
- [ ] Health endpoint working
- [ ] Upload endpoint validates files
- [ ] Prediction endpoint returns mocked prediction
- [ ] History endpoint returns mocked history
- [ ] Swagger documentation generated

No AI model should exist yet.

The backend should already resemble a production backend even though predictions are mocked.

---

# Next Part

Part 3 will complete the backend by implementing:

- Supabase Integration
- Storage Layer
- Inference Manager
- AI Module Registration
- Startup Events
- Middleware
- Background Tasks
- Backend Testing
- Production Readiness
- Future Scalability

# 02 - Backend Foundation

> **Project:** AI Clinical Decision Support System (AI-CDSS)
>
> **Version:** 1.0
>
> **Document:** Backend Foundation
>
> **Part:** 3
>
> **Status:** Development Specification

---

# Purpose

This document completes the backend architecture.

After completing this phase, the backend should be fully functional from an architectural perspective.

The only missing component should be the trained AI model.

Everything else—including API infrastructure, persistence, middleware, startup lifecycle, and production readiness—should already exist.

---

# Objectives

At the end of this phase the backend should provide:

- Supabase Integration
- Repository Implementations
- Storage Layer
- Inference Manager
- AI Model Registry
- Middleware
- Startup Lifecycle
- Background Tasks
- Backend Testing
- Production Ready Architecture

---

# Persistence Layer

The Persistence Layer is responsible for storing and retrieving application data.

Business logic must NEVER communicate directly with the database.

Correct architecture

```
Router

↓

Service

↓

Repository

↓

Supabase
```

Incorrect

```
Router

↓

Supabase
```

or

```
Service

↓

Supabase
```

---

# Repository Responsibilities

Repositories own database communication.

Allowed responsibilities

- Insert records
- Update records
- Delete records
- Query records

Repositories must NEVER

- Predict diseases
- Validate requests
- Apply business rules
- Generate responses

Repositories are data access components only.

---

# Prediction Repository

Responsibilities

- Save prediction
- Retrieve prediction
- Retrieve prediction details

Stored fields

- User ID
- Prediction
- Confidence
- Image URL
- Created Timestamp
- Module

---

# History Repository

Responsibilities

Retrieve

- Prediction history
- Prediction details

Delete

- Prediction (Future)

Search

- Prediction history (Future)

---

# Authentication Repository

Responsibilities

Communicate with Supabase Authentication.

Supported operations

- Login
- Register
- Session Validation

---

# Storage Layer

Images should never be stored inside the database.

Use Supabase Storage.

Buckets

```
xray-images
```

Future buckets

```
heatmaps

blood-reports

documents
```

The Storage Repository is responsible for

- Upload image
- Delete image
- Generate public URL

Nothing else.

---

# Supabase Integration

Supabase provides

- PostgreSQL Database
- Authentication
- Storage

The backend communicates with Supabase only through Repositories.

No other layer may access Supabase directly.

---

# Database Design

## Users

```
id

email

name

created_at
```

---

## Predictions

```
id

user_id

module

prediction

confidence

image_url

created_at
```

Future

```
heatmap_url

blood_report_url

symptoms
```

The schema should already support future modules.

---

# AI Layer

Business logic must remain completely independent of AI implementation.

Architecture

```
Prediction Service

↓

Inference Manager

↓

Model Registry

↓

Selected Model

↓

Prediction Result
```

Prediction Service should never know

- DenseNet
- Blood Predictor
- Future Models

---

# Inference Manager

The Inference Manager is responsible for coordinating AI models.

Responsibilities

- Receive inference request
- Select appropriate model
- Execute prediction
- Return standardized result

Current

```
Prediction

↓

DenseNet121
```

Future

```
Prediction

↓

DenseNet121

↓

Blood Predictor

↓

Symptom Predictor

↓

Fusion Predictor
```

Only the Inference Manager changes when new AI models are added.

---

# AI Model Registry

Instead of hardcoding models, maintain a registry.

Responsibilities

- Register available models
- Load models
- Retrieve requested model

Benefits

- Easy model replacement
- Multiple model support
- Cleaner architecture

---

# AI Folder Structure

```
ai/

│

├── inference/

│   ├── manager.py

│   ├── registry.py

│   └── selector.py

│

├── models/

│   ├── xray/

│   ├── blood/

│   ├── multimodal/

│   └── common/

│

├── preprocessing/

│

├── explainability/

│

└── utils/
```

---

# Application Lifecycle

The backend should perform initialization automatically.

Startup sequence

```
Server Starts

↓

Load Configuration

↓

Initialize Logger

↓

Connect Supabase

↓

Initialize Inference Manager

↓

Register Models

↓

Load DenseNet

↓

Verify Storage

↓

Application Ready
```

No model should be loaded during requests.

Models should remain in memory.

---

# Shutdown Sequence

On shutdown

- Close database connections
- Flush logs
- Release resources

This prevents resource leaks.

---

# Middleware

The backend should include middleware.

---

## CORS Middleware

Allows Flutter to communicate.

Allowed origins should be configurable.

---

## Logging Middleware

Every request should record

- Method
- Endpoint
- Status Code
- Response Time
- Timestamp

---

## Exception Middleware

Catch unhandled exceptions.

Return standardized error responses.

Never expose Python tracebacks.

---

## Authentication Middleware (Future)

Protect private endpoints.

Public endpoints

- Health
- Login
- Register

Private endpoints

- Prediction
- History

---

# Background Tasks

Long-running tasks should not block API responses.

Future tasks

- Generate Grad-CAM
- Upload Heatmap
- Send Notifications
- Generate PDF Report

Use FastAPI Background Tasks where appropriate.

---

# Error Handling Strategy

Every failure should produce a meaningful response.

Examples

Invalid Image

```
400 Bad Request
```

Unauthorized

```
401 Unauthorized
```

Prediction Failure

```
500 Internal Server Error
```

Storage Failure

```
503 Service Unavailable
```

Every error response should follow the standard API response structure.

---

# Performance Considerations

The backend should be designed for performance.

Recommendations

- Load AI models only once
- Reuse database connections
- Avoid duplicate queries
- Cache frequently used configuration
- Compress uploaded images when appropriate

---

# Security Guidelines

Version 1 should implement

- Environment variables
- Secure secret management
- Input validation
- File validation
- Authentication
- HTTPS in production

Never

- Hardcode API keys
- Expose stack traces
- Trust client input

---

# Backend Testing Strategy

Testing should occur in layers.

---

## Router Testing

Verify

- Correct status codes
- Correct routing
- Validation

---

## Service Testing

Verify

- Business logic
- Prediction workflow
- Authentication workflow

---

## Repository Testing

Verify

- Database operations
- Storage operations

---

## AI Testing (Future)

Verify

- Prediction accuracy
- Confidence generation
- Invalid image handling

---

# Health Endpoint

The Health endpoint should verify

- Backend Status
- Database Connection
- Storage Connection
- AI Model Loaded
- Application Version

Example response

```
{
    "success": true,
    "message": "Application healthy.",
    "data": {
        "backend": "healthy",
        "database": "connected",
        "storage": "connected",
        "model": "loaded",
        "version": "1.0.0"
    }
}
```

This endpoint becomes useful for monitoring and deployment.

---

# Coding Standards

Mandatory rules

- One responsibility per file
- One business feature per folder
- No circular imports
- No hardcoded paths
- No hardcoded secrets
- No direct database access outside repositories
- No direct AI access outside the Inference Manager
- Always validate input
- Always use logging
- Always use typed schemas

---

# Future Expansion

The architecture should support adding new modules without major refactoring.

Adding Blood Report Analysis should require only

```
features/

prediction/

(no changes)

↓

ai/models/blood/

↓

Register Blood Model

↓

Done
```

The Prediction Service remains unchanged.

---

# AI Coding Agent Tasks

The coding agent should complete the following tasks in order.

## Infrastructure

- Configure Supabase client
- Implement repositories
- Implement storage layer
- Configure middleware
- Configure startup lifecycle

---

## AI Infrastructure

- Create Inference Manager
- Create Model Registry
- Create AI folder structure
- Create model loading interface

Do not implement prediction logic.

---

## Application Lifecycle

- Register startup events
- Register shutdown events
- Load configuration
- Initialize logging

---

## Testing

- Router tests
- Service tests
- Repository tests

Prediction tests should use mocked AI responses.

---

# Production Readiness Checklist

Before moving to AI development, verify:

- [ ] Folder structure complete
- [ ] Feature-based architecture implemented
- [ ] Repository pattern implemented
- [ ] Dependency Injection configured
- [ ] Middleware configured
- [ ] Logging configured
- [ ] Exception handling configured
- [ ] Supabase connected
- [ ] Storage configured
- [ ] Startup lifecycle implemented
- [ ] Shutdown lifecycle implemented
- [ ] Health endpoint operational
- [ ] Swagger documentation available
- [ ] Mock prediction endpoint working
- [ ] History endpoint working
- [ ] Authentication integrated
- [ ] Unit testing structure created

---

# Backend Milestone

The Backend Foundation phase is complete when:

- The backend starts successfully.
- The API is fully documented through Swagger.
- Authentication works.
- File uploads work.
- Prediction endpoints return mocked responses.
- History endpoints persist and retrieve data.
- The backend is fully prepared for AI integration.

At this point, the backend behaves like a production-ready service. Replacing the mocked prediction with a real AI model should require changes only within the AI layer and the Inference Manager, leaving the API, services, repositories, and Flutter application unchanged.

---

# Next Phase

**03_AI_Model_Development.md**

The next phase focuses on:

- Dataset selection
- Dataset preparation
- Image preprocessing
- Transfer learning with DenseNet121
- Model training
- Model evaluation
- Exporting the trained model
- Integrating the model with the Inference Manager