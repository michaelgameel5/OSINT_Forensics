import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pyvis.network import Network
import requests
import json
import os
import datetime

class NetworkGraph:
    def __init__(self, output_dir="data/graphs"):
        self.graph = nx.DiGraph()
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

    # ─────────────────────────────────────────
    # ADD RELATIONSHIPS MANUALLY
    # ─────────────────────────────────────────
    def add_relationship(self, account_a: str, account_b: str, relation: str = "follows"):
        self.graph.add_edge(account_a, account_b, label=relation)

    # ─────────────────────────────────────────
    # FETCH REAL GITHUB FOLLOWERS/FOLLOWING
    # ─────────────────────────────────────────
    def load_github_network(self, username: str, max_users: int = 10):
        print(f"\n[*] Fetching GitHub network for: {username}")

        # Fetch followers
        followers_url = f"https://api.github.com/users/{username}/followers?per_page={max_users}"
        followers_res = requests.get(followers_url, headers=self.headers, timeout=10)

        if followers_res.status_code == 200:
            for user in followers_res.json():
                follower = user["login"]
                self.graph.add_node(follower, platform="github", role="follower")
                self.graph.add_edge(follower, username, label="follows")
            print(f"[✓] Loaded {len(followers_res.json())} followers")
        else:
            print(f"[✗] Could not fetch followers")

        # Fetch following
        following_url = f"https://api.github.com/users/{username}/following?per_page={max_users}"
        following_res = requests.get(following_url, headers=self.headers, timeout=10)

        if following_res.status_code == 200:
            for user in following_res.json():
                followee = user["login"]
                self.graph.add_node(followee, platform="github", role="following")
                self.graph.add_edge(username, followee, label="follows")
            print(f"[✓] Loaded {len(following_res.json())} following")
        else:
            print(f"[✗] Could not fetch following")

        # Mark the target node
        self.graph.add_node(username, platform="github", role="target")
        print(f"[✓] Network built: {self.graph.number_of_nodes()} nodes, "
              f"{self.graph.number_of_edges()} edges")

    # ─────────────────────────────────────────
    # FETCH REAL REDDIT FRIENDS/CONNECTIONS
    # ─────────────────────────────────────────
    def load_reddit_network(self, username: str, max_posts: int = 10):
        print(f"\n[*] Fetching Reddit network for: {username}")

        # Get recent posts to find subreddits and interactions
        url = f"https://www.reddit.com/user/{username}/comments.json?limit={max_posts}"
        res = requests.get(url, headers=self.headers, timeout=10)

        if res.status_code != 200:
            print(f"[✗] Could not fetch Reddit activity")
            return

        self.graph.add_node(username, platform="reddit", role="target")
        interactions = {}

        for post in res.json().get("data", {}).get("children", []):
            data = post["data"]
            subreddit = f"r/{data.get('subreddit', 'unknown')}"
            parent_author = data.get("parent_id", "")

            # Link user to subreddits they are active in
            if subreddit not in self.graph:
                self.graph.add_node(subreddit, platform="reddit", role="subreddit")
            self.graph.add_edge(username, subreddit, label="active_in")

        print(f"[✓] Reddit network built: {self.graph.number_of_nodes()} nodes, "
              f"{self.graph.number_of_edges()} edges")

    # ─────────────────────────────────────────
    # DETECT SUSPECT CLUSTERS
    # ─────────────────────────────────────────
    def detect_suspect_clusters(self):
        print(f"\n[*] Detecting clusters...")
        clusters = list(nx.weakly_connected_components(self.graph))
        print(f"[✓] Found {len(clusters)} connected cluster(s)")
        for i, cluster in enumerate(clusters):
            print(f"    Cluster {i+1}: {len(cluster)} nodes → {', '.join(list(cluster)[:5])}{'...' if len(cluster) > 5 else ''}")
        return clusters

    # ─────────────────────────────────────────
    # STATIC GRAPH (saved as PNG)
    # ─────────────────────────────────────────
    def visualize(self, output_path=None):
        if not output_path:
            output_path = f"{self.output_dir}/network_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"

        if len(self.graph.nodes) == 0:
            print("[!] No nodes to visualize")
            return

        # Color nodes by role
        color_map = []
        for node in self.graph.nodes(data=True):
            role = node[1].get("role", "default")
            if role == "target":
                color_map.append("red")
            elif role == "follower":
                color_map.append("lightblue")
            elif role == "following":
                color_map.append("lightgreen")
            elif role == "subreddit":
                color_map.append("orange")
            else:
                color_map.append("grey")

        plt.figure(figsize=(20, 15))          # ← was (14, 10)
        pos = nx.spring_layout(self.graph, k=2.5, seed=42)   # ← k was 0.8, higher = more spread
        nx.draw(self.graph, pos,
                with_labels=True,
                node_color=color_map,
                node_size=2000,               # ← was 800
                font_size=10,                 # ← was 7
                arrows=True,
                edge_color="gray",
                arrowsize=20)                 # ← was 15

        # Legend
        legend = [
            mpatches.Patch(color="red",        label="Target Account"),
            mpatches.Patch(color="lightblue",  label="Follower"),
            mpatches.Patch(color="lightgreen", label="Following"),
            mpatches.Patch(color="orange",     label="Subreddit"),
            mpatches.Patch(color="grey",       label="Other"),
        ]
        plt.legend(handles=legend, loc="upper left")
        plt.title("Social Network Graph", fontsize=14)
        plt.savefig(output_path, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"[+] Static graph saved → {output_path}")

    # ─────────────────────────────────────────
    # INTERACTIVE GRAPH (saved as HTML)
    # ─────────────────────────────────────────
    def visualize_interactive(self, output_path=None):
        if not output_path:
            output_path = f"{self.output_dir}/network_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.html"

        net = Network(height="900px", width="100%", directed=True, notebook=False)
        net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=200, spring_strength=0.05)

        # Add nodes with bigger size
        for node, data in self.graph.nodes(data=True):
            role = data.get("role", "default")
            color = {"target": "#e74c3c", "follower": "#3498db",
                    "following": "#2ecc71", "subreddit": "#f39c12"}.get(role, "#95a5a6")
            size = 40 if role == "target" else 20
            net.add_node(node,
                        label=node,
                        color=color,
                        size=size,
                        font={"size": 16, "color": "#000000"},
                        title=f"Role: {role}\nUsername: {node}")

        # Add edges with labels
        for u, v, data in self.graph.edges(data=True):
            net.add_edge(u, v,
                        title=data.get("label", ""),
                        color="#aaaaaa",
                        width=2)

        # Enable physics controls panel
        net.show_buttons(filter_=["physics"])
        net.save_graph(output_path)
        print(f"[+] Interactive graph saved → {output_path}")
        print(f"[*] Open this file in your browser to explore the network")
    # ─────────────────────────────────────────
    # SAVE GRAPH DATA AS JSON
    # ─────────────────────────────────────────
    def save_graph_data(self, username: str):
        output_path = f"{self.output_dir}/graph_data_{username}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        data = {
            "target": username,
            "nodes": [{"id": n, **d} for n, d in self.graph.nodes(data=True)],
            "edges": [{"from": u, "to": v, "relation": d.get("label", "")}
                      for u, v, d in self.graph.edges(data=True)],
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
            "generated_at": datetime.datetime.utcnow().isoformat()
        }
        with open(output_path, "w") as f:
            json.dump(data, f, indent=4)
        print(f"[+] Graph data saved → {output_path}")