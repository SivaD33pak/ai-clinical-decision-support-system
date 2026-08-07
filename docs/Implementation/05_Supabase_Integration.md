# 05 - Supabase Engineering Specification

> **Project:** AI Clinical Decision Support System (AI-CDSS)
>
> **Version:** 1.0
>
> **Document:** Supabase Engineering Specification
>
> **Part:** 1
>
> **Status:** Infrastructure Foundation
>
> **Audience:** Human Developers & AI Coding Agents

---

# Purpose

This document defines the engineering standards governing the Supabase infrastructure used by the AI Clinical Decision Support System.

Supabase is the cloud infrastructure layer responsible for:

- Authentication
- PostgreSQL Database
- Object Storage
- Security
- Data Persistence

Supabase is **not** responsible for:

- AI inference
- Business logic
- Medical decision making
- Image processing

Those responsibilities belong to the backend.

This document defines how Supabase should be configured and how every application layer must communicate with it.

---

# Engineering Philosophy

Supabase is treated as an infrastructure service.

It should remain completely hidden behind the Repository Layer.

The Flutter application must never communicate with Supabase directly (except authentication if explicitly designed).

The Backend is the owner of business data.

---

# Infrastructure Architecture

The complete architecture is

```
Flutter

↓

FastAPI Backend

↓

Repository Layer

↓

Supabase

↓

PostgreSQL

Storage

Authentication
```

Supabase never communicates directly with the AI Model.

---

# RULE-076

## Supabase Is Infrastructure

Priority

CRITICAL

Requirement

Supabase must only provide infrastructure services.

Responsibilities

- Authentication
- Database
- Object Storage

Never

- Execute business logic
- Execute AI inference
- Validate medical predictions

Reason

Infrastructure should never own business logic.

---

# RULE-077

## Backend Owns Business Logic

Priority

CRITICAL

Requirement

Every business operation must pass through the backend.

Correct

```
Flutter

↓

Backend

↓

Repository

↓

Supabase
```

Incorrect

```
Flutter

↓

Supabase
```

Reason

Business logic must remain centralized.

---

# RULE-078

## Repository Pattern

Priority

CRITICAL

Requirement

Only repositories communicate with Supabase.

Allowed

```
PredictionRepository

AuthenticationRepository

HistoryRepository
```

Forbidden

```
PredictionService

↓

Supabase SDK
```

Repositories isolate infrastructure from business logic.

---

# RULE-079

## Single Supabase Client

Priority

CRITICAL

Requirement

Only one Supabase client should exist.

Created during backend startup.

Injected using Dependency Injection.

Never instantiate multiple clients.

---

# RULE-080

## Environment Variables

Priority

CRITICAL

Every secret must come from environment variables.

Required

```
SUPABASE_URL

SUPABASE_ANON_KEY

SUPABASE_SERVICE_ROLE_KEY
```

Never hardcode credentials.

---

# Supabase Responsibilities

The project uses Supabase for

## Authentication

Responsible for

- Login
- Registration
- Session Management
- Password Recovery

Authentication logic remains inside the Authentication feature.

---

## PostgreSQL Database

Responsible for

- Users
- Predictions
- Metadata

Database never stores

- AI models
- Heatmaps
- Temporary files

---

## Object Storage

Responsible for

- Chest X-ray images
- Generated heatmaps (future)
- User profile images

Storage is not a database.

Metadata belongs in PostgreSQL.

---

# Project Configuration

The Supabase project should contain

```
Authentication

↓

Database

↓

Storage

↓

Policies

↓

Functions (Future)
```

Version 1 does not require Edge Functions.

---

# Environment Configuration

Every environment should use independent credentials.

Recommended

```
Development

↓

Local Backend

↓

Development Supabase
```

Future

```
Production Backend

↓

Production Supabase
```

Development and production must remain isolated.

---

# RULE-081

## Environment Separation

Priority

HIGH

Requirement

Never share production credentials with development.

Each environment must maintain

- Separate database
- Separate storage
- Separate authentication

---

# Bootstrap Lifecycle

Backend startup should follow

```
Load Environment

↓

Validate Configuration

↓

Initialize Supabase Client

↓

Test Connection

↓

Register Repositories

↓

Application Ready
```

