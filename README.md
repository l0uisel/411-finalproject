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

###Routing Documentation (app.py)
## Health Check Routes

### **Route: `/api/health`**

- **Request Type**: `GET`
- **Purpose**: Verify if the service is running.

#### Response Format

- **Success Response Example**:
  ```json
  {
      "status": "healthy"
  }
  ```

---

### **Route: `/api/db-check`**

- **Request Type**: `GET`
- **Purpose**: Verify the database connection and ensure the required tables exist.

#### Response Format

- **Success Response Example**:
  ```json
  {
      "database_status": "healthy"
  }
  ```

- **Error Response Example**:
  ```json
  {
      "error": "movies table does not exist"
  }
  ```

---

## Movie Catalog Routes

### **Route: `/api/create-movie`**

- **Request Type**: `POST`
- **Purpose**: Add a new movie to the catalog.

#### Request Body

```json
{
    "title": "Inception"
}
```

#### Response Format

- **Success Response Example**:
  ```json
  {
      "status": "success",
      "movie": "Inception"
  }
  ```

- **Error Response Example**:
  ```json
  {
      "error": "Invalid input, all fields are required with valid values"
  }
  ```

---

### **Route: `/api/clear-catalog`**

- **Request Type**: `DELETE`
- **Purpose**: Clear the entire movie catalog.

#### Response Format

- **Success Response Example**:
  ```json
  {
      "status": "success"
  }
  ```

---

## Watchlist Management Routes

### **Route: `/api/add-movie-to-watchlist`**

- **Request Type**: `POST`
- **Purpose**: Add a new movie to the watchlist by compound key.

#### Response Format

- **Success Response Example**:
  ```json
  {
      "status": "success, movie added to watchlist"
  }
  ```

- **Error Response Example**:
  ```json
  {
      "error": "Error adding movie to watchlist"
  }
  ```

---

### **Route: `/api/remove-movie-from-watchlist`**

- **Request Type**: `DELETE`
- **Purpose**: Remove a movie from the watchlist by compound key.

#### Response Format

- **Success Response Example**:
  ```json
  {
      "status": "success, movie removed from watchlist"
  }
  ```

- **Error Response Example**:
  ```json
  {
      "error": "Error removing movie from watchlist"
  }
  ```

---

## Arrange Watchlist Routes

### **Route: `/api/move-movie-to-beginning`**

- **Request Type**: `POST`
- **Purpose**: Move a movie to the beginning of the watchlist.

#### Request Body

```json
{
    "director": "Christopher Nolan",
    "title": "Inception",
    "year": 2010
}
```

#### Response Format

- **Success Response Example**:
  ```json
  {
      "status": "success",
      "movie": "Inception"
  }
  ```

- **Error Response Example**:
  ```json
  {
      "error": "Invalid input, all fields are required with valid values"
  }
  ```

---

### **Route: `/api/move-movie-to-end`**

- **Request Type**: `POST`
- **Purpose**: Move a movie to the end of the watchlist.

#### Request Body

```json
{
    "director": "Christopher Nolan",
    "title": "Inception",
    "year": 2010
}
```

#### Response Format

- **Success Response Example**:
  ```json
  {
      "status": "success",
      "movie": "Inception"
  }
  ```

- **Error Response Example**:
  ```json
  {
      "error": "Invalid input, all fields are required with valid values"
  }
  ```

---

### **Route: `/api/move-movie-to-list-number`**

- **Request Type**: `POST`
- **Purpose**: Move a movie to a specific list number in the watchlist.

#### Request Body

```json
{
    "director": "Christopher Nolan",
    "title": "Inception",
    "year": 2010,
    "list_number": 2
}
```

#### Response Format

- **Success Response Example**:
  ```json
  {
      "status": "success",
      "movie": "Inception",
      "list_number": 2
  }
  ```

- **Error Response Example**:
  ```json
  {
      "error": "Invalid input, all fields are required with valid values"
  }
  ```

---

### **Route: `/api/swap-movies-in-watchlist`**

- **Request Type**: `POST`
- **Purpose**: Swap two movies in the watchlist by their list numbers.

#### Request Body

```json
{
    "list_number_1": 1,
    "list_number_2": 2
}
```

#### Response Format

- **Success Response Example**:
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

- **Error Response Example**:
  ```json
  {
      "error": "Invalid list numbers or movies not found"
  }
  ```

---

## Leaderboard Route

### **Route: `/api/movie-leaderboard`**

- **Request Type**: `GET`
- **Purpose**: Get a list of all movies sorted by watch count.

#### Response Format

- **Success Response Example**:
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

<<<<<<< HEAD
- **Error Response Example**:
  ```json
  {
      "error": "Error generating leaderboard"
  }
  ```
=======
    "status": "success"

}

#### User
**Route: /api/login**

  Request Type: POST
  
  Purpose: Validate a user's credentials.
  
  Request Body:
  
  {
  
    "username": "string",
    "password": "string"
  
  }
  
  Response Format: JSON
  
  Success Response Example:
  
  {
  
    "status": "success",
    "username": "newuser1"
  
  }
  
  Error Response Example:
  
  {
  
    "error": "Invalid credentials"
  
  }
  
**Route: /api/create-account**
  
  Request Type: POST
  
  Purpose: Create a new user account.
  
  Request Body:
  
  {
  
    "username": "string",
    "password": "string"
  
  }
  
  Response Format: JSON
  
  Success Response Example:
  
  {
  
    "status": "success",
    "username": "newuser1"
  
  }
  
  Error Response Example:
  
  {
  
   "error": "Username already exists"
  
  }
  
**Route: /api/update-password**
  
  Request Type: POST
  
  Purpose: Update a user's password.
  
  Request Body:
  
  {
  
    "username": "string",
    "old_password": "string",
    "new_password": "string"
  
  }
  
  Response Format: JSON
  
  Success Response Example:
  
  {
  
    "status": "success",
    "username": "newuser1"
  
  }
  
  
  Error Response Example:
  
  {
  
    "error": "Invalid credentials"
  
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
>>>>>>> 55fc466da783cbd6e1b5c3165bb942eeddd70fd2
