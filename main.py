import requests
from dotenv import load_dotenv
import os
from collections import defaultdict
import csv
from itertools import combinations

load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"

HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}


def search_director(name: str) -> list[dict]:
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

def build_movie_graph(movie_casts: dict[str, list[dict]]) -> list[dict]:
    """
    Build edges between movies that share actors.
    Each edge: {source, target, weight, shared_actors}
    """
    # movie_title -> set of actor IDs
    movie_actor_ids = {
        title: {actor["id"] for actor in cast}
        for title, cast in movie_casts.items()
    }
    # actor_id -> name for lookup
    actor_id_to_name = {
        actor["id"]: actor["name"]
        for cast in movie_casts.values()
        for actor in cast
    }

    edges = []
    for (title_a, ids_a), (title_b, ids_b) in combinations(movie_actor_ids.items(), 2):
        shared_ids = ids_a & ids_b
        if shared_ids:
            shared_names = [actor_id_to_name[aid] for aid in shared_ids]
            edges.append({
                "source": title_a,
                "target": title_b,
                "weight": len(shared_ids),
                "shared_actors": "; ".join(sorted(shared_names))
            })

    return sorted(edges, key=lambda e: -e["weight"])

def export_graph_csv(edges: list[dict], director_name: str) -> None:
    base = director_name.replace(" ", "_")

    with open(f"{base}_movie_graph.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["Source", "Target", "Weight", "shared_actors"])
        writer.writeheader()
        for edge in edges:
            writer.writerow({"Source": edge["source"], "Target": edge["target"],
                             "Weight": edge["weight"], "shared_actors": edge["shared_actors"]})
    print(f"Exported {len(edges)} edges")


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
    for actor in cast:
        print(f"  - {actor['name']} as {actor['character']}")

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

edges = build_movie_graph(movie_casts)
export_graph_csv(edges, director["name"])