Supabase must be initialized before repositories.

---

# Storage Architecture

Storage should contain separate buckets.

```
xray-images

profile-images

heatmaps (Future)

reports (Future)
```

Buckets should never mix unrelated content.

---

# RULE-082

## Bucket Isolation

Priority

HIGH

Each bucket owns one responsibility.

Correct

```
xray-images

↓

Medical Images
```

Incorrect

```
uploads/

↓

Everything
```

---

# Naming Standards

Database

snake_case

Example

```
prediction_history

user_profiles
```

Buckets

snake_case

Example

```
xray_images

profile_images
```

Primary Keys

UUID

Never auto increment.

---

# Folder Ownership

Supabase should own

```
Authentication

Database

Storage
```

The backend owns

```
Repositories

Business Logic

Inference

Validation
```

Flutter owns

```
Presentation

State

Navigation
```

Ownership boundaries must never overlap.

---

# Dependency Rules

Supabase must never depend on

- Flutter
- AI Models
- Business Services

The backend depends on Supabase.

Not the other way around.

---

# Logging

Log

- Connection Success
- Connection Failure
- Authentication Events
- Storage Upload
- Database Insert

Never log

- Passwords
- Tokens
- Medical Information

---

# Error Handling

Possible failures

- Invalid Credentials
- Database Offline
- Storage Failure
- Authentication Failure
- Timeout

Every failure should be converted into backend exceptions.

Never expose raw Supabase exceptions.

---

# Forbidden Practices

The following are prohibited.

❌ Flutter writing directly to PostgreSQL

❌ Flutter uploading directly to Storage

❌ Services accessing Supabase directly

❌ Multiple Supabase clients

❌ Hardcoded credentials

❌ Shared storage buckets

❌ Business logic inside Supabase

❌ AI models stored inside PostgreSQL

❌ Medical calculations inside SQL

---

# AI Coding Agent Rules

The coding agent must

✓ Use Dependency Injection

✓ Create one Supabase client

✓ Respect Repository Pattern

✓ Use environment variables

✓ Separate Storage from Database

✓ Separate Authentication from Business Logic

✓ Respect bucket ownership

The coding agent must never

✗ Hardcode credentials

✗ Access Supabase outside repositories

✗ Store images inside PostgreSQL

✗ Mix infrastructure with business logic

---

# Definition of Done

Part 1 is complete when

- [ ] Supabase project created
- [ ] Authentication enabled
- [ ] PostgreSQL available
- [ ] Storage enabled
- [ ] Environment variables configured
- [ ] Backend bootstrap updated
- [ ] Dependency Injection configured
- [ ] Single Supabase client implemented
- [ ] Bucket strategy defined
- [ ] Engineering rules documented

No database schema should be created during this phase.

The objective is to establish a clean and scalable infrastructure foundation before implementing tables, security policies, and backend integration.

---

# Next Part

Part 2 covers

- Database Engineering Standards
- Table Design
- Relationship Rules
- UUID Strategy
- Timestamp Strategy
- Indexing
- Constraints
- Migration Rules
- Repository Mapping
- AI Coding Agent Standards

# 05 - Supabase Engineering Specification

> **Project:** AI Clinical Decision Support System (AI-CDSS)
>
> **Version:** 1.0
>
> **Document:** Supabase Engineering Specification
>
> **Part:** 2
>
> **Status:** Database Engineering Standards
>
> **Audience:** Human Developers & AI Coding Agents

---

# Purpose

This document defines the database architecture of the AI Clinical Decision Support System.

Every table, relationship, constraint, and index must comply with these engineering standards.

The objective is to create a scalable database that supports future expansion without requiring structural redesign.

---

# Database Philosophy

The PostgreSQL database stores application data.

It does **NOT** store:

- AI models
- Image processing logic
- Medical decisions
- Business logic

Those responsibilities belong to the AI Core and Backend.

The database should only persist information.

---

# Database Architecture

```
Flutter

↓

FastAPI

↓

Repository

↓

Supabase PostgreSQL

↓

Tables

↓

Relationships

↓

Indexes
```

Repositories are the only layer allowed to access database tables.

---

# RULE-083

## Database Owns Persistence

Priority

CRITICAL

Requirement

The database only stores information.

It must never

