# 04 - Flutter Engineering Specification

> **Project:** AI Clinical Decision Support System (AI-CDSS)
>
> **Version:** 1.0
>
> **Document:** Flutter Engineering Specification
>
> **Part:** 1
>
> **Status:** Engineering Rules & Architecture
>
> **Audience:** Human Developers & AI Coding Agents

---

# Purpose

This document defines the engineering standards that every Flutter developer and AI coding agent must follow while implementing the AI Clinical Decision Support System.

This document is NOT a Flutter tutorial.

It is an engineering specification.

Every implementation must comply with these rules.

Any deviation should require explicit justification.

---

# Compliance Levels

Every rule belongs to one of four priorities.

---

## CRITICAL

Must never be violated.

Violation requires redesign.

Example

- UI directly calling Dio
- Widget performing business logic
- Bloc directly accessing Supabase

---

## HIGH

Strong architectural recommendation.

Can only be violated with documented reasoning.

Example

- Every feature owns its own Repository.
- Every feature owns its own Bloc.

---

## MEDIUM

Recommended best practice.

May be adjusted depending on implementation.

Example

- Widget length
- File organization

---

## LOW

Code style and readability improvements.

Example

- Prefer const constructors
- Prefer extension methods

---

# Engineering Philosophy

The Flutter application follows these principles.

---

## Principle 1

Flutter is a Presentation Layer.

Flutter is responsible for

- Displaying UI
- Receiving user interaction
- Managing application state

Flutter is NOT responsible for

- Business logic
- AI processing
- Database operations

---

## Principle 2

Everything is Feature-Based.

The application is organized around business capabilities.

Correct

```
features/

authentication/

prediction/

history/

profile/
```

Incorrect

```
screens/

widgets/

models/
```

Business capabilities always come first.

---

## Principle 3

One Responsibility Per Layer.

Every layer has exactly one responsibility.

```
UI

↓

Bloc

↓

Repository

↓

API

↓

Backend
```

Never skip layers.

---

## Principle 4

Presentation Never Knows Infrastructure.

Widgets never know

- Dio
- Supabase
- FastAPI
- AI Model

Widgets only communicate with Bloc.

---

## Principle 5

Everything is Replaceable.

Any implementation should be replaceable without affecting other layers.

Examples

Replace

```
Dio
```

with

```
GraphQL
```

No widget changes.

Replace

```
FastAPI
```

with

```
NodeJS
```

No UI changes.

Replace

```
DenseNet121
```

with

```
Vision Transformer
```

No Flutter changes.

---

# Flutter Architecture

The application follows Feature-Based Architecture.

```
Flutter

↓

Presentation Layer

↓

Bloc

↓

Repository

↓

API Client

↓

FastAPI Backend
```

Business logic never exists inside Widgets.

---

# Canonical Project Structure

The application must follow this structure.

```
lib/

│

├── app/

│   ├── bootstrap/
│   ├── router/
│   ├── theme/
│   ├── app.dart
│   └── view/

│

├── core/

│   ├── api/
│   ├── constants/
│   ├── extensions/
│   ├── services/
│   ├── utils/
│   └── widgets/

│

├── features/

│   ├── authentication/
│   ├── dashboard/
│   ├── prediction/
│   ├── history/
│   ├── profile/
│   └── settings/

│

├── shared/

│

├── l10n/

│

└── main.dart
```

No folders should be created outside this architecture without architectural approval.

---

# Feature Architecture

Every feature must follow the same internal structure.

```
prediction/

│

├── prediction.dart

│

├── api/

│

├── bloc/

│

├── models/

│

├── repository/

│

├── view/

│

└── widgets/
```

Every feature should look identical.

Consistency is mandatory.

---

# RULE-001

## Feature Isolation

Priority

CRITICAL

Requirement

Every feature must own its own

- Bloc
- Repository
- Models
- Widgets
- API

Reason

Features should be independently maintainable.

Correct

```
features/

prediction/

history/
```

Incorrect

```
repositories/

shared_prediction_repository.dart
```

unless it truly belongs to the shared layer.

Acceptance

Removing one feature should not affect another.

---

# RULE-002

## No Business Logic Inside Widgets

Priority

CRITICAL

Requirement

Widgets only render UI.

Widgets never

- Validate business rules
- Upload files
- Parse responses
- Save history

Correct

