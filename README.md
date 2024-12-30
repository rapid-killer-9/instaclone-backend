# Instaclone Backend

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/instaclone-backend.git
    cd instaclone-backend
    ```

2. Create and activate a virtual environment:
    ```sh
    python3 -m venv env
    source env/bin/activate
    ```

3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Set up environment variables:
    Create a [.env](http://_vscodecontentref_/2) file in the root directory and add the necessary environment variables.

## Running the Application

### Setting up a .env File
Create a `.env` file in the root directory with your environment variables, for example:
```sh
MONGO_URI=mongodb+srv://<username>:<password>@cluster0.r38qj.mongodb.net/dev?retryWrites=true&w=majority&appName=Cluster0
JWT_SECRET_KEY=SecRet_KeY
JWT_ALGORITHM=HS256
```
To Test application You can use. It will be active for 2 week for public IP 
```sh
MONGO_URI=mongodb+srv://hjha0695:8HCIDgs2CUFHAlJl@cluster0.r38qj.mongodb.net/dev?retryWrites=true&w=majority&appName=Cluster0
```
Test User
```
{
  "username": "Test",
  "email": "Test@gmail.com",
  "password": "Test@1234",
  "full_name": "Test Bot"
}
```

To run the FastAPI application, use the following command:
```sh
uvicorn app.main:app --reload
```

The application will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).

## API Documentation

FastAPI provides interactive API documentation. You can access it at the following URLs once the application is running:

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Project Modules

- **config**: Configuration settings for the application.
- **routes**: API route definitions.
  - `auth_routes.py`: Authentication-related routes.
  - `follow_routes.py`: Routes for following users.
  - `post_routes.py`: Routes for creating and managing posts.
  - `user_routes.py`: Routes for user-related operations.
- **services**: Business logic and service layer.
  - `auth_service.py`: Authentication services.
  - `follow_service.py`: Services for following users.
  - `post_service.py`: Services for managing posts.
  - `user_service.py`: User-related services.
- **utils**: Utility functions and helpers.
  - `auth.py`: Authentication utilities.
  - `db.py`: Database connection and utilities.
  - `validator.py`: Data validation utilities.

## Used Technologies

- **Programming Language**: Python
- **Framework**: FastAPI
- **Database**: MongoDB
- **Authentication**: JSON Web Tokens (JWT)
- **Documentation**: Swagger UI / ReDoc
- **Web Server**: Uvicorn
- **Environment Management**: Python Virtual Environment (venv)

---
Feel free to reach out for contributions or issues related to the project!
