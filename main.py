from fastapi import FastAPI, HTTPException, Depends, Path, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from pydantic import BaseModel
from datetime import datetime, timedelta
import csv
import os
from typing import List, Optional

# Configuration
DOCUMENT_STORAGE_PATH = "documents/"  
DOCUMENT_DB = "documents.csv"  
SECRET_KEY = "your-secret-key"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Create storage directory if it doesn't exist
if not os.path.exists(DOCUMENT_STORAGE_PATH):
    os.makedirs(DOCUMENT_STORAGE_PATH)

# Initialize FastAPI app
app = FastAPI()

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# User model
class User(BaseModel):
    email: str
    role: str

# Document model
class Document(BaseModel):
    document_id: str
    title: str
    tags: List[str]
    uploaded_by: str
    permissions: List[str]

# Token model
class Token(BaseModel):
    access_token: str
    token_type: str

# Mock user database
USERS_DB = {
    "admin@example.com": {"email": "admin@example.com", "password": "adminpassword", "role": "admin"},
    "editor@example.com": {"email": "editor@example.com", "password": "editorpassword", "role": "editor"},
    "viewer@example.com": {"email": "viewer@example.com", "password": "viewerpassword", "role": "viewer"}
}

# Helper function to create JWT token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Helper function to decode JWT token
def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# Dependency to get the current user
def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_token(token)
    user_email = payload.get("sub")
    if user_email not in USERS_DB:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return User(email=user_email, role=USERS_DB[user_email]["role"])

# Login endpoint
@app.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = USERS_DB.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    return {"access_token": create_access_token({"sub": user["email"]}), "token_type": "bearer"}

# Add a new document
@app.post("/documents")
def add_document(doc: Document, current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "editor"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin or editor can upload documents")

    # Check if the document ID already exists
    if find_document_in_db(doc.document_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Document ID already exists")

    # Save document metadata to CSV
    with open(DOCUMENT_DB, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow([doc.document_id, doc.title, ",".join(doc.tags), doc.uploaded_by, ",".join(doc.permissions)])

    return {"message": "Document added successfully"}

# Get all documents
@app.get("/documents", response_model=List[Document])
def get_documents(current_user: User = Depends(get_current_user)):
    with open(DOCUMENT_DB, mode="r") as file:
        reader = csv.DictReader(file)
        return [Document(
            document_id=row["document_id"],
            title=row["title"],
            tags=row["tags"].split(","),
            uploaded_by=row["uploaded_by"],
            permissions=row["permissions"].split(",")
        ) for row in reader]

# Delete a document
@app.delete("/documents/{document_id}")
def delete_document(document_id: str, current_user: User = Depends(get_current_user)):
    if current_user.role not in ["admin", "editor"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this document")

    document = find_document_in_db(document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")

    if document["uploaded_by"] != current_user.email and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have permission to delete this document")

    file_path = os.path.join(DOCUMENT_STORAGE_PATH, document_id)
    if os.path.exists(file_path):
        os.remove(file_path)

    delete_document_from_db(document_id)
    return {"message": "Document deleted successfully"}

# Helper functions
def find_document_in_db(document_id: str):
    with open(DOCUMENT_DB, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["document_id"] == document_id:
                return row
    return None

def delete_document_from_db(document_id: str):
    rows = []
    with open(DOCUMENT_DB, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row["document_id"] != document_id:
                rows.append(row)
    with open(DOCUMENT_DB, mode="w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["document_id", "title", "tags", "uploaded_by", "permissions"])
        writer.writeheader()
        writer.writerows(rows)

# Initialize the database
def initialize_db():
    if not os.path.exists(DOCUMENT_DB):
        with open(DOCUMENT_DB, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["document_id", "title", "tags", "uploaded_by", "permissions"])

initialize_db()
