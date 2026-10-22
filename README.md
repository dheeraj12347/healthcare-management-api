# Healthcare Management API

A RESTful healthcare backend built using Django, Django REST Framework (DRF), PostgreSQL, and JWT authentication.

## Features

- User registration and JWT login.
- Secure, authenticated API endpoints.
- Patient creation, listing, retrieval, updating, and deletion.
- Doctor creation, listing, retrieval, updating, and deletion.
- Assign doctors to patients and manage those assignments.
- Patient records restricted to the user who created them.
- Input validation and appropriate API error responses.

## Technology Stack

- Python
- Django
- Django REST Framework
- PostgreSQL
- Simple JWT
- python-dotenv

## Project Setup

### 1. Open the project directory

Open PowerShell in the project root directory.

### 2. Create and activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root using `.env.example` as a template. Configure the Django secret key, debug setting, allowed hosts, and PostgreSQL credentials.

**Never commit or share your actual `.env` file.**

### 5. Create the PostgreSQL database

Create the PostgreSQL database and database user specified by your environment variables, and grant the user the required permissions.

### 6. Apply migrations

```powershell
python manage.py migrate
```

### 7. Start the development server

```powershell
python manage.py runserver
```

The development server runs at `http://127.0.0.1:8000/`.

## API Endpoints

All API routes begin with `/api/`.

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register/` | Register a user |
| POST | `/api/auth/login/` | Obtain JWT access and refresh tokens |
| POST | `/api/auth/refresh/` | Refresh an access token |
| GET, POST | `/api/patients/` | List your patients or create a patient |
| GET, PUT, PATCH, DELETE | `/api/patients/<id>/` | Retrieve, update, or delete your patient |
| GET, POST | `/api/doctors/` | List doctors or create a doctor |
| GET, PUT, PATCH, DELETE | `/api/doctors/<id>/` | Retrieve, update, or delete a doctor |
| GET, POST | `/api/mappings/` | List patient-doctor mappings or create one |
| GET | `/api/mappings/<patient_id>/` | Retrieve mappings for a patient |
| DELETE | `/api/mappings/<mapping_id>/` | Delete a patient-doctor mapping |

Authenticated endpoints require the following HTTP header:

```http
Authorization: Bearer <access_token>
```

Use the access token returned by the login endpoint.

## Running Tests

Run the automated test suite:

```powershell
python manage.py test patients_api
```

## Security Notes

- Keep `.env` and its credentials private.
- Use a strong, unique Django secret key.
- Set `DEBUG=False` and configure appropriate `ALLOWED_HOSTS` for production.
- This project is configured for local development unless separately deployed and hardened.
