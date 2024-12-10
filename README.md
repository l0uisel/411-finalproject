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

  The application interacts with an external API (from IMDb API) to fetch movie data and provides functionality for user authentication and movie management.

  Formatting for the movie would be extracting its IMDb ID, giving it a watchlist number, and assigning the director, genre, year, and runtime.

  To join our app, users can create an account. We also check for username uniqueness, if the account already exists and allow users to update their password.
  
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
