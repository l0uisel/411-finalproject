# Movie Tracking App
### Overview

- **What the application does at a high level**

  Our Movie Tracker App is a movie watchlist to help users browse and manage their movie collections. The key features include:
  - Adding and removing movies from a watchlist.
  - Clearing the watchlist entirely.
  - Re-arranging the order of movies in the watchlist.
  - Viewing (display) all movies in the watchlist.
  - Retrieving overall watchlist statistics, such as the total number of movies and their combined runtime.
  - Checking if the watchlist is empty.
  - Validating movie IDs to ensure they are correct.
  - Ensuring the watchlist order/numbering corresponds somewhere in the watchlist.

  The application interacts with an external API (from oMDb API) to fetch movie data and provides functionality for user authentication and movie management.

  Formatting for the movie would be extracting its IMDb ID, giving it a watchlist number, and assigning the director, genre, year, and runtime.

  To join our app, users can create an account. We also check for username uniqueness, if the account already exists and allow users to update their password. Users can log in when they have an existing account with the right password.

#### Health Check Routes
**Route: /api/health**

  Request Type: GET
  
  Purpose: Verify if the service is running.
  
  Response Format: JSON
  
  Example Response:
  {
  
    "status": "healthy"
    
  }
  
**Route: /api/db-check**

Request Type: GET

Purpose: Verify the database connection and ensure the required tables exist.

Response Format: JSON

Success Response Example:
{

  "database_status": "healthy"
  
}

Error Response Example:
{

  "error": "movies table does not exist"
  
}

**Route: /api/create-movie**

Request Type: POST

Purpose: Add a new movie to the catalog.

Request Body:

{
  "title": "string"
}

Response Format: JSON

Success Response Example:

{

  "status": "success",
  "movie": "Inception"
  
}

Error Response Example:

{

  "error": "Invalid input, all fields are required with valid values"

}

**Route: /api/clear-catalog**

Request Type: DELETE

Purpose: Clear the entire movie catalog.

Response Format: JSON

Success Response Example:

{

  "status": "success"
  
}
- **A description of each route (example on ed discussion):**
  - **Route Name and Path**
  - **Request Type**
    - GET, POST, PUT, DELETE
  - **Purpose**
  - **Request Format**
    - GET parameters
    - POST / PUT / DELETE body
  - **Response Format**
    - JSON keys and value types
  - **Example**
    - Request in the form of JSON body or cURL command
    - Associated JSON response

## Steps required to run the application:
1. Create an API key for the omdbapi.com: https://www.omdbapi.com/
2. Put it in the .env file like API_KEY=<your api key>
3. Activate the virtual environment using setup_env.sh
4. Run run_docker.sh
5. Now the app is running on the port specified in the .env file. The default port is 800.