- Execute business rules
- Perform AI inference
- Calculate predictions

Reason

Persistence should remain independent from application logic.

---

# RULE-084

## UUID Primary Keys

Priority

CRITICAL

Every table must use UUID as the primary key.

Correct

```
id UUID PRIMARY KEY
```

Incorrect

```
id SERIAL
```

Reason

UUIDs scale better and prevent predictable identifiers.

---

# RULE-085

## Timestamp Strategy

Priority

CRITICAL

Every table must include

```
created_at

updated_at
```

Both timestamps should be generated automatically.

Reason

Auditability and future synchronization.

---

# RULE-086

## Soft Delete Strategy

Priority

HIGH

Version 1 should avoid permanent deletion.

Instead use

```
deleted_at
```

Future features can restore records when necessary.

---

# Core Database Tables

Version 1 requires only a small set of tables.

```
profiles

predictions
```

Future versions

```
blood_reports

notifications

doctor_accounts

patient_notes
```

The schema should allow these additions without redesign.

---

# Profiles Table

Purpose

Stores user profile information.

Fields

```
id

email

full_name

avatar_url

created_at

updated_at
```

The authentication credentials remain managed by Supabase Authentication.

The Profiles table stores only application-specific data.

---

# RULE-087

## Authentication Separation

Priority

CRITICAL

Authentication data belongs to

```
Supabase Auth
```

Application profile data belongs to

```
profiles
```

Never duplicate authentication information.

---

# Predictions Table

Purpose

Stores every AI prediction generated by the application.

Fields

```
id

user_id

prediction

confidence

image_url

model_version

prediction_time

created_at

updated_at
```

Future

```
heatmap_url

doctor_notes

blood_report_id
```

---

# Relationships

```
profiles

1

↓

∞

predictions
```

One user

↓

Many predictions

Every prediction belongs to exactly one user.

---

# RULE-088

## Foreign Keys

Priority

CRITICAL

Every relationship must use foreign keys.

Correct

```
user_id

↓

profiles.id
```

Never store orphaned records.

---

# Relationship Rules

Every prediction requires

```
user_id
```

No anonymous prediction history.

Unauthenticated users may still receive predictions, but those predictions should not be persisted unless a user account exists.

---

# Model Version

Every prediction should store

```
model_version
```

Example

```
1.0.0
```

Future AI upgrades become traceable.

---

# Prediction Time

Every prediction should record

```
prediction_time
```

Measured in milliseconds.

Useful for

- Performance monitoring
- Benchmarking

---

# RULE-089

## Immutable Prediction Records

Priority

HIGH

Prediction records should never be modified after creation.

Updates allowed only for

- Metadata
- Doctor Notes (Future)

Medical prediction values remain immutable.

---

# Constraints

Every prediction requires

- user_id
- prediction
- confidence
- image_url

Confidence should remain within

```
0.0

↓

1.0
```

Database constraints should enforce valid ranges where appropriate.

---

# RULE-090

## Required Fields

Priority

CRITICAL

Business-critical fields must not be nullable.

Examples

```
prediction

confidence

user_id
```

Optional

```
heatmap_url

doctor_notes
```

---

# Index Strategy

Indexes improve query performance.

Recommended indexes

```
user_id

created_at

prediction
```

Do not index every column.

Only index frequently queried fields.

---

# RULE-091

## Query Optimization

Priority

HIGH

Repositories should query indexed fields whenever possible.

Avoid full table scans.

---

# Repository Mapping

Each table belongs to exactly one repository.

```
profiles

↓

AuthenticationRepository

predictions

↓

PredictionRepository
```

Repositories own persistence.

Services own business logic.

---

# Migration Rules

Every schema change must occur through migrations.

Never manually edit production tables.

Migration naming

```
001_create_profiles.sql

002_create_predictions.sql
```

Future

```
003_add_heatmap.sql
```

---

# RULE-092

## Backward Compatibility

Priority

HIGH

Database migrations must preserve existing data whenever possible.

Avoid destructive schema changes.

---

# Future Expansion

The schema should support

```
Blood Reports

↓

Prediction Fusion

↓

Clinical Notes

↓

Doctor Accounts
```

without redesigning existing tables.

---

# Forbidden Practices

The following are prohibited.

❌ Business logic inside SQL