```
Widget

↓

Bloc
```

Incorrect

```
Widget

↓

HTTP Request
```

---

# RULE-003

## Bloc Owns State

Priority

CRITICAL

Requirement

Every UI state must originate from Bloc.

Examples

Loading

Success

Failure

Empty

Never manage business state using StatefulWidget.

---

# RULE-004

## Repository Owns Data

Priority

CRITICAL

Requirement

Repositories communicate with APIs.

Bloc never communicates directly with Dio.

Correct

```
Bloc

↓

Repository

↓

API
```

Incorrect

```
Bloc

↓

Dio
```

---

# RULE-005

## API Layer Owns Networking

Priority

CRITICAL

Requirement

Only API classes may use Dio.

Widgets

↓

Never

Bloc

↓

Never

Repository

↓

Calls API

API

↓

Uses Dio

---

# RULE-006

## Backend Is The Single Source Of Truth

Priority

HIGH

Requirement

Flutter never performs medical calculations.

Prediction always comes from the backend.

Never calculate

- Confidence
- Disease
- Medical result

inside Flutter.

---

# RULE-007

## One Feature One Responsibility

Priority

HIGH

Every feature solves one business problem.

Authentication

↓

User Access

Prediction

↓

Disease Prediction

History

↓

Prediction Records

Never merge unrelated responsibilities.

---

# RULE-008

## Shared Components

Priority

HIGH

Only reusable components belong inside

```
shared/
```

Examples

Buttons

Dialogs

Cards

Typography

Spacing

Do not move feature-specific widgets into shared.

---

# RULE-009

## Bootstrap First

Priority

CRITICAL

Application startup must follow

```
main()

↓

bootstrap()

↓

Load Environment

↓

Initialize Supabase

↓

Initialize Dio

↓

Register Repositories

↓

Register Blocs

↓

Run App
```

Never initialize dependencies inside Widgets.

---

# RULE-010

## Navigation

Priority

HIGH

Only GoRouter manages navigation.

Never use

```
Navigator.push()
```

directly unless absolutely required.

All routes belong to

```
app/router/
```

---

# Theme Rules

The application must use one centralized theme.

Never hardcode

- Colors
- Font Sizes
- Border Radius
- Padding

Everything should originate from the Theme.

---

# Asset Rules

Assets belong in

```
assets/

images/

icons/

animations/
```

Never place assets inside feature folders.

---

# Naming Conventions

Classes

PascalCase

Variables

camelCase

Folders

snake_case

Files

snake_case.dart

Widgets

Should end with

```
Widget
```

Pages

Should end with

```
Page
```

Repositories

Should end with

```
Repository
```

Blocs

Should end with

```
Bloc
```

---

# Forbidden Practices

The following are strictly prohibited.

❌ Widget calling Dio

❌ Bloc accessing Supabase

❌ Hardcoded API URLs

❌ Business logic inside UI

❌ Duplicate widgets

❌ Duplicate repositories

❌ Duplicate API clients

❌ Hardcoded colors

❌ Hardcoded strings

❌ Direct navigation from repositories

❌ Global mutable variables

❌ Feature importing another feature's internal files

---

# AI Coding Agent Rules

The coding agent must always

- Respect Feature Architecture
- Respect Repository Pattern
- Respect Bloc Pattern
- Generate reusable widgets
- Prefer composition over duplication
- Keep files focused
- Extract reusable components

The coding agent must never

- Collapse architecture for convenience
- Introduce unnecessary global state
- Bypass repositories
- Skip Bloc

---

# Definition of Done

Part 1 is complete when

- [ ] Project structure established
- [ ] Feature architecture defined
- [ ] Bootstrap architecture documented
- [ ] Engineering philosophy documented
- [ ] Flutter architecture finalized
- [ ] Naming conventions defined
- [ ] Theme rules documented
- [ ] Asset rules documented
- [ ] AI coding rules documented
- [ ] Forbidden practices documented

No UI should be implemented during this phase.

This phase defines the engineering standards that govern every Flutter implementation in the project.

---

# Next Part

Part 2 covers:

- Feature Engineering Standards
- Authentication Rules
- Dashboard Rules
- Prediction Feature Rules
- History Feature Rules
- Profile Feature Rules
- Widget Engineering Standards
- Bloc Engineering Standards
- Repository Engineering Standards

