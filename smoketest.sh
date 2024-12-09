#!/bin/bash

source .env
# Define the base URL for the Flask API
BASE_URL="http://localhost:$PORT/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done


###############################################
#
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

# Function to check the database connection
check_db() {
  echo "Checking database connection..."
  curl -s -X GET "$BASE_URL/db-check" | grep -q '"database_status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Database connection is healthy."
  else
    echo "Database check failed."
    exit 1
  fi
}


##########################################################
#
# Movie Management
#
##########################################################

clear_catalog() {
  echo "Clearing the watchlist..."
  curl -s -X DELETE "$BASE_URL/clear-catalog" | grep -q '"status": "success"'
}


create_movie() {
  title=$1

  echo "Adding movie ($title) to the watchlist..."
  curl -s -X POST "$BASE_URL/create-movie" -H "Content-Type: application/json" \
    -d "{\"title\":\"$title\"}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Movie added successfully."
  else
    echo "Failed to add movie."
    exit 1
  fi
}

delete_movie_by_id() {
  movie_id=$1

  echo "Deleting movie by ID ($movie_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-movie/$movie_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Movie deleted successfully by ID ($movie_id)."
  else
    echo "Failed to delete movie by ID ($movie_id)."
    exit 1
  fi
}

get_all_movies() {
  echo "Getting all movies in the watchlist..."
  response=$(curl -s -X GET "$BASE_URL/get-all-movies-from-catalog")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "All movies retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Movies JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get movies."
    exit 1
  fi
}

