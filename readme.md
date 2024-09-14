This following  structure clearly outlines each step needed to set up and run the project.

## Installation and Setup

1. **Creating a Virtual Environment:**
   ```bash
   python -m venv venv
   ```

2. **Activating the Virtual Environment:**
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Installing Required Packages:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Running Database Migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Creating a Superuser:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Running the Server:**
   ```bash
   python manage.py runserver
   ```