# 04 - Flutter Engineering Specification

> **Project:** AI Clinical Decision Support System (AI-CDSS)
>
> **Version:** 1.0
>
> **Document:** Flutter Engineering Specification
>
> **Part:** 2
>
> **Status:** Feature Development Standards
>
> **Audience:** Human Developers & AI Coding Agents

---

# Purpose

This document defines the engineering standards for every Flutter feature.

Every feature implemented inside the application must comply with these rules.

No feature should invent its own architecture.

Consistency is mandatory.

---

# Feature Philosophy

Every feature represents one business capability.

Examples

```
Authentication

Dashboard

Prediction

History

Profile

Settings
```

A feature owns everything required to complete its responsibility.

Features should be isolated and independently maintainable.

---

# Canonical Feature Structure

Every feature must follow this exact structure.

```
feature_name/

│

├── feature_name.dart

│

├── api/

│

├── bloc/

│

├── models/

│

├── repository/

│

├── view/

│

└── widgets/
```

No additional folders should be created unless approved.

Every feature follows the same layout.

---

# RULE-012

## Feature Independence

Priority

CRITICAL

Requirement

Each feature must be self-contained.

A feature owns

- Bloc
- Repository
- API
- Models
- Widgets
- Views

Reason

Features should be removable without affecting other features.

---

# RULE-013

## Feature Communication

Priority

CRITICAL

Features must NEVER directly access another feature.

Correct

```
Prediction

↓

Repository

↓

Backend
```

Incorrect

```
Prediction

↓

History Bloc
```

If two features require shared functionality, it belongs in

```
shared/

or

core/
```

---

# RULE-014

## One Repository Per Feature

Priority

CRITICAL

Every feature exposes exactly one Repository.

Example

```
PredictionRepository

AuthenticationRepository

HistoryRepository
```

Repositories hide API implementation from the Bloc.

---

# RULE-015

## One Bloc Per Feature

Priority

HIGH

Each feature owns exactly one primary Bloc.

Example

```
PredictionBloc

HistoryBloc

AuthenticationBloc
```

Do not create multiple Blocs unless the feature genuinely requires independent state machines.

---

# RULE-016

## Feature Entry File

Priority

HIGH

Every feature exposes

```
feature_name.dart
```

Purpose

Acts as the public interface of the feature.

Internal implementation should remain hidden.

---

# Authentication Feature

Responsibilities

- Login
- Register
- Logout
- Session Check

Authentication must NEVER

- Upload Images
- Save Predictions
- Retrieve History

Authentication owns only authentication.

---

# Dashboard Feature

Responsibilities

- Display application overview
- Navigate to Prediction
- Display recent prediction summary
- Display quick actions

Dashboard must NEVER

- Run predictions
- Upload images

Dashboard is a presentation feature.

---

# Prediction Feature

Prediction is the core feature.

Responsibilities

- Select image
- Preview image
- Upload image
- Request prediction
- Display prediction
- Display confidence
- Display Grad-CAM (Future)

Prediction does NOT

- Perform AI inference
- Calculate confidence
- Process medical logic

Everything comes from the backend.

---

# Prediction Workflow

```
User

↓

Select Image

↓

Prediction Bloc

↓

Prediction Repository

↓

Prediction API

↓

Backend

↓

Prediction Response

↓

Bloc

↓

UI
```

The UI never communicates with the backend directly.

---

# History Feature

Responsibilities

- Retrieve prediction history
- Display prediction cards
- View prediction details

History must NEVER

- Run predictions
- Upload images

History is read-only.

---

# Profile Feature

Responsibilities

- Display user information
- Edit profile
- Update profile image
- Logout

Profile must not contain application settings.

---

# Settings Feature

Responsibilities

- Theme
- Language
- About
- Privacy

Settings should remain independent from Profile.

---

# RULE-017

## Feature State

Priority

CRITICAL

Every feature must define states.

Minimum

```
Initial

Loading

Success

Failure
```

Optional

```
Empty

Refreshing

Uploading
```

Widgets should react only to states.

---

# RULE-018

## Feature Events

Priority

HIGH

Every feature exposes events.

Example

Prediction

```
PickImage

UploadImage

Predict

Reset
```

Events describe

"What happened"

not

"What should the UI do"

---

# RULE-019

## Feature Widgets

Priority

HIGH

