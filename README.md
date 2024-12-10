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
- **Steps to run the application:**
    1. Create an API key for the omdbapi.com: https://www.omdbapi.com/
    2. Put it in the `.env` file like `API_KEY=<your api key>`
    3. Activate the virtual environment using `setup_env.sh`
    4. Run `run_docker.sh`
    5. Now the app is running on the port specified in the .env file. The default port is `8000`.


## Routing Documentation (app.py)
### Health Check Routes

**Route: `/api/health`**

  Request Type: `GET`
  
  Purpose: Verify if the service is running.
  
  Response Format: `JSON`
  
  Example Response:

  Code: `200`

  Content:

```json
{
        "status": "healthy"
}
```
  
**Route: `/api/db-check`**

Request Type: `GET`

Purpose: Verify the database connection and ensure the required tables exist.

Response Format: `JSON`

Success Response Example:
  Code: `200`

  Content:

```json
  {
  
    "database_status": "healthy"
  
  }
```            
  
  Error Response Example:

  Code: `404`

  Content:
  
```json
  {
  
    "error": "movies table does not exist"
  
  }
```

### Movie Management Routes

**Route: `/api/create-movie`**

  Request Type: `POST`
  
  Purpose: Add a new movie to the catalog.
  
  Request Body:
  
  `title (String)`: The title of the movie.
  
  Response Format: `JSON`
  
  Success Response Example:
  
  Code: `201`
  
  Content:
```json
  {
  
    "status": "success",
    "movie": "Inception"
  
  }
```
  Error Response Example:
  
  Code: `500`
  
  Content:
```json
  {
  
    "error": "Invalid input, all fields are required with valid values"
    
  }
```
  Example Request:
```json
  {
  
    "title": "Inception"
    
  }
```
  Example Response:
```json
  {
  
    "status": "success",
    "movie": "Inception"
  
  }
```

**Route: `/api/clear-catalog`**

  Request Type: `DELETE`
  
  Purpose: Clear the entire movies catalog by recreating the table.
  
  Response Format: `JSON`
  
  Success Response Example:
  
  Code: `200`

  Content:
```json
  {
  
    "status": "success"
    
  }
```

  Error Response Example:
  
  Code: `500`
  
  Content:
 ```json 
  {
  
    "error": "Database error while clearing the catalog"
    
  }
```

**Route: `/api/delete-movie/<movie_id>`**

  Request Type: `DELETE`
  
  Purpose: Delete a movie by its ID (soft delete).
  
  Path Parameters:
  
  movie_id (Integer): The ID of the movie to delete.
  
  Response Format: `JSON`
  
  Success Response Example:
  
  Code: `200`
  
  Content:
```json
  {
  
    "status": "success"
    
  }
```

  Error Response Example:

  Code: `500`
  
  Content:
 ```json 
  {
  
    "error": "Database error while deleting the movie"
    
  }
```
  Example Request:
```http
  DELETE /api/delete-movie/
```

  Example Response:
```json
  {
  
    "status": "success"
  
  }
```

**Route: `/api/get-all-movies-from-catalog`**

  Request Type: `GET`
  
  Purpose: Retrieve all non-deleted movies in the catalog.
  
  Query Parameters:
  
  `sort_by_watch_count (Boolean, optional)`: If true, sort movies by watch count.
  
  Response Format: `JSON`
  
  Success Response Example:
  
  Code: `200`
  
  Content:
```json
  {
  
    "status": "success",
    "movies": [
      {
        "id": 1,
        "title": "Inception",
        "director": "Christopher Nolan",
        "genre": "Sci-Fi",
        "year": 2010,
        "duration": 148,
        "watch_count": 3
      }
    ]

  }
```
  Error Response Example:
  
  Code: `500`
  
  Content:
```json
  {
  
    "error": "Database error while retrieving movies"
    
  }
```
  Example Request:

```http
  GET /api/get-all-movies-from-catalog?sort_by_watch_count=true
```

  Example Response:
```json
  {
  
    "status": "success",
    "movies": [
      {
        "id": 1,
        "title": "Inception",
        "director": "Christopher Nolan",
        "genre": "Sci-Fi",
        "year": 2010,
        "duration": 148,
        "watch_count": 3
      }
    ]
  
  }
``` 
**Route: `/api/get-movie-from-catalog-by-id/<movie_id>`**

  Request Type: `GET`
  
  Purpose: Retrieve a movie by its ID.
  
  Path Parameters:
  
  `movie_id (Integer)`: The ID of the movie.
  
  Response Format: `JSON`
  
  Success Response Example:
  
  Code: `200`

  Content:
```json
  {
  
    "status": "success",
    "movie": {
      "id": 1,
      "title": "Inception",
      "director": "Christopher Nolan",
      "genre": "Sci-Fi",
      "year": 2010,
      "duration": 148
    }
  
  }
```
  Error Response Example:
  
  Code: `500`
  
  Content:
```json
  {
  
    "error": "Database error while retrieving movie by ID"
  
  }
```

  Example Request:
```http
  GET /api/get-movie-from-catalog-by-id/1
```

  Example Response:
 ```json 
  {
  
    "status": "success",
    "movie": {
      "id": 1,
      "title": "Inception",
      "director": "Christopher Nolan",
      "genre": "Sci-Fi",
      "year": 2010,
      "duration": 148
    }
  
  }
```
**Route: `/api/get-movie-from-catalog-by-compound-key`**

  Request Type: `GET`
  
  Purpose: Retrieve a movie by its compound key `(director, title, year)`.
  
  Query Parameters:
  
  ``director (String)``: The director's name.
  
  ``title (String)``: The movie title.
  
  ``year (Integer)``: The year the movie was released.
  
  Response Format: `JSON`
  
  Success Response Example:
  
  Code: `200`

  Content:
 ```json 
  {
  
    "status": "success",
    "movie": {
      "id": 1,
      "title": "Inception",
      "director": "Christopher Nolan",
      "genre": "Sci-Fi",
      "year": 2010,
      "duration": 148
    }
  
  }
```
Error Response Example:

Code: `500`

Content:
```json
  {
    "error": "Invalid input, missing required query parameters"
  }
```
  Example Request:
```http
  GET /api/get-movie-from-catalog-by-compound-key?director=Christopher%20Nolan&title=Inception&year=2010
```

  Example Response:
```json
  {
  
    "status": "success",
    "movie": {
      "id": 1,
      "title": "Inception",
      "director": "Christopher Nolan",
      "genre": "Sci-Fi",
      "year": 2010,
      "duration": 148
    }
 
  }
``` 
### Watchlist Management Routes

**Route: `/api/add-movie-to-watchlist`**

Request Type: `POST`

Purpose: Adds a new movie to the watchlist by compound key

Response Format: `JSON`

Success Response Example:
```json
  {
  
    "status": "success, movie added to watchlist"
    
  }
```
  
Error Response Example:
```json
  {
  
    "error": "Error adding movie to watchlist"
  
  }
```
**Route: `/api/remove-movie-from-watchlist`**

Request Type: `DELETE`

Purpose: Removes a movie from the watchlist by compound key

Response Format: `JSON`

Success Response Example:
```json
  {
  
    "status": "success, movie removed from watchlist"
    
  }
```
  
Error Response Example:
```json
  {
  
    "error": "Error removing movie from watchlist"
  
  }
```

**Route: `/api/remove-movie-from-watchlist-by-list-number/<int:list_number>`**

Request Type: `DELETE`

Purpose: Removes a movie from the watchlist by list number

Response Format: `JSON`

Success Response Example:
```json
  {
  
    "status": "success, movie at list number 5 removed from watchlist"
    
  }
```
Error Response Example:
```json
  {
    "error": "Error removing movie by list number”
    "error": "Error removing movie from watchlist”
  }
```

**Route: `/api/clear-watchlist`**

Request Type: `POST`

Purpose: Clears all movies from the watchlist

Response Format: `JSON`

Success Response Example:
```json
  {
  
    "status": "success, watchlist cleared"
    
  }
```
  
Error Response Example:
```json
  {
  
    "error": "Error clearing the watchlist”
  
  }
```

**Route: `/api/get-all-movies-from-watchlist`**

Request Type:`GET`

Purpose: Retrieves all movies in the watchlist

Response Format:`JSON`

Success Response Example:
```json
  {
  
    "status": "success"
    "movies": Inception, Barbie, The Holdovers, Fantastic Mr. Fox, Scott   Pilgrim vs. the World 
    
  }
```
  
