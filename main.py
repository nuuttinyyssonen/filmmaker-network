import requests
from dotenv import load_dotenv
import os
from collections import defaultdict

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

def get_movie_cast(movie_id: int) -> list[dict]:
    url = f"{BASE_URL}/movie/{movie_id}/credits"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json().get("cast", [])

def find_shared_actors(movie_casts: dict[str, list[dict]]) -> dict[str, list[str]]:
    """
    Given a dict of {movie_title: cast_list}, return actors who appear
    in more than one movie, mapped to the list of movie titles they appear in.
    """
    actor_appearances = defaultdict(lambda: {"name": "", "movies": []})

    for movie_title, cast in movie_casts.items():
        for actor in cast:
            entry = actor_appearances[actor["id"]]
            entry["name"] = actor["name"]
            entry["movies"].append(movie_title)

    return {
        data["name"]: data["movies"]
        for data in actor_appearances.values()
        if len(data["movies"]) > 1
    }


results = search_director("Quentin Tarantino")
director = results[0]
print(f"Found: {director['name']} (ID: {director['id']})")

movies = get_directed_movies(director["id"])
print(f"{director['name']} has directed {len(movies)} movies.\n")

movie_casts = {}
for movie in movies:
    print(f"{movie['title']}")
    cast = get_movie_cast(movie["id"])
    movie_casts[movie["title"]] = cast

shared = find_shared_actors(movie_casts)

print("\n" + "=" * 50)
print(f"SHARED ACTORS ACROSS {director['name']}'s FILMS")
print("=" * 50)

if not shared:
    print("No shared actors found.")
else:
    for actor_name, film_list in sorted(shared.items(), key=lambda x: -len(x[1])):
        print(f"\n{actor_name} ({len(film_list)} films)")
        for title in film_list:
            print(f"  • {title}")