Large pages must be decomposed.

Instead of

```
PredictionPage

900 lines
```

Use

```
PredictionPage

↓

PredictionHeaderWidget

↓

ImagePreviewWidget

↓

PredictionButtonWidget

↓

ResultCardWidget
```

Widgets should remain reusable.

---

# RULE-020

## Screen Size

Priority

MEDIUM

Pages should not exceed

```
300 Lines
```

Widgets should not exceed

```
150 Lines
```

Large widgets should be extracted.

---

# RULE-021

## Widget Responsibilities

Priority

CRITICAL

Widgets only

- Render UI
- Receive interaction

Widgets never

- Upload files
- Parse JSON
- Call API
- Calculate business logic

---

# RULE-022

## Loading States

Priority

HIGH

Every asynchronous operation must have

Loading State.

Example

Prediction

```
Loading Indicator

↓

Prediction Completed
```

Never leave the user wondering.

---

# RULE-023

## Empty States

Priority

HIGH

Every feature displaying collections must support

Empty State.

Example

History

```
No Predictions Yet
```

instead of blank screens.

---

# RULE-024

## Error States

Priority

CRITICAL

Every feature must support

```
Network Error

API Error

Unexpected Error

Validation Error
```

Errors should be user-friendly.

Never display raw exceptions.

---

# RULE-025

## Confirmation Dialogs

Priority

MEDIUM

Destructive actions require confirmation.

Examples

Logout

Delete History

Reset Prediction

---

# RULE-026

## Navigation

Priority

HIGH

Navigation originates only from

Presentation Layer.

Repositories

↓

Never Navigate

Bloc

↓

Never Navigate

Only

Pages

or

Navigation Service

---

# RULE-027

## Image Selection

Priority

HIGH

Prediction Feature owns image selection.

Supported

- Gallery
- Camera

Future

- File Picker

The selected image remains inside Prediction State.

---

# RULE-028

## Prediction Result

Priority

HIGH

Prediction results must be immutable.

Displayed information

- Disease
- Confidence
- Prediction Time
- Uploaded Image
- Heatmap (Future)

Never mutate prediction results.

---

# RULE-029

## Shared Widgets

Priority

HIGH

Reusable UI belongs inside

```
shared/widgets/
```

Examples

Buttons

Cards

Dialogs

Loading Indicators

App Bars

Do not duplicate reusable widgets.

---

# RULE-030

## Feature Assets

Priority

MEDIUM

Feature-specific illustrations belong inside

```
assets/images/
```

Do not duplicate images.

---

# Forbidden Practices

The following are prohibited.

❌ Bloc importing another Bloc

❌ Repository importing another Repository

❌ Widgets importing API

❌ Widgets importing Dio

❌ Widgets performing JSON parsing

❌ Shared widgets containing business logic

❌ Feature directly reading Supabase

❌ Prediction calculated inside Flutter

❌ History modifying predictions

❌ Dashboard containing Prediction logic

---

# AI Coding Agent Rules

The coding agent must

- Create one feature at a time.
- Complete the feature before starting another.
- Keep architecture identical across all features.
- Extract reusable widgets.
- Keep feature boundaries strict.
- Respect Bloc architecture.
- Respect Repository architecture.

The coding agent must never

- Collapse folders.
- Merge unrelated features.
- Skip states.
- Skip loading indicators.
- Skip error handling.

---

# Definition of Done

A feature is considered complete only when

- [ ] Feature folder exists
- [ ] Bloc implemented
- [ ] Repository implemented
- [ ] API implemented
- [ ] Models implemented
- [ ] Views implemented
- [ ] Widgets extracted
- [ ] States implemented
- [ ] Events implemented
- [ ] Loading state implemented
- [ ] Error state implemented
- [ ] Empty state implemented
- [ ] Theme applied
- [ ] Responsive layout verified
- [ ] No analyzer warnings

Features that do not satisfy every requirement should not be considered complete.

---

# Next Part

Part 3 defines

- API Engineering Standards
- Repository Engineering Rules
- Dio Standards
- State Management Standards
- DTO Rules
- Error Handling Standards
- Image Upload Standards
- Retry Policies
- AI Agent Implementation Rules

# 04 - Flutter Engineering Specification