❌ AI inference inside PostgreSQL

❌ Duplicate profile tables

❌ Missing foreign keys

❌ Auto-increment IDs

❌ Hardcoded timestamps

❌ Missing indexes on frequently queried fields

❌ Direct database access from services

❌ Direct database access from Flutter

---

# AI Coding Agent Rules

The coding agent must

✓ Create normalized tables

✓ Use UUID primary keys

✓ Use foreign keys

✓ Use automatic timestamps

✓ Respect repository ownership

✓ Create indexes where appropriate

✓ Use migrations

The coding agent must never

✗ Duplicate authentication data

✗ Store AI models

✗ Store business logic

✗ Bypass repositories

✗ Use SERIAL IDs

---

# Definition of Done

Part 2 is complete when

- [ ] Profiles table designed
- [ ] Predictions table designed
- [ ] Foreign keys configured
- [ ] UUID strategy implemented
- [ ] Timestamp strategy implemented
- [ ] Constraints documented
- [ ] Index strategy documented
- [ ] Migration strategy defined
- [ ] Repository mapping completed
- [ ] Future expansion planned

The database structure should now be fully designed and ready for security policies and storage configuration.

---

# Next Part

Part 3 covers

- Row Level Security (RLS)
- Storage Buckets
- Authentication Policies
- JWT Authentication
- Storage Rules
- Bucket Permissions
- Security Engineering Standards
- AI Coding Agent Security Rules

# 05 - Supabase Engineering Specification

> **Project:** AI Clinical Decision Support System (AI-CDSS)
>
> **Version:** 1.0
>
> **Document:** Supabase Engineering Specification
>
> **Part:** 3
>
> **Status:** Security & Storage Engineering
>
> **Audience:** Human Developers & AI Coding Agents

---

# Purpose

This document defines the security architecture for the AI Clinical Decision Support System.

Security is responsible for protecting

- User Accounts
- Medical Predictions
- Uploaded Chest X-rays
- Future Heatmaps
- Future Blood Reports

The goal is to ensure users can only access their own resources.

---

# Security Philosophy

Every request should follow the principle of

```
Least Privilege
```

A user should only have access to

- Their account
- Their prediction history
- Their uploaded images

Nothing else.

---

# Security Architecture

```
Flutter

↓

JWT Token

↓

FastAPI

↓

Authentication Middleware

↓

Repository

↓

Supabase

↓

RLS Policies
```

Every database request passes through security validation.

---

# RULE-093

## Row Level Security (RLS)

Priority

CRITICAL

Requirement

Every table must have

```
Row Level Security Enabled
```

No exceptions.

Reason

Without RLS, authenticated users may access records that do not belong to them.

---

# RULE-094

## Default Deny

Priority

CRITICAL

Every table should deny access by default.

Permissions must be granted explicitly.

Never

```
Allow Everyone
```

---

# Authentication Strategy

Supabase Authentication is responsible for

- Registration
- Login
- Session
- Password Reset

FastAPI validates authenticated users using JWTs before executing business logic.

---

# RULE-095

## Authentication Ownership

Priority

CRITICAL

Authentication belongs to

```
Supabase Auth
```

Business logic belongs to

```
FastAPI
```

Flutter should never validate users manually.

---

# JWT Authentication

Every authenticated request should include

```
Bearer Token
```

Flow

```
Flutter

↓

JWT

↓

FastAPI

↓

Token Validation

↓

Repository

↓

Supabase
```

If the token is invalid

↓

Reject request.

---

# RULE-096

## JWT Validation

Priority

CRITICAL

Every protected endpoint must validate

- Token
- User ID
- Expiration

Never trust client-provided user identifiers.

Always derive the authenticated user from the validated token.

---

# Storage Architecture

Supabase Storage stores

```
Chest X-rays

Profile Images

Heatmaps (Future)

Reports (Future)
```

Storage buckets should remain independent.

---

# Bucket Design

Version 1

```
xray_images

profile_images
```

Future

```
heatmaps

blood_reports

reports
```

Each bucket has one responsibility.

---

# RULE-097

## Bucket Isolation

Priority

HIGH

Every bucket owns one file type.

Correct

```
xray_images
```

Incorrect

```
uploads
```

