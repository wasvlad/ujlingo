## Recommended steps to work with this project:

1. **Clone repository**

2. **Create `.env` file in root directory. Recommended content:**
    ```env
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=password
    POSTGRES_DB=database
    ENVIRONMENT="local"
    FRONTEND_URL="http://localhost:3001"
    BACKEND_URL="http://backend:3000"
    TRANSLATOR_URL="http://translator:3002"
    ```

3. **Create `.gitignore` file in root directory. Recommended content:**
    ```gitignore
    .env
    .gitignore
    .venv
    .idea
    translator/data
    ```

4. **Run `docker-compose up --build`**
    - When using an IDE, you should sometimes include `docker-compose.override.yml` file manually to run the project in the IDE.

5. **Open `http://localhost:3001` in your browser**

**Note:**
- File `.env` is not recommended to be changed or pushed to the repository.
- File `.gitignore` is not recommended to be pushed. It should be changed to your specific needs. Add any file or directory you need to ignore (big data files, IDE files, etc.)

**Backend documentation is accessible at (if env is local):**
- `http://localhost:3000/docs`
- `http://localhost:3000/redoc`