> **Project:** AI Clinical Decision Support System (AI-CDSS)
>
> **Version:** 1.0
>
> **Document:** Flutter Engineering Specification
>
> **Part:** 3
>
> **Status:** API Integration & State Management Standards
>
> **Audience:** Human Developers & AI Coding Agents

---

# Purpose

This document defines the engineering standards governing:

- API Communication
- Repository Pattern
- State Management
- Authentication Flow
- Image Upload
- Error Handling
- Loading States
- Network Architecture

Every network request inside the application must comply with these standards.

---

# Communication Architecture

Flutter communicates with the backend using the following flow.

```
Widget

↓

Bloc

↓

Repository

↓

API Client

↓

Dio

↓

FastAPI

↓

Repository

↓

Service

↓

Inference Manager

↓

AI
```

No layer may be skipped.

---

# RULE-032

## Presentation Layer Never Performs Networking

Priority

CRITICAL

Widgets must never perform

- HTTP Requests
- API Calls
- Dio Requests

Correct

```
Widget

↓

Bloc
```

Incorrect

```
Widget

↓

Dio
```

---

# RULE-033

## Bloc Owns Application State

Priority

CRITICAL

Bloc is responsible for

- Events
- State
- Business Flow

Bloc must never

- Parse JSON
- Use Dio
- Upload Files

Correct

```
Bloc

↓

Repository
```

---

# RULE-034

## Repository Owns Data Source

Priority

CRITICAL

Repository decides where data comes from.

Current

```
Repository

↓

FastAPI
```

Future

```
Repository

↓

Local Cache

↓

FastAPI
```

Widgets should never know.

---

# RULE-035

## API Layer Owns Dio

Priority

CRITICAL

Only API classes may import

```
dio.dart
```

Forbidden

Bloc

↓

Dio

Repository

↓

Dio

Allowed

API

↓

Dio

---

# API Client

Every API call should originate from one API Client.

```
PredictionApi

HistoryApi

AuthenticationApi

ProfileApi
```

Every feature owns one API class.

---

# RULE-036

## One API Per Feature

Priority

HIGH

Every feature should expose exactly one API class.

Example

```
PredictionApi

HistoryApi

AuthenticationApi
```

No shared mega API.

---

# Dio Configuration

The application uses one Dio instance.

Responsibilities

- Base URL
- Timeout
- Authentication Header
- Logging
- Retry Policy

No feature configures Dio independently.

---

# RULE-037

## One Dio Instance

Priority

CRITICAL

Only one Dio instance should exist.

Created during bootstrap.

Injected everywhere.

Never instantiate Dio inside features.

---

# Authentication Flow

Authentication uses Supabase.

Workflow

```
Login Screen

↓

Authentication Bloc

↓

Authentication Repository

↓

Authentication API

↓

Supabase Auth

↓

Session

↓

Dashboard
```

The UI never talks directly to Supabase.

---

# Authentication Token

The Authentication Repository owns

- Access Token
- Refresh Token
- Session

Other features request authentication through the repository.

---

# RULE-038

## Token Ownership

Priority

CRITICAL

Only AuthenticationRepository owns authentication state.

PredictionRepository

↓

Never reads tokens directly.

HistoryRepository

↓

Never reads tokens directly.

---

# Prediction Flow

```
Prediction Page

↓

Prediction Bloc

↓

Prediction Repository

↓

Prediction API

↓

Upload Endpoint

↓

Prediction Endpoint

↓

Prediction Response

↓

Bloc

↓

UI
```

No intermediate layer may be skipped.

---

# Image Upload

Uploading images is independent from prediction.

Workflow

```
Select Image

↓

Validation

↓

Upload

↓

Receive Upload ID

↓

Predict

↓

Receive Prediction
```

Prediction should never upload files internally.

---

# RULE-039

## Image Validation

Priority

HIGH

Validate

- File Exists
- File Type
- Maximum Size

Reject invalid images before network requests.

---

# RULE-040

## Upload Progress

Priority

MEDIUM

Large uploads should expose progress.

Example

```
0%

↓

25%

↓

60%

↓

100%
```

The UI should reflect upload progress.

---

# History Flow

```
History Page

↓

History Bloc

↓

History Repository

↓

History API

↓

Backend

↓

History Response
```

History should never cache stale prediction data without explicit strategy.

---

# RULE-041

## Immutable State

Priority

CRITICAL

Bloc states must be immutable.

Never modify existing state.

