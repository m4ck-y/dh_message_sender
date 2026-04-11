# PulseCore - Multi-channel Messaging Service

PulseCore is a high-performance messaging API designed for the Digital Hospital ecosystem. It provides a transport-agnostic architecture for dispatching notifications across multiple channels, including Email, SMS, and WhatsApp.

## Key Features

- **Provider Pattern Architecture**: Decoupled messaging logic from delivery mechanisms.
- **Multi-channel Support**: Unified interface for OTP verification, user onboarding, and waitlist notifications.
- **Asynchronous Execution**: High-concurrency processing using FastAPI and asynchronous handlers.
- **Centralized Auditing**: Automatic logging of all message events, including delivery status and metadata.
- **Template Management**: Responsive HTML notification support via Jinja2.

## Technical Requirements

- **Python**: 3.13 or higher
- **Dependency Manager**: uv
- **Framework**: FastAPI

## Installation and Configuration

### 1. Repository Setup
Navigate to the component directory and synchronize dependencies:
```bash
cd app_message_sender
uv sync
```

### 2. Environment Configuration
Copy the template environment file and populate it with your provider credentials:
```bash
cp .env.example .env
```
Ensure SMTP, Twilio, or other provider settings are correctly configured in the `.env` file.

### 3. Service Execution
Start the development server:
```bash
uv run uvicorn app.main:app --reload
```
The interactive API documentation is accessible at: `http://localhost:8000/docs`.

## Architecture Overview

PulseCore utilizes a centralized `MessageDispatcher` that routes requests to specific channel providers (e.g., SmtpEmailProvider). Every dispatch operation is intercepted by an internal Audit Service to ensure full traceability without compromising the core business logic.

## Configuration Guides

Detailed configuration for specific providers is available in the documentation directory:
- [Google SMTP Configuration (Spanish)](docs/settings/email_google.md)
- SMS and WhatsApp integration guides are currently under development.

## API Specification

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/health` | GET | Validates service health and configuration status. |
| `/audit/logs` | GET | Returns the most recent message audit entries. |
| `/emails/send-otp` | POST | Dispatches a secure One-Time Password. |
| `/emails/welcome` | POST | Dispatches a standardized user welcome message. |
| `/waitlist/send-confirmation` | POST | Dispatches a waitlist registration confirmation. |

---
*Digital Hospital - PulseCore Component*