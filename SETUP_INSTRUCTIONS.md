# How to Run the Application

Based on the documentation, here are the steps needed to run the application properly:

1. Environment Setup
   - Set up required environment variables:
     - JWT_SECRET_KEY for authentication
     - DNS_TIMEOUT and other performance settings
   - Copy the environment variables from ENV_SETUP.md to a new `.env` file

2. Installation
   ```bash
   # Clone the repository (if not already done)
   
   # Option 1: Using Docker (Recommended)
   docker-compose up --build

   # Option 2: Local Installation
   pip install -r requirements.txt
   ```

3. Configuration
   - Ensure all environment variables are set correctly
   - The application will use configuration based on the FLASK_ENV setting:
     - development (default)
     - testing
     - production

4. Running the Application
   ```bash
   # If using Docker:
   docker-compose up

   # If running locally:
   python main.py
   ```

5. Verify Installation
   - The application should start up without errors
   - Check the logs for any configuration or startup issues
   - Access the web interface (default port can be found in docker-compose.yml)

6. Development Tools
   - For development, you can use the included code style tools
   - Run tests using the test suite
   ```bash
   pytest
   flake8
   black .
   ```

For more detailed information, refer to:
- docs/getting_started.md
- docs/ENV_SETUP.md
- docker-compose.yml