Mixed-purpose buckets should be avoided.

---

# Storage Permissions

Every uploaded image belongs to one user.

Only

- Owner
- Authorized backend

may access the image.

Public buckets should not be used for medical images.

---

# RULE-098

## Private Storage

Priority

CRITICAL

Medical images must remain private.

Never expose direct public URLs for diagnostic images.

Image access should occur through secure backend logic or time-limited signed URLs.

---

# Signed URLs

The backend should generate signed URLs whenever temporary image access is required.

Workflow

```
Flutter

↓

Backend

↓

Supabase

↓

Signed URL

↓

Flutter
```

Signed URLs should expire after a short duration.

---

# RULE-099

## Signed URL Expiration

Priority

HIGH

Signed URLs should have limited validity.

Recommended

```
5–15 Minutes
```

Never generate permanent public links.

---

# Prediction Security

Prediction history belongs only to its owner.

Relationship

```
Authenticated User

↓

Prediction History

↓

Owner Access
```

No cross-user visibility.

---

# RULE-100

## Ownership Verification

Priority

CRITICAL

Every repository query must verify ownership.

Example

Correct

```
WHERE user_id = authenticated_user
```

Incorrect

```
SELECT * FROM prediction_history
```

---

# Database Policies

Profiles

Allowed

- Read Own Profile
- Update Own Profile

Denied

- Read Other Profiles
- Modify Other Profiles

---

# Prediction Policies

Allowed

- Insert Own Prediction
- Read Own Prediction

Denied

- Read Other Predictions
- Modify Other Predictions
- Delete Other Predictions

---

# Storage Policies

Allowed

- Upload Own Image
- Read Own Image
- Delete Own Image

Denied

- Read Other Images
- Upload to Other Users' Directories

---

# RULE-101

## Principle of Ownership

Priority

CRITICAL

Every resource must have an owner.

Examples

```
Prediction

↓

Owner

Image

↓

Owner

Profile

↓

Owner
```

Anonymous ownership is prohibited.

---

# Secret Management

The following values are secrets

```
SUPABASE_SERVICE_ROLE_KEY

JWT Secret

Database Credentials
```

Secrets belong only in environment variables.

Never commit secrets to Git.

---

# RULE-102

## Secret Isolation

Priority

CRITICAL

Never

- Hardcode secrets
- Commit secrets
- Print secrets in logs

---

# Logging Policy

Allowed

- Authentication Success
- Authentication Failure
- Prediction Saved
- Upload Completed

Forbidden

- Password
- Token
- Image Content
- Medical Prediction Details

Logs should never expose patient-sensitive information.

---

# Error Handling

Security-related failures should return generic messages.

Correct

```
Unauthorized
```

Incorrect

```
Token expired because...
```

Avoid revealing implementation details.

---

# RULE-103

## Security Error Responses

Priority

HIGH

Security responses should never reveal

- Internal IDs
- SQL Queries
- JWT Structure
- Stack Traces

---

# Future Security

The architecture should support

- Multi-factor Authentication
- Doctor Accounts
- Role-Based Access Control
- Audit Logs
- Access Monitoring

without redesigning the authentication flow.

---

# Forbidden Practices

The following are prohibited.

❌ Public storage buckets for medical images

❌ Disabled Row Level Security

❌ Hardcoded JWTs

❌ Public prediction history

❌ Exposing database IDs

❌ Logging passwords

❌ Logging tokens

❌ Public access to profile images

❌ Flutter accessing Storage directly

❌ Flutter bypassing backend authorization

---

# AI Coding Agent Rules

The coding agent must

✓ Enable RLS on every table

✓ Create ownership-based policies

✓ Use signed URLs

✓ Validate JWTs

✓ Respect repository boundaries

✓ Keep storage private

✓ Use environment variables

The coding agent must never

✗ Disable RLS

✗ Use public medical storage

✗ Hardcode secrets

✗ Trust client user IDs

✗ Return raw security exceptions

---

# Definition of Done

Part 3 is complete when

- [ ] Row Level Security enabled
- [ ] Authentication policies configured
- [ ] Prediction policies configured
- [ ] Storage buckets created
- [ ] Bucket permissions configured
- [ ] Private storage enforced
- [ ] Signed URLs implemented
- [ ] JWT validation documented
- [ ] Secret management configured
- [ ] Logging policy implemented
- [ ] Security rules documented

