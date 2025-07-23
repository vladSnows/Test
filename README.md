# DMSF Professional App

## Overview
A professional Streamlit application for monitoring and reporting DMSF processing status and errors.

## Features
- Secure authentication (username/password from .env)
- Modular code structure (components, pages, core, utils)
- Centralized configuration and database logic
- Advanced UI with header, footer, and responsive layout
- Paginated data views
- Oracle database integration
- Error logging with Python's logging module
- Caching for expensive operations (st.cache_data, st.cache_resource)

## Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

### Main dependencies
- streamlit
- cx_Oracle
- pandas
- logging

## Project Structure

- `app.py`: Main Streamlit app entry point
- `pages/`: Contains Streamlit pages (home.py, errors.py)
- `utils/`: Utility modules (db.py for database, session.py for session management)
- `components/`: UI components (footer, header, sidebar)
- `core/`: Configuration and Oracle connector

```
app.py                # Main entry point
core/                 # Configuration and DB connector
  config.py           # App and DB config (uses .env)
  OraConnector.py     # Oracle DB connector (legacy)
components/           # Reusable UI components (header, footer, sidebar)
pages/                # Streamlit pages (home, errors, ...)
utils/                # Helper modules (db, session)
requirements.txt      # Python dependencies
.env                  # Secrets and credentials
README.md             # Documentation
```

## Setup
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with your credentials (see example below)
4. Run the app:
   ```bash
   streamlit run app.py
   ```

### Example .env file
```
DB_HOST=localhost
DB_USER=user
DB_PASS=password
ADMIN_USER=admin
ADMIN_PASS=admin123
APP_USER=user
APP_PASS=user123
```

## Usage
- Log in with credentials from `.env`
- Navigate using the sidebar
- View processing status and errors

## Adding Pages/Components
- Add new pages to `pages/` and link in `app.py`
- Create reusable UI in `components/`

## Contribution
- Follow modular structure
- Add docstrings and comments
- Use logging for errors
- Use caching for expensive operations
- Submit pull requests for new features

## License
MIT

## Notes
- Database schema is now parameterized in all queries.
- Session management is centralized in `utils/session.py`.
- All database select logic is in `utils/db.py`.
