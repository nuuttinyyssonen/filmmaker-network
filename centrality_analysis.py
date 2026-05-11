import networkx as nx
import pandas as pd
from collections import defaultdict

def load_network_from_csv(csv_file: str) -> nx.Graph:
    """Load network from CSV file and create a weighted graph."""
    df = pd.read_csv(csv_file)
    G = nx.Graph()
    
    for _, row in df.iterrows():
        G.add_edge(row['Source'], row['Target'], weight=row['Weight'])
    
    return G

def compute_centrality_measures(G: nx.Graph) -> dict:
    """Compute various centrality measures for the network."""
    centrality = {}
    
    # Degree centrality
    centrality['degree'] = nx.degree_centrality(G)
    
    # Betweenness centrality
    centrality['betweenness'] = nx.betweenness_centrality(G, weight='weight')
    
    # Closeness centrality
    centrality['closeness'] = nx.closeness_centrality(G, distance='weight')
    
    # Eigenvector centrality
    try:
        centrality['eigenvector'] = nx.eigenvector_centrality(G, weight='weight', max_iter=1000)
    except:
        print("Warning: Eigenvector centrality could not be computed")
        centrality['eigenvector'] = {}
    
    # PageRank
    centrality['pagerank'] = nx.pagerank(G, weight='weight')
    
    # Weighted degree (strength)
    centrality['weighted_degree'] = dict(G.degree(weight='weight'))
    
    return centrality

def print_centrality_summary(G: nx.Graph, centrality: dict) -> None:
    """Print a summary of centrality measures."""
    print(f"\n{'='*80}")
    print(f"NETWORK CENTRALITY ANALYSIS")
    print(f"{'='*80}\n")
    
    print(f"Network Statistics:")
    print(f"  - Number of nodes (movies): {G.number_of_nodes()}")
    print(f"  - Number of edges: {G.number_of_edges()}")
    print(f"  - Density: {nx.density(G):.4f}")
    print(f"  - Average clustering coefficient: {nx.average_clustering(G):.4f}\n")
    
    # Degree Centrality
    print(f"{'DEGREE CENTRALITY':-^80}")
    print(f"(Proportion of movies a movie is connected to)\n")
    sorted_degree = sorted(centrality['degree'].items(), key=lambda x: x[1], reverse=True)
    for movie, score in sorted_degree[:10]:
        print(f"  {movie:<40} {score:.4f}")
    
    # Betweenness Centrality
    print(f"\n{'BETWEENNESS CENTRALITY':-^80}")
    print(f"(How often a movie lies on shortest paths between other movies)\n")
    sorted_betweenness = sorted(centrality['betweenness'].items(), key=lambda x: x[1], reverse=True)
    for movie, score in sorted_betweenness[:10]:
        print(f"  {movie:<40} {score:.4f}")
    
    # Closeness Centrality
    print(f"\n{'CLOSENESS CENTRALITY':-^80}")
    print(f"(Average proximity to all other movies)\n")
    sorted_closeness = sorted(centrality['closeness'].items(), key=lambda x: x[1], reverse=True)
    for movie, score in sorted_closeness[:10]:
        print(f"  {movie:<40} {score:.4f}")
    
    # Eigenvector Centrality
    if centrality['eigenvector']:
        print(f"\n{'EIGENVECTOR CENTRALITY':-^80}")
        print(f"(Connectivity to well-connected movies)\n")
        sorted_eigenvector = sorted(centrality['eigenvector'].items(), key=lambda x: x[1], reverse=True)
        for movie, score in sorted_eigenvector[:10]:
            print(f"  {movie:<40} {score:.4f}")
    
    # PageRank
    print(f"\n{'PAGERANK':-^80}")
    print(f"(Importance based on network structure)\n")
    sorted_pagerank = sorted(centrality['pagerank'].items(), key=lambda x: x[1], reverse=True)
    for movie, score in sorted_pagerank[:10]:
        print(f"  {movie:<40} {score:.4f}")
    
    # Weighted Degree
    print(f"\n{'WEIGHTED DEGREE (Network Strength)':-^80}")
    print(f"(Total weight of connections per movie)\n")
    sorted_weighted = sorted(centrality['weighted_degree'].items(), key=lambda x: x[1], reverse=True)
    for movie, score in sorted_weighted[:10]:
        print(f"  {movie:<40} {score:.1f}")

def export_centrality_to_csv(G: nx.Graph, centrality: dict, output_file: str = "centrality_measures.csv") -> None:
    """Export centrality measures to CSV file."""
    nodes = list(G.nodes())
    data = {
        'Movie': nodes,
        'Degree_Centrality': [centrality['degree'].get(node, 0) for node in nodes],
        'Betweenness_Centrality': [centrality['betweenness'].get(node, 0) for node in nodes],
        'Closeness_Centrality': [centrality['closeness'].get(node, 0) for node in nodes],
        'Eigenvector_Centrality': [centrality['eigenvector'].get(node, 0) for node in nodes],
        'PageRank': [centrality['pagerank'].get(node, 0) for node in nodes],
        'Weighted_Degree': [centrality['weighted_degree'].get(node, 0) for node in nodes],
    }
    
    df = pd.DataFrame(data)
    df = df.sort_values('Betweenness_Centrality', ascending=False)
    df.to_csv(output_file, index=False)
    print(f"\nCentrality measures exported to: {output_file}")

def main():
    # Load the network
    print("Loading network from CSV...")
    G = load_network_from_csv("Quentin_Tarantino_movie_graph.csv")
    
    # Compute centrality measures
    print("Computing centrality measures...")
    centrality = compute_centrality_measures(G)
    
    # Print summary
    print_centrality_summary(G, centrality)
    
    # Export to CSV
    export_centrality_to_csv(G, centrality)

if __name__ == "__main__":
    main()