Always emit new state.

---

# RULE-042

## Event Naming

Priority

HIGH

Events describe

"What happened"

Correct

```
ImageSelected

PredictionRequested

HistoryLoaded
```

Incorrect

```
DoPrediction

LoadHistoryNow
```

---

# RULE-043

## State Naming

Priority

HIGH

States describe

"What the application currently is"

Examples

```
PredictionInitial

PredictionLoading

PredictionSuccess

PredictionFailure
```

---

# RULE-044

## Repository Return Types

Priority

HIGH

Repositories return domain models.

Never return

```
Response

Map

JSON
```

Correct

```
PredictionModel
```

---

# DTO Rules

Every API response should have its own DTO.

Example

```
PredictionResponseDto

HistoryDto

AuthenticationDto
```

DTOs remain inside the API layer.

---

# RULE-045

## Domain Models

Priority

HIGH

Bloc should never receive DTOs.

Convert

```
DTO

↓

Domain Model

↓

Bloc
```

---

# Error Handling

Every request must support

- Network Error
- Timeout
- Unauthorized
- Server Error
- Unknown Error

Never expose Dio exceptions directly.

---

# RULE-046

## Error Mapping

Priority

CRITICAL

Every exception must be mapped into user-friendly errors.

Example

Instead of

```
SocketException
```

Return

```
No internet connection.
```

---

# Loading Rules

Every asynchronous action requires loading state.

Examples

Prediction

History

Login

Profile

Uploading

Never freeze the UI.

---

# RULE-047

## Loading Indicators

Priority

HIGH

Every API request should display

- Loading Indicator

or

- Skeleton UI

---

# Retry Policy

Transient failures should be retryable.

Examples

Timeout

↓

Retry

Server Busy

↓

Retry

Invalid Credentials

↓

Do Not Retry

---

# RULE-048

## Retry Strategy

Priority

MEDIUM

Retry only

- Timeout
- Temporary Network Failure

Never retry

Authentication Failure

Validation Failure

---

# API Timeouts

Recommended

Connection

10 seconds

Receive

30 seconds

Configurable

Never hardcode.

---

# RULE-049

## Logging

Priority

HIGH

Log

- Endpoint
- Method
- Status
- Duration

Do not log

- Passwords
- Tokens
- Personal Information

---

# Offline Behaviour

Version 1

Requires Internet.

If offline

Display

```
No Internet Connection
```

Future

Repository can support local cache.

---

# AI Coding Agent Rules

The coding agent must

- Respect Repository Pattern
- Respect API Layer
- Respect Bloc Pattern
- Generate immutable models
- Handle every error
- Handle loading
- Handle retry

The coding agent must never

- Import Dio into Bloc
- Parse JSON in Widgets
- Return DTOs to Widgets
- Skip loading states
- Skip error mapping

---

# Forbidden Practices

❌ Widget calling API

❌ Bloc using Dio

❌ Repository returning JSON

❌ Duplicate Dio instances

❌ Hardcoded Base URL

❌ Hardcoded Tokens

❌ Mutable Bloc State

❌ Missing Loading State

❌ Missing Error State

❌ Missing Empty State

---

# Definition of Done

Part 3 is complete when

- [ ] Dio configured
- [ ] API clients created
- [ ] Repositories implemented
- [ ] Bloc communicates only with Repository
- [ ] DTO mapping implemented
- [ ] Domain models implemented
- [ ] Error mapping implemented
- [ ] Loading states implemented
- [ ] Retry policy implemented
- [ ] Logging implemented
- [ ] Authentication flow completed
- [ ] Image upload workflow completed
- [ ] Prediction workflow completed
- [ ] History workflow completed

No feature should communicate directly with the backend.

Every request must follow the architecture defined in this document.

---

# Next Part

Part 4 defines:

- Performance Engineering
- Responsive Design
- Accessibility
- Animations
- Widget Optimization
- Code Quality Standards
- Production Readiness
- Release Checklist
- Final AI Coding Agent Rules

# 04 - Flutter Engineering Specification

> **Project:** AI Clinical Decision Support System (AI-CDSS)
>
> **Version:** 1.0
>
> **Document:** Flutter Engineering Specification
>
> **Part:** 4
>
> **Status:** Production Readiness & Engineering Standards
>
> **Audience:** Human Developers & AI Coding Agents

---

