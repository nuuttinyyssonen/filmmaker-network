import requests
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}


def search_director(name: str) -> list[dict]:
    """Search for a person by name and return matching results."""
    url = f"{BASE_URL}/search/person"
    params = {"query": name}
    response = requests.get(url, headers=HEADERS, params=params)
    response.raise_for_status()
    return response.json().get("results", [])

def get_directed_movies(person_id: int) -> list[dict]:
    url = f"{BASE_URL}/person/{person_id}/movie_credits"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    crew = response.json().get("crew", [])
    return [m for m in crew if m.get("job") == "Director"]
 
 
results = search_director("Quentin Tarantino")
director = results[0]
print(f"Found: {director['name']} (ID: {director['id']})")
 
movies = get_directed_movies(director["id"])
print(director ["name"], "has directed", len(movies), "movies.")
for movie in movies:
    print(movie["title"])