Error Response Example:
```json
  {
  
    "error": "Error retrieving the movies from watchlist”
  
  }
```

**Route: `/api/get-movie-from-watchlist-by-list-number/<int:list_number>`**

Request Type:`GET`

Purpose: Retrieves a movie form the watchlist by its list number

Response Format:`JSON`

Success Response Example:
```json
  {
  
    "status": "success"
    "movie": Scott Pilgrim vs. the World
 
  }
```
  
Error Response Example:
```json
  {
  
   "error": "Error retrieving movie by list number”
   "error”: “Error retrieving movie from watchlist”

  }
```

**Route: `/api/get-watchlist-length-duration`**

Request Type:`GET`

Purpose: Retrieves both total number of movies in list and total duration of the watchlist

Response Format:`JSON`

Success Response Example:
```json
  {
  
  "status": "success"
  "watchlist_length": 10
  "watchlist_duration": 1080

  }
```
  
Error Response Example:
```json
  {
  
  "error": "Error retrieving watchlist length and duration"
  "error": “Error retrieving movie from watchlist”
  
  }
```

**Route: `/api/go-to-list-number/<int:list_number>`**

Request Type:`POST`

Purpose: Sets the watchlist to start playing from a specific list number

Response Format:`JSON`

Success Response Example:
```json
  {
  
  "status": "success"
  "list_number": 3

  }
```
  
Error Response Example:
```json
  {
  
  "error": "Error going to list number 3”

  }
```


### Arrange Watchlist Routes
**Route: `/api/move-movie-to-beginning`**

- Request Type:`POST`

- Purpose: move a movie to the beginning of the watchlist.

- Request Body:
    - `director (String)`: The director of the movie.
    - `title(String)`: The title of the movie.
    - `year(Integer)`: The year the movie was released.
- Response Format:`JSON`
    - Success Response Example:
        - code:`200`
        - content:
```json   
      {

        "status": "success",
        "movie": "Inception"
     
      }
```
- Error Response Example:
    - code:`500`
    - content:
```json   
        {

          "error": "Invalid input, all fields are required with valid values"

        }
```
- Example Request:
```json   
    {
        "director": "Christopher Nolan",
        "title": "Inception",
        "year": 2010
    }
```
- Example Response:
```json   
    {
        "status": "success",
        "movie": "Inception"
    }
```

**Route: `/api/move-movie-to-end`**

- Request Type:`POST`

- Purpose: Move a movie to the end of the watchlist.

- Request Body:
    - `director (String)`: The director of the movie.
    - `title (String)`: The title of the movie.
    - `year (Integer)`: The year the movie was released.

- Response Format:`JSON`
    - Success Response Example:
        - code:`200`
        - content:
          ```json
          {
              "status": "success",
              "movie": "Inception"
          }
          ```
    - Error Response Example:
        - code:`500`
        - content:
          ```json
          {
              "error": "Invalid input, all fields are required with valid values"
          }
          ```

- Example Request:
  ```json
  {
      "director": "Christopher Nolan",
      "title": "Inception",
      "year": 2010
  }
  ```

- Example Response:
  ```json
  {
      "status": "success",
      "movie": "Inception"
  }
  ```

---

**Route: `/api/move-movie-to-list-number`**

- Request Type:`POST`

- Purpose: Move a movie to a specific list number in the watchlist.

- Request Body:
    - `director (String)`: The director of the movie.
    - `title (String)`: The title of the movie.
    - `year (Integer)`: The year the movie was released.
    - `list_number (Integer)`: The new list number to move the movie to.

- Response Format:`JSON`
    - Success Response Example:
        - code:`200`
        - content:
          ```json
          {
              "status": "success",
              "movie": "Inception",
              "list_number": 2
          }
          ```
    - Error Response Example:
        - code:`500`
        - content:
          ```json
          {
              "error": "Invalid input, all fields are required with valid values"
          }
          ```

- Example Request:
  ```json
  {
      "director": "Christopher Nolan",
      "title": "Inception",
      "year": 2010,
      "list_number": 2
  }
  ```

- Example Response:
  ```json
  {
      "status": "success",
      "movie": "Inception",
      "list_number": 2
  }
  ```