# Purpose

This document defines the production engineering standards for the Flutter application.

These rules ensure that every feature developed throughout the project maintains a consistent level of quality, scalability, performance, and maintainability.

This document should be considered the final quality checklist before deployment.

---

# Engineering Philosophy

Writing working code is not enough.

Every implementation should satisfy four objectives.

- Functional
- Maintainable
- Performant
- Scalable

The application should remain easy to extend even after Version 1 is completed.

---

# RULE-050

## Feature Completeness

Priority

CRITICAL

A feature is not complete until every required component exists.

Required

- Bloc
- Repository
- API
- Models
- Views
- Widgets
- Tests

A screen alone is never considered a completed feature.

---

# RULE-051

## File Responsibility

Priority

CRITICAL

Every file should have exactly one responsibility.

Correct

```
prediction_repository.dart

↓

Handles Prediction Repository
```

Incorrect

```
prediction_repository.dart

↓

Repository

↓

Networking

↓

Parsing

↓

UI Helpers
```

---

# RULE-052

## Widget Size

Priority

HIGH

Widgets should remain small.

Recommended

Maximum

```
150 Lines
```

Pages

Maximum

```
300 Lines
```

Extract reusable widgets whenever necessary.

---

# RULE-053

## Build Method

Priority

HIGH

The build() method should only build UI.

Never

- Perform calculations
- Call repositories
- Create controllers repeatedly

The build method must remain lightweight.

---

# RULE-054

## Const Constructors

Priority

MEDIUM

Use const constructors whenever possible.

Benefits

- Faster rebuilds
- Better performance
- Cleaner widget tree

---

# RULE-055

## Reusable Widgets

Priority

HIGH

If the same UI appears more than once,

Extract it.

Correct

```
PredictionCardWidget
```

Incorrect

Duplicate Card UI in multiple pages.

---

# RULE-056

## Theme Consistency

Priority

CRITICAL

Never hardcode

- Colors
- Font sizes
- Border Radius
- Elevation
- Shadows

Everything should originate from the Theme.

Correct

```
Theme.of(context)
```

Incorrect

```
Color(0xFF0066FF)
```

inside widgets.

---

# RULE-057

## Responsive Design

Priority

HIGH

Every page must support

- Mobile
- Tablet
- Desktop (Optional)

Avoid fixed widths.

Prefer flexible layouts.

Use

- Expanded
- Flexible
- LayoutBuilder

---

# RULE-058

## Accessibility

Priority

MEDIUM

Every interactive component should provide

- Semantic labels
- Proper touch targets
- Readable contrast
- Keyboard accessibility (Desktop)

Accessibility should never be added as an afterthought.

---

# RULE-059

## Animations

Priority

LOW

Animations should improve user experience.

Allowed

- Fade
- Slide
- Scale

Avoid excessive animation.

Medical applications should prioritize clarity over visual effects.

---

# RULE-060

## Loading Experience

Priority

HIGH

Every asynchronous operation must display a loading state.

Preferred

- Skeleton UI
- Progress Indicator
- Upload Progress

Never leave the interface frozen.

---

# RULE-061

## Empty States

Priority

HIGH

Every collection screen should display meaningful empty states.

Example

History

```
No Predictions Available

Upload your first Chest X-ray.
```

Avoid blank pages.

---

# RULE-062

## Error States

Priority

CRITICAL

Every feature must gracefully handle

- Network Failure
- Timeout
- Unauthorized
- Server Error
- Unknown Error

Never expose raw exception messages.

---

# RULE-063

## Performance

Priority

HIGH

Avoid unnecessary rebuilds.

Recommended

- BlocSelector
- BlocBuilder
- const Widgets

Only rebuild affected widgets.

---

# RULE-064

## Image Handling

Priority

HIGH

Images should

- Be compressed before upload
- Display placeholders
- Display loading indicators
- Cache when appropriate

Never block the UI while loading images.

---

# RULE-065

## Navigation

Priority

HIGH

Navigation should always be declarative.

Use

```
GoRouter
```

Never manually maintain navigation stacks.

---

# RULE-066

## Environment Configuration

Priority

CRITICAL

Never hardcode

- Base URLs
- API Keys
- Environment Variables

Use

```
.env
```

or

```
Flutter Environment Configuration
```

---

# RULE-067

## Logging

Priority

MEDIUM

