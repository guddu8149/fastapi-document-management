# FastAPI Document Management System

This is a document management system built using FastAPI with JWT authentication.

## Features
- User authentication (Admin, Editor, Viewer)
- JWT-based authorization
- Document storage and retrieval
- Role-based access control

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/fastapi-document-management.git
   cd fastapi-document-management
   ```
2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

```
3. Install dependencies:
 ```bash
pip install fastapi[all] python-jose pydantic
```
4. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

Detailed Description for GitHub Repository:
This repository contains a FastAPI-powered document management system that allows users to upload, retrieve, and delete documents with role-based access control (RBAC).

Key Features:
```md
✅ User Authentication: Uses OAuth2 and JWT for secure login.
✅ Role-Based Access Control: Users have different roles (Admin, Editor, Viewer) with different permissions.
✅ Secure Document Management: Supports adding, viewing, and deleting documents with access restrictions.
✅ CSV-Based Storage: Stores metadata in a CSV file for simplicity.
✅ API-First Design: RESTful API endpoints for seamless integration.

Technology Stack:
FastAPI (Backend Framework)
OAuth2 & JWT (Authentication & Authorization)
Pydantic (Data Validation)
CSV File Handling (For Storing Document Metadata)
API Endpoints:
1️⃣ POST /auth/login → Authenticate users and generate a JWT token.
2️⃣ POST /documents → Add a new document (Admin/Editor only).
3️⃣ GET /documents → Retrieve all documents (Authenticated users only).
4️⃣ DELETE /documents/{document_id} → Delete a document (Admin/Editor only).
   