The infrastructure is now secured and ready for backend integration.

---

# Next Part

Part 4 covers

- Backend Repository Integration
- Storage Upload Workflow
- Prediction Persistence
- History Retrieval
- Dependency Injection
- Connection Lifecycle
- Monitoring
- Testing
- Production Checklist
- Final AI Coding Agent Rules

# 05 - Supabase Engineering Specification

> **Project:** AI Clinical Decision Support System (AI-CDSS)
>
> **Version:** 1.0
>
> **Document:** Supabase Engineering Specification
>
> **Part:** 4
>
> **Status:** Backend Integration & Production Readiness
>
> **Audience:** Human Developers & AI Coding Agents

---

# Purpose

This document defines how the backend integrates with Supabase.

After completing this phase,

- Authentication should work.
- Images should upload successfully.
- Predictions should persist.
- History should be retrievable.
- The backend should remain independent of Supabase implementation details.

---

# Integration Philosophy

The backend owns business logic.

Supabase owns infrastructure.

Communication must always occur through repositories.

Correct

```
Service

↓

Repository

↓

Supabase
```

Incorrect

```
Service

↓

Supabase SDK
```

---

# RULE-104

## Backend Owns Infrastructure Access

Priority

CRITICAL

Requirement

Services must never communicate directly with Supabase.

Repositories are the only infrastructure gateway.

Reason

Infrastructure should remain replaceable.

---

# Repository Integration

Each feature owns one repository.

```
Authentication

↓

AuthenticationRepository

Prediction

↓

PredictionRepository

History

↓

HistoryRepository
```

Repositories encapsulate every Supabase operation.

---

# Prediction Save Workflow

Every completed prediction follows

```
Prediction Service

↓

Prediction Repository

↓

Supabase Database

↓

Prediction Saved
```

The repository owns

- Insert
- Update (Future)
- Retrieval

The service owns

- Business validation
- AI orchestration

---

# RULE-105

## Prediction Persistence

Priority

CRITICAL

Requirement

Every successful prediction must be persisted.

Required fields

- User ID
- Prediction
- Confidence
- Image URL
- Model Version
- Prediction Time

Never persist incomplete prediction objects.

---

# Image Upload Workflow

The backend owns every upload.

Workflow

```
Flutter

↓

Backend

↓

Image Validation

↓

Storage Repository

↓

Supabase Storage

↓

Image URL

↓

Prediction Service
```

Flutter should never upload directly.

---

# RULE-106

## Storage Repository

Priority

HIGH

Requirement

Every storage operation belongs inside

```
StorageRepository
```

Responsibilities

- Upload Image
- Delete Image
- Generate Signed URL

Nothing else.

---

# Prediction History Workflow

```
History Request

↓

History Repository

↓

Supabase

↓

Prediction Records

↓

Flutter
```

History should always be retrieved through repositories.

---

# RULE-107

## Read Operations

Priority

HIGH

Repositories own every read query.

Allowed

```
PredictionRepository

↓

SELECT
```

Forbidden

```
PredictionService

↓

SQL
```

---

# Authentication Integration

Authentication flow

```
Flutter

↓

Authentication API

↓

FastAPI

↓

Authentication Repository

↓

Supabase Auth
```

Authentication repositories should remain independent of prediction repositories.

---

# Dependency Injection

Repositories should be injected.

Never instantiate repositories manually.

Correct

```
Dependency Injection

↓

Repository

↓

Service
```

Incorrect

```
Service

↓

new Repository()
```

---

# RULE-108

## Dependency Injection

Priority

CRITICAL

All repositories must be registered during application startup.

Repositories should never instantiate infrastructure manually.

---

# Connection Lifecycle

Application Startup

```
Load Environment

↓

Initialize Logger

↓

Initialize Supabase

↓

Register Repositories

↓

Application Ready
```

Application Shutdown

```
Flush Logs

↓

Close Connections

↓

Shutdown
```

Connections should remain open throughout application execution.

---

# Storage Naming

Images should use predictable naming.

Recommended

```
user_id/

prediction_id.jpg
```

Future

```
user_id/

heatmaps/

reports/
```

Never generate random folder structures.

