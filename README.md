## Features

- **POST /event**: Accepts and stores events (JSON), hashed and timestamped.
- **GET /events**: Retrieves stored events, sorted by timestamp.
- **GET /health**: Health check endpoint.
- **JWT Authentication**: All event endpoints require a valid JWT.
- **Tamper Detection**: Each event is hashed and chained to the previous event.
- **Proof-of-Integrity**: Verify the event chain for tampering.
- **Frontend**: Register, authenticate, and view events in a simple web UI.

Cloud Deployment

- [Live Demo @ http://18.234.243.50/app](http://18.234.243.50/app)

---

## Implementation Details

### Backend

- **Framework**: FastAPI (Python)
- **Database**: PostgreSQL (via Docker)
- **Event Storage**: Each event is stored with a SHA-256 hash of its data and a reference to the previous event's hash, forming a tamper-evident chain.
- **Authentication**: JWT tokens are issued per application. Each token is signed with a unique API key (HMAC/HS256).
- **Endpoints**:
  - `POST /api/app/register`: Register a new application, receive a JWT.
  - `POST /api/event`: Log an event (JWT required).
  - `GET /api/events`: Retrieve all events for the authenticated app.
  - `GET /api/events/proof`: Verify the integrity of the event chain.
  - `GET /health`: Health check.
- **Database Initialization**: On startup, tables for `apps` and `events` are created if they do not exist.

### Frontend

- **Location**: `frontend/`
- **Stack**: HTML, Bulma CSS, Vanilla JS
- **Features**:
  - Register a new application and receive a JWT.
  - Login with JWT to view events.
  - Simple, modern UI for demo and testing.

---

## Application Flow

1. **Register Application**: A developer registers their application via the API (e.g., using cURL) or the provided frontend UI. This creates a new app record in the backend and generates a unique API key.
2. **Receive JWT**: Upon registration, the backend issues a JWT (signed with the app's API key) to the user. This JWT authenticates all future requests for that app.
3. **Log Events**: The developer (or their app) sends events to the backend using the JWT for authentication. Each event is securely stored and chained for tamper detection.
4. **Login to Frontend**: Developers can paste their JWT into the frontend UI to 'log in' and view the events associated with their app.
5. **View & Verify Events**: The frontend displays the event log and allows users to verify the integrity of the event chain for their app.

---

## Getting Started

### Prerequisites

- Docker & Docker Compose

### Quick Start

1. **Clone the repository**
   ```sh
   git clone <your-repo-url>
   cd <repo-directory>
   ```

2. **Start the services**
   ```sh
   docker-compose up --build
   ```
   - This will start both the backend (FastAPI) and a PostgreSQL database.
   - The backend will be available at [http://localhost:8001](http://localhost:8001)
   - The frontend will be served at [http://localhost:8001/app](http://localhost:8001/app)

---

## API Usage

### 1. Register a New Application

**Request**
```http
POST /api/app/register
Content-Type: application/json

{
  "name": "my-app"
}
```

**Response**
```json
{
  "message": "Application registered successfully.",
  "app_name": "my-app",
  "token": "<JWT_TOKEN>"
}
```

### 2. Log an Event

**Request**
```http
POST /api/event
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json

{
  "type": "user_login",
  "data": {
    "user_id": 123,
    "ip": "1.2.3.4"
  }
}
```

**Response**
```json
{
  "status": "event logged successfully",
  "hash": "<event_hash>"
}
```

### 3. Retrieve Events

**Request**
```http
GET /api/events
Authorization: Bearer <JWT_TOKEN>
```

**Response**
```json
[
  {
    "id": 1,
    "type": "user_login",
    "event_data": { ... },
    "timestamp": "...",
    "event_hash": "...",
    "prev_event_hash": "..."
  },
  ...
]
```

### 4. Proof of Integrity

**Request**
```http
GET /api/events/proof
Authorization: Bearer <JWT_TOKEN>
```

**Response**
If there is only zero or one event for the app:
```json
{
  "status": "valid",
  "message": "Zero or one event; chain is trivially valid."
}
```
or, if tampering is detected:
```json
{
  "status": "invalid",
  "break_index": 3,
  "event_id": 7,
  "message": "Chain broken at this event."
}
```
or, if there are multiple events, and no tampering detected:
```json
{
  "status": "valid",
  "message": "Event chain is valid and unbroken."
}
```
### 5. Health Check

**Request**
```http
GET /health
```

**Response**
```json
{ "status": "ok" }
```

---

## Frontend Usage

1. Visit [http://localhost:8001/app](http://localhost:8001/app)
2. Register a new application to get a JWT.
3. Use the JWT to log in and view events for your app.

---

## Development

- **Backend code**: `main.py`, `src/`
- **Frontend code**: `frontend/`
- **Database schema**: See `src/database/scripts/db_init.py`
- **Dependencies**: See `requirements.txt`

---

## Security Notes

- JWTs are signed per-app with a unique API key (HMAC/HS256).
- Event hashes are chained to detect tampering.
- All event endpoints require authentication.

---

## Example Docker Compose Setup

- **PostgreSQL**: Exposed on port 5434 (internal 5432)
- **Backend**: Exposed on port 8001

---

## Gaps/Future Improvements

- **Full User Management**: Introducing a `users` table and authentication to allow users to own and manage multiple applications under a single account.
- **Enhanced Event Querying**: Implementing server-side pagination and add filtering capabilities to the API and frontend (e.g., by event type or a text search).
- **Hardened Security**: Adding features like API key regeneration, rate limiting on sensitive endpoints, and comprehensive unit/integration tests.
- **Configuration Management**: Moving all secrets and environment-specific settings into a `.env` file for better security.