get_movie_by_id() {
  movie_id=$1

  echo "Getting movie by ID ($movie_id)..."
  response=$(curl -s -X GET "$BASE_URL/get-movie-from-catalog-by-id/$movie_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Movie retrieved successfully by ID ($movie_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Movie JSON (ID $movie_id):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get movie by ID ($movie_id)."
    exit 1
  fi
}

get_movie_by_compound_key() {
  director=$1
  title=$2
  year=$3

  echo "Getting movie by compound key (Director: '$director', Title: '$title', Year: $year)..."
  response=$(curl -s -X GET "$BASE_URL/get-movie-from-catalog-by-compound-key?director=$(echo $director | sed 's/ /%20/g')&title=$(echo $title | sed 's/ /%20/g')&year=$year")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Movie retrieved successfully by compound key."
    if [ "$ECHO_JSON" = true ]; then
      echo "Movie JSON (by compound key):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get movie by compound key."
    exit 1
  fi
}

############################################################
#
# Watchlist Management
#
############################################################

add_movie_to_watchlist() {
  director=$1
  title=$2
  year=$3

  echo "Adding movie to watchlist: $director - $title ($year)..."
  response=$(curl -s -X POST "$BASE_URL/add-movie-to-watchlist" \
    -H "Content-Type: application/json" \
    -d "{\"director\":\"$director\", \"title\":\"$title\", \"year\":$year}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Movie added to watchlist successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Movie JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to add movie to watchlist."
    exit 1
  fi
}

remove_movie_from_watchlist() {
  director=$1
  title=$2
  year=$3

  echo "Removing movie from watchlist: $director - $title ($year)..."
  response=$(curl -s -X DELETE "$BASE_URL/remove-movie-from-watchlist" \
    -H "Content-Type: application/json" \
    -d "{\"director\":\"$director\", \"title\":\"$title\", \"year\":$year}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Movie removed from watchlist successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Movie JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to remove movie from watchlist."
    exit 1
  fi
}

remove_movie_by_list_number() {
  list_number=$1

  echo "Removing movie by list number: $list_number..."
  response=$(curl -s -X DELETE "$BASE_URL/remove-movie-from-watchlist-by-list-number/$list_number")

  if echo "$response" | grep -q '"status":'; then
    echo "Movie removed from watchlist by list number ($list_number) successfully."
  else
    echo "Failed to remove movie from watchlist by list number."
    exit 1
  fi
}

clear_watchlist() {
  echo "Clearing watchlist..."
  response=$(curl -s -X POST "$BASE_URL/clear-watchlist")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Watchlist cleared successfully."
  else
    echo "Failed to clear watchlist."
    exit 1
  fi
}


############################################################
#
# Pulling Watchlist Info
#
############################################################

get_all_movies_from_watchlist() {
  echo "Retrieving all movies from watchlist..."
  response=$(curl -s -X GET "$BASE_URL/get-all-movies-from-watchlist")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "All movies retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Movies JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve all movies from watchlist."
    exit 1
  fi
}

get_movie_from_watchlist_by_list_number() {
  list_number=$1
  echo "Retrieving movie by list number ($list_number)..."
  response=$(curl -s -X GET "$BASE_URL/get-movie-from-watchlist-by-list-number/$list_number")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Movie retrieved successfully by list number."
    if [ "$ECHO_JSON" = true ]; then
      echo "Movie JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve movie by list number."
    exit 1
  fi
}

get_watchlist_length_duration() {
  echo "Retrieving watchlist length and duration..."
  response=$(curl -s -X GET "$BASE_URL/get-watchlist-length-duration")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Watchlist length and duration retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Watchlist Info JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve watchlist length and duration."
    exit 1
  fi
}

go_to_list_number() {
  list_number=$1
  echo "Going to list number ($list_number)..."
  response=$(curl -s -X POST "$BASE_URL/go-to-list-number/$list_number")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Moved to list number ($list_number) successfully."
  else
    echo "Failed to move to list number ($list_number)."
    exit 1
  fi
}

############################################################
#
# Arrange Watchlist
#
############################################################

move_movie_to_beginning() {
  director=$1
  title=$2
  year=$3

  echo "Moving movie ($director - $title, $year) to the beginning of the watchlist..."
  response=$(curl -s -X POST "$BASE_URL/move-movie-to-beginning" \
    -H "Content-Type: application/json" \
    -d "{\"director\": \"$director\", \"title\": \"$title\", \"year\": $year}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Movie moved to the beginning successfully."
  else
    echo "Failed to move movie to the beginning."
    exit 1
  fi
}

move_movie_to_end() {
  director=$1
  title=$2
  year=$3

  echo "Moving movie ($director - $title, $year) to the end of the watchlist..."
  response=$(curl -s -X POST "$BASE_URL/move-movie-to-end" \
    -H "Content-Type: application/json" \
    -d "{\"director\": \"$director\", \"title\": \"$title\", \"year\": $year}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Movie moved to the end successfully."
  else
    echo "Failed to move movie to the end."
    exit 1
  fi
}

move_movie_to_list_number() {
  director=$1
  title=$2
  year=$3
  list_number=$4

  echo "Moving movie ($director - $title, $year) to list number ($list_number)..."
  response=$(curl -s -X POST "$BASE_URL/move-movie-to-list-number" \
    -H "Content-Type: application/json" \
    -d "{\"director\": \"$director\", \"title\": \"$title\", \"year\": $year, \"list_number\": $list_number}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Movie moved to list number ($list_number) successfully."
  else
    echo "Failed to move movie to list number ($list_number)."
    exit 1
  fi
}

swap_movies_in_watchlist() {
  list_number1=$1
  list_number2=$2

  echo "Swapping movies at list numbers ($list_number1) and ($list_number2)..."
  response=$(curl -s -X POST "$BASE_URL/swap-movies-in-watchlist" \
    -H "Content-Type: application/json" \
    -d "{\"list_number_1\": $list_number1, \"list_number_2\": $list_number2}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Movies swapped successfully between list numbers ($list_number1) and ($list_number2)."
  else
    echo "Failed to swap movies."
    exit 1
  fi
}

######################################################
#
# Leaderboard
#
######################################################

# Function to get the movie leaderboard sorted by watch count
get_movie_leaderboard() {
  echo "Getting movie leaderboard sorted by watch count..."
  response=$(curl -s -X GET "$BASE_URL/movie-leaderboard?sort=watch_count")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Movie leaderboard retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON (sorted by watch count):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get movie leaderboard."
    exit 1
  fi
}

######################################################
#
# User
#
######################################################

# Function to log in a user
login(){
  username=$1
  password=$2

  echo "Logging in..."
  curl -s -X POST "$BASE_URL/login" -H "Content-Type: application/json" \
    -d "{\"username\":\"$username\", \"password\":\"$password\"}" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Logged in successfully."
  else
    echo "Failed to log in."
    exit 1
  fi
}

# Function to create a user account
create_account() {
  username=$1
  password=$2

  echo "Creating a user account..."
  curl -s -X POST "$BASE_URL/create-account" -H "Content-Type: application/json" \
    -d "{\"username\":\"$username\", \"password\":\"$password\"}" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "User account created successfully."
  else
    echo "Failed to create user account."
    exit 1
  fi
}

# Function to update password
update_password(){
  username=$1
  old_password=$2
  new_password=$3

  echo "Updating password..."
  curl -s -X POST "$BASE_URL/update-password" -H "Content-Type: application/json" \
    -d "{\"username\":\"$username\", \"old_password\":\"$old_password\", \"new_password\":\"$new_password\"}" | grep -q '"status": "success"'
  if [ $? -eq 0 ]; then
    echo "Password updated successfully."
  else
    echo "Failed to update password."
    exit 1
  fi
}



# Health checks
check_health
check_db

#Clear the catalog
clear_catalog

# Create movies
create_movie "The Holdovers"
create_movie "The Notebook"
create_movie "Interstellar"
create_movie "Scream"
create_movie "12 Angry Men"

delete_movie_by_id 1
get_all_movies

get_movie_by_id 2
get_movie_by_compound_key "Christopher Nolan" "Interstellar" 2014

clear_watchlist

add_movie_to_watchlist "Nick Cassavetes" "The Notebook" 2004
add_movie_to_watchlist "Wes Craven" "Scream" 1996
add_movie_to_watchlist "Sidney Lumet" "12 Angry Men" 1957
add_movie_to_watchlist "Christopher Nolan" "Interstellar" 2014

remove_movie_from_watchlist "Christopher Nolan" "Interstellar" 2014
remove_movie_by_list_number 2

get_all_movies_from_watchlist

add_movie_to_watchlist "Wes Craven" "Scream" 1996
add_movie_to_watchlist "Christopher Nolan" "Interstellar" 2014

move_movie_to_beginning "Christopher Nolan" "Interstellar" 2014
move_movie_to_end "Wes Craven" "Scream" 1996
move_movie_to_list_number "Sidney Lumet" "12 Angry Men" 1957 2
swap_movies_in_watchlist 1 2

get_all_movies_from_watchlist
get_movie_from_watchlist_by_list_number 1

get_watchlist_length_duration

get_movie_leaderboard

create_account "testuser" "password"
login "testuser" "password"
update_password "testuser" "password" "newpassword"

echo "All tests passed successfully!"