---

# RULE-109

## Storage Organization

Priority

HIGH

Every uploaded file should belong to exactly one user.

Folder ownership must remain deterministic.

---

# Prediction History Retrieval

Repositories should support

- Latest Predictions
- Prediction Details

Future

- Search
- Filters
- Pagination

The API should remain stable as features expand.

---

# Repository Standards

Repositories should

- Return domain models
- Handle infrastructure exceptions
- Translate Supabase responses

Repositories should never

- Perform AI inference
- Validate medical predictions
- Calculate confidence

---

# RULE-110

## Domain Model Mapping

Priority

HIGH

Repositories convert

```
Supabase Response

↓

Domain Model
```

Services should never receive raw Supabase objects.

---

# Monitoring

Track

- Successful Uploads
- Failed Uploads
- Successful Predictions
- Failed Predictions
- Average Query Time
- Database Connection Status

Monitoring should assist debugging.

---

# Logging

Log

- Authentication
- Uploads
- Prediction Saves
- Prediction Retrieval

Never log

- Passwords
- JWTs
- Medical Images
- Sensitive User Data

---

# Performance

Recommendations

- Reuse Supabase Client
- Minimize duplicate queries
- Avoid unnecessary uploads
- Retrieve only required fields
- Use indexed queries

Repositories should remain efficient.

---

# Error Handling

Infrastructure errors should become application errors.

Example

Instead of

```
SupabaseException
```

Return

```
Prediction could not be saved.
```

Do not expose internal infrastructure.

---

# RULE-111

## Infrastructure Error Mapping

Priority

CRITICAL

Infrastructure exceptions should always be translated into meaningful application exceptions.

Never expose provider-specific errors.

---

# Testing Strategy

Repository Tests

Verify

- Insert Prediction
- Retrieve History
- Upload Image
- Authentication

Integration Tests

Verify

Flutter

↓

Backend

↓

Supabase

Complete workflow should succeed.

---

# Future Expansion

The architecture should support

```
Blood Reports

Doctor Dashboard

Patient Dashboard

Heatmaps

Notifications

Audit Logs
```

without redesigning repositories.

---

# Forbidden Practices

The following are prohibited.

❌ Services accessing Supabase directly

❌ Flutter accessing Storage directly

❌ Duplicate Supabase clients

❌ Duplicate repositories

❌ SQL inside services

❌ Business logic inside repositories

❌ AI inference inside repositories

❌ Hardcoded bucket names

❌ Manual dependency creation

---

# AI Coding Agent Rules

The coding agent must

✓ Use Dependency Injection

✓ Respect Repository Pattern

✓ Create one StorageRepository

✓ Create one AuthenticationRepository

✓ Create one PredictionRepository

✓ Create one HistoryRepository

✓ Return domain models

✓ Translate infrastructure exceptions

✓ Use environment variables

The coding agent must never

✗ Instantiate Supabase repeatedly

✗ Mix infrastructure with business logic

✗ Return raw Supabase responses

✗ Skip repositories

✗ Bypass Dependency Injection

---

# Production Readiness Checklist

Before production deployment

- [ ] Supabase client initialized
- [ ] Authentication working
- [ ] Storage buckets configured
- [ ] Images upload successfully
- [ ] Prediction persistence working
- [ ] History retrieval working
- [ ] Signed URLs implemented
- [ ] Repository pattern verified
- [ ] Dependency Injection configured
- [ ] Error mapping implemented
- [ ] Logging enabled
- [ ] Monitoring configured

---

# Supabase Milestone

The Supabase infrastructure is considered complete when

- Authentication is functional.
- Database persistence is operational.
- Storage uploads work securely.
- Prediction history is retrievable.
- Repositories isolate the backend from Supabase.
- The backend can be migrated to another infrastructure provider with minimal repository changes.

At this stage, Supabase becomes a transparent infrastructure layer rather than a business component.

---

# Next Phase

## 06 - End-to-End System Integration

The next phase covers

- Flutter ↔ Backend Integration
- Backend ↔ AI Integration
- Backend ↔ Supabase Integration
- Authentication Flow
- Prediction Workflow
- Image Upload Pipeline
- History Persistence
- End-to-End Validation
- System Acceptance Testing
- Production Integration