---

**Route: `/api/swap-movies-in-watchlist`**

- Request Type:`POST`

- Purpose: Swap two movies in the watchlist by their list numbers.

- Request Body:
    - `list_number_1 (Integer)`: The list number of the first movie.
    - `list_number_2 (Integer)`: The list number of the second movie.

- Response Format:`JSON`
    - Success Response Example:
        - code:`200`
        - content:
          ```json
          {
              "status": "success",
              "swapped_movies": {
                  "list_1": {
                      "id": 1,
                      "director": "Christopher Nolan",
                      "title": "Inception"
                  },
                  "list_2": {
                      "id": 2,
                      "director": "Quentin Tarantino",
                      "title": "Pulp Fiction"
                  }
              }
          }
          ```
    - Error Response Example:
        - code:`500`
        - content:
          ```json
          {
              "error": "Invalid list numbers or movies not found"
          }
          ```

- Example Request:
  ```json
  {
      "list_number_1": 1,
      "list_number_2": 2
  }
  ```

- Example Response:
  ```json
  {
      "status": "success",
      "swapped_movies": {
          "list_1": {
              "id": 1,
              "director": "Christopher Nolan",
              "title": "Inception"
          },
          "list_2": {
              "id": 2,
              "director": "Quentin Tarantino",
              "title": "Pulp Fiction"
          }
      }
  }
  ```

---

**Route: `/api/movie-leaderboard`**

- Request Type:`GET`

- Purpose:`GET` a list of all movies sorted by watch count.

- Response Format:`JSON`
    - Success Response Example:
        - code:`200`
        - content:
          ```json
          {
              "status": "success",
              "leaderboard": [
                  {
                      "id": 1,
                      "director": "Christopher Nolan",
                      "title": "Inception",
                      "watch_count": 42
                  },
                  {
                      "id": 2,
                      "director": "Steven Spielberg",
                      "title": "Jurassic Park",
                      "watch_count": 35
                  }
              ]
          }
          ```
    - Error Response Example:
        - code:`500`
        - content:
          ```json
          {
              "error": "Error generating leaderboard"
          }
          ```

- Example Request:
  ```http
  GET /api/movie-leaderboard
  ```

- Example Response:
  ```json
  {
      "status": "success",
      "leaderboard": [
          {
              "id": 1,
              "director": "Christopher Nolan",
              "title": "Inception",
              "watch_count": 42
          },
          {
              "id": 2,
              "director": "Steven Spielberg",
              "title": "Jurassic Park",
              "watch_count": 35
          }
      ]
  }
  ```

### User Routes
**Route: `/api/login`**

  Request Type:`POST`
  
  Purpose: Validate a user's credentials.
  
  Request Body:

  - `username (String)`: The user's username.

  - `password (String)`: The user's password.
  
  Response Format:`JSON`
  
  Success Response Example:
  
  Code:`200`
  
  Content:
  
  {
  
  	"status": "success", "username": username 
  
  }
  
  Error Response Example:
  
  Code: `401`
  
  Content:
```json
  {
  
  	"error": "Invalid credentials"
  
  }
```
  
**Route: `/api/create-account`**
  
  Request Type:`POST`
  
  Purpose: Create a new user account.
  
  Request Body:
  
  - `username (String)`: The user's username.

  - `password (String)`: The user's password.
  
  Response Format:`JSON`
  
  Success Response Example:
  
  Code: `201`
  
  Content:
 ```json 
  {
  
	"status": "success", "username": username 
  
  }
```
  
  Error Response Example:

  Code: `400`
  
  Content:
```json 
  {
  
	"error": "Error creating account."
  
  }
```
  
**Route: `/api/update-password`**
  
  Request Type:`POST`
  
  Purpose: Update a user's password.
  
  Request Body:

  - `username (String)`: The user's username.
  
  - `old_password (String)`: The user's current password.
  
  - `new_password (String)`: The user's new password.
  
  Response Format:`JSON`
  
  Success Response Example:
  
  Code:`200`
  
  Content:
```json
  {
  
	"status": "success", "username": username 
  
  }
``` 
  
  Error Response Example:

  Code: `400`
  
  Content:
```json
  {
  
    "error": "Error updating user password."
  
  }
``` 