Log

- Navigation
- API Requests
- Prediction Workflow

Never log

- Passwords
- Tokens
- Personal Medical Information

---

# RULE-068

## Error Reporting

Priority

MEDIUM

Every unexpected error should be

- Logged
- Recoverable where possible

The application should fail gracefully.

---

# RULE-069

## Testing

Priority

HIGH

Every feature should include

- Bloc Tests
- Repository Tests
- Widget Tests

Critical workflows should include integration tests.

---

# RULE-070

## Code Generation

Priority

MEDIUM

Use code generation only where it provides clear value.

Examples

- Freezed
- JSON Serialization

Avoid unnecessary generated code.

---

# RULE-071

## Localization

Priority

LOW

Prepare the application for localization.

Store user-facing strings separately.

Avoid hardcoded text inside widgets.

---

# RULE-072

## Security

Priority

CRITICAL

Never store

- Passwords
- Access Tokens
- Secrets

inside

- Widgets
- Bloc
- Local Storage (unless encrypted)

Sensitive information should be managed securely.

---

# RULE-073

## Medical Disclaimer

Priority

CRITICAL

Every prediction screen must display a disclaimer.

Example

```
This prediction is generated by an AI model.

It should not replace professional medical advice.

Please consult a qualified healthcare professional for diagnosis and treatment.
```

This disclaimer must always be visible alongside prediction results.

---

# RULE-074

## Code Quality

Priority

HIGH

The project should compile with

```
flutter analyze
```

without warnings or errors.

No TODO comments should remain before release.

---

# RULE-075

## Documentation

Priority

HIGH

Every public class should include documentation.

Complex business logic should explain

- Why
- Not just What

Code should be self-explanatory whenever possible.

---

# Flutter Coding Agent Rules

The coding agent must

✓ Follow VGV Architecture

✓ Respect Feature Boundaries

✓ Respect Bloc Pattern

✓ Respect Repository Pattern

✓ Build Responsive UI

✓ Extract Reusable Widgets

✓ Use Theme

✓ Use Dependency Injection

✓ Generate Clean Code

✓ Follow Naming Standards

The coding agent must never

✗ Generate God Classes

✗ Skip Architecture

✗ Place Business Logic in Widgets

✗ Hardcode Values

✗ Duplicate Widgets

✗ Skip Loading States

✗ Skip Error Handling

✗ Bypass Repositories

✗ Ignore Theme

---

# Forbidden Practices

The following are prohibited.

❌ Widgets larger than 300 lines

❌ Business logic inside UI

❌ Bloc importing Dio

❌ Repository importing Widgets

❌ Duplicate repositories

❌ Duplicate API clients

❌ Hardcoded colors

❌ Hardcoded routes

❌ Direct API calls from Widgets

❌ Calling FastAPI without Repository

❌ Ignoring loading states

❌ Ignoring error states

❌ Ignoring empty states

❌ Mutable Bloc states

---

# Definition of Done

The Flutter application is considered production-ready when

- [ ] Architecture follows every engineering rule
- [ ] Every feature is complete
- [ ] No analyzer warnings
- [ ] Responsive layouts verified
- [ ] Theme applied consistently
- [ ] Loading states implemented
- [ ] Error handling implemented
- [ ] Empty states implemented
- [ ] API integration completed
- [ ] Bloc architecture verified
- [ ] Repository architecture verified
- [ ] Widget extraction completed
- [ ] Code reviewed
- [ ] Documentation updated
- [ ] Medical disclaimer displayed
- [ ] End-to-end prediction workflow verified

Only after satisfying every item should the application be considered complete.

---

# Flutter Milestone

The Flutter application is complete when

- Authentication works.
- Dashboard is functional.
- Users can upload Chest X-rays.
- Predictions are displayed correctly.
- Prediction history is available.
- Profile and Settings are functional.
- The UI is responsive.
- The application integrates successfully with the backend.
- AI predictions are displayed with confidence scores and medical disclaimer.

At this point, Version 1 of the AI Clinical Decision Support System is considered feature-complete.

---

# Next Phase

## 05 - End-to-End System Integration

The next phase focuses on:

- Flutter ↔ Backend Integration
- Backend ↔ AI Integration
- Prediction Workflow Verification
- Supabase Integration
- End-to-End Testing
- Performance Validation
- System Acceptance Testing