# Test Project

This project is a Streamlit-based data dashboard for Oracle databases, featuring interactive tables with filtering, pagination, and column auto-fit using AgGrid.

## Project Structure

- **app.py**: Main entry point for the Streamlit application.
- **pagin.py**: Standalone Streamlit page for debugging and testing pagination and table features.
- **pages/**: Contains additional Streamlit pages:
  - `home.py`, `errors.py`, `logs.py`: Main dashboard pages for different data views.
  - `home_org.py`, `errors_org.py`, `logs_original.py`: Alternative or legacy versions of the main pages.
- **db/**: Database logic and models.
  - `models.py`: SQLAlchemy ORM models.
  - `generic_utils.py`: Database utility functions (queries, pagination, etc).
- **utils/**: Helper utilities for authentication and other shared logic.
- **images/**: Contains logo and image assets for the UI.
- **requirements.txt**: Python dependencies for the project.
- **README.md**: Project documentation and setup instructions.

## Features
- Streamlit UI for data exploration
- Oracle database connection (via oracledb and SQLAlchemy)
- Interactive tables with filtering, sorting, and column auto-fit (st-aggrid)
- Date formatting (YYYY-MM-DD)
- Pagination and dynamic loading

## Requirements
See `requirements.txt` for all dependencies. Main libraries:
- streamlit >= 1.33.0
- pandas >= 2.2.2
- sqlalchemy >= 2.0.30
- st-aggrid >= 0.3.4
- oracledb >= 2.2.0

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up your Oracle database credentials in the app as prompted.
3. Run the app:
   ```bash
   streamlit run app.py
   ```

## Usage
- Use the sidebar and filters to select data.
- Tables support sorting, filtering, and column resizing.
- Click "Pokaż więcej" to load more data if available.

## Notes
- Make sure you have network access to your Oracle database.
- For best experience, use a modern browser and a wide layout.
