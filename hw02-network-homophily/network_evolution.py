import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from collections import defaultdict
import math
import platform
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent / "results"

# 解决mac系统字体兼容性问题
if platform.system() == 'Darwin':  # macOS
    plt.rcParams['font.family'] = ['Arial Unicode MS', 'Heiti TC', 'Hiragino Sans GB']
    plt.rcParams['axes.unicode_minus'] = False

class NetworkEvolution:
    def __init__(self):
        # Initial social network (adjacency matrix)
        self.social_network = np.array([
            [0, 1, 0, 1, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [1, 0, 0, 0, 0, 1, 1, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 0, 0, 1, 0, 1],
            [0, 0, 0, 1, 0, 0, 0, 1, 0, 1],
            [0, 0, 0, 0, 0, 1, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 1],
            [0, 0, 0, 0, 0, 1, 1, 0, 1, 0]
        ])

        # Initial club affiliations (each row represents Pi's participation in Cj clubs)
        self.club_affiliations = np.array([
            [1, 0],
            [1, 1],
            [0, 1],
            [0, 1],
            [0, 1],
            [1, 0],
            [0, 0],
            [0, 0],
            [0, 0],
            [0, 0]
        ])

        self.num_people = 10
        self.num_clubs = 2

        # Threshold values
        self.friendship_threshold = 3  # common friends needed for new friendship
        self.club_friendship_threshold = 2  # common clubs needed for new friendship
        self.club_participation_threshold = 2  # friends in club needed to join

    def get_common_friends(self, i, j):
        """Calculate number of common friends between person i and j"""
        if i == j:
            return 0

        # Find friends of i and j
        friends_i = set(np.where(self.social_network[i] == 1)[0])
        friends_j = set(np.where(self.social_network[j] == 1)[0])

        # Exclude i and j themselves
        friends_i.discard(j)
        friends_j.discard(i)

        return len(friends_i.intersection(friends_j))

    def get_common_clubs(self, i, j):
        """Calculate number of common clubs between person i and j"""
        if i == j:
            return 0

        clubs_i = set(np.where(self.club_affiliations[i] == 1)[0])
        clubs_j = set(np.where(self.club_affiliations[j] == 1)[0])

        return len(clubs_i.intersection(clubs_j))

    def get_friends_in_club(self, person, club):
        """Calculate number of friends in a specific club"""
        friends = np.where(self.social_network[person] == 1)[0]
        count = 0
        for friend in friends:
            if self.club_affiliations[friend, club] == 1:
                count += 1
        return count

    def closure_mechanism_1(self):
        """Friendship closure: if two people have 3+ common friends, they become friends"""
        new_edges = []
        # Collect all potential new edges first to avoid interference
        potential_edges = []
        for i in range(self.num_people):
            for j in range(i + 1, self.num_people):
                if self.social_network[i, j] == 0:  # Not already friends
                    common_friends = self.get_common_friends(i, j)
                    if common_friends >= self.friendship_threshold:
                        potential_edges.append((i, j))

        # Apply all changes at once
        for i, j in potential_edges:
            self.social_network[i, j] = 1
            self.social_network[j, i] = 1
            new_edges.append((i, j))

        return new_edges

    def closure_mechanism_2(self):
        """Club closure: if two people participate in 2+ common clubs, they become friends"""
        new_edges = []
        # Collect all potential new edges first to avoid interference
        potential_edges = []
        for i in range(self.num_people):
            for j in range(i + 1, self.num_people):
                if self.social_network[i, j] == 0:  # Not already friends
                    common_clubs = self.get_common_clubs(i, j)
                    if common_clubs >= self.club_friendship_threshold:
                        potential_edges.append((i, j))

        # Apply all changes at once
        for i, j in potential_edges:
            self.social_network[i, j] = 1
            self.social_network[j, i] = 1
            new_edges.append((i, j))

        return new_edges

    def closure_mechanism_3(self):
        """Club participation: if person has 2+ friends in a club, they join the club"""
        new_participations = []
        # Collect all potential new participations first to avoid interference
        potential_participations = []
        for person in range(self.num_people):
            for club in range(self.num_clubs):
                if self.club_affiliations[person, club] == 0:  # Not already in club
                    friends_in_club = self.get_friends_in_club(person, club)
                    if friends_in_club >= self.club_participation_threshold:
                        potential_participations.append((person, club))

        # Apply all changes at once
        for person, club in potential_participations:
            self.club_affiliations[person, club] = 1
            new_participations.append((person, club))

        return new_participations

    def calculate_homophily_measures(self):
        """Calculate professional homophily measures: E-I index and Modularity Q"""
        # Define 4-value club participation patterns: 0=无, 1=C1 only, 2=C2 only, 3=C1+C2
        patterns = []
        for i in range(self.num_people):
            if self.club_affiliations[i, 0] == 0 and self.club_affiliations[i, 1] == 0:
                patterns.append(0)  # 无俱乐部
            elif self.club_affiliations[i, 0] == 1 and self.club_affiliations[i, 1] == 0:
                patterns.append(1)  # 仅C1
            elif self.club_affiliations[i, 0] == 0 and self.club_affiliations[i, 1] == 1:
                patterns.append(2)  # 仅C2
            else:
                patterns.append(3)  # C1+C2

        # Step 1: Count internal and external edges
        L_internal = 0  # Edges within same category
        L_external = 0  # Edges between different categories

        for i in range(self.num_people):
            for j in range(i + 1, self.num_people):
                if self.social_network[i, j] == 1:
                    if patterns[i] == patterns[j]:
                        L_internal += 1
                    else:
                        L_external += 1

        total_edges = L_internal + L_external

        if total_edges == 0:
            return {
                'simple_homophily': 0.0,
                'ei_index': 0.0,
                'modularity_q': 0.0,
                'internal_edges': 0,
                'external_edges': 0,
                'total_edges': 0
            }

        # Step 2: Calculate E-I index
        ei_index = (L_external - L_internal) / total_edges

        # Step 3: Calculate simple homophily (original method)
        simple_homophily = L_internal / total_edges

        # Step 4: Calculate Newman's Modularity Q
        # Build mixing matrix
        mixing_matrix = np.zeros((4, 4))

        for i in range(self.num_people):
            for j in range(i + 1, self.num_people):
                if self.social_network[i, j] == 1:
                    mixing_matrix[patterns[i], patterns[j]] += 1
                    mixing_matrix[patterns[j], patterns[i]] += 1

        # Calculate expected edges under random connection
        total_edges = mixing_matrix.sum() / 2  # Divide by 2 since matrix is symmetric

        # Calculate degree distribution for each category
        category_sizes = [patterns.count(c) for c in range(4)]

        # Calculate expected edges if connections were random
        expected_matrix = np.zeros((4, 4))
        for i in range(4):
            for j in range(4):
                if i == j:
                    # Same category: n_i choose 2
                    n_i = category_sizes[i]
                    if n_i >= 2:
                        expected_matrix[i, j] = (n_i * (n_i - 1)) / 2
                else:
                    # Different categories: n_i * n_j
                    n_i = category_sizes[i]
                    n_j = category_sizes[j]
                    expected_matrix[i, j] = n_i * n_j

        # Normalize expected matrix to match total edges
        expected_total = expected_matrix.sum() / 2
        if expected_total > 0:
            expected_matrix = expected_matrix * (total_edges / expected_total)

        # Calculate modularity Q
        modularity_q = 0.0
        for i in range(4):
            actual_internal = mixing_matrix[i, i] / 2  # Divide by 2 for undirected edges
            expected_internal = expected_matrix[i, i] / 2

            if total_edges > 0:
                modularity_q += (actual_internal - expected_internal) / total_edges

        return {
            'simple_homophily': simple_homophily,
            'ei_index': ei_index,
            'modularity_q': modularity_q,
            'internal_edges': L_internal,
            'external_edges': L_external,
            'total_edges': total_edges
        }

    def visualize_network(self, step, new_edges=None):
        """Create an optimized network visualization with clear edges and edge legends"""
        G = nx.Graph()

        # Add person nodes with club participation attributes
        for i in range(self.num_people):
            club_pattern = "none"
            if self.club_affiliations[i, 0] == 1 and self.club_affiliations[i, 1] == 0:
                club_pattern = "C1"
            elif self.club_affiliations[i, 0] == 0 and self.club_affiliations[i, 1] == 1:
                club_pattern = "C2"
            elif self.club_affiliations[i, 0] == 1 and self.club_affiliations[i, 1] == 1:
                club_pattern = "C1+C2"

            G.add_node(i, club=club_pattern, type="person")

        # Add club nodes
        G.add_node("C1", type="club", club="C1")
        G.add_node("C2", type="club", club="C2")

        # Add friendship edges
        for i in range(self.num_people):
            for j in range(i + 1, self.num_people):
                if self.social_network[i, j] == 1:
                    G.add_edge(i, j, type="friendship")

        # Add club membership edges
        for i in range(self.num_people):
            if self.club_affiliations[i, 0] == 1:
                G.add_edge(i, "C1", type="membership")
            if self.club_affiliations[i, 1] == 1:
                G.add_edge(i, "C2", type="membership")

        # Track new membership edges (for step > 0)
        new_membership_edges = []
        if step > 0 and hasattr(self, 'previous_club_affiliations'):
            for i in range(self.num_people):
                # Check for new C1 membership
                if (self.club_affiliations[i, 0] == 1 and
                    self.previous_club_affiliations[i, 0] == 0):
                    new_membership_edges.append((i, "C1"))
                # Check for new C2 membership
                if (self.club_affiliations[i, 1] == 1 and
                    self.previous_club_affiliations[i, 1] == 0):
                    new_membership_edges.append((i, "C2"))

        # Create visualization with optimized layout
        plt.figure(figsize=(14, 10))

        # Define optimized positions for clear visualization
        pos = {}

        # Position club nodes at the top with good spacing
        pos["C1"] = (0.3, 0.95)
        pos["C2"] = (0.7, 0.95)

        # Position person nodes in two rows with vertical separation for better edge visibility
        # First row: P1-P5 (staggered vertically)
        for i in range(5):
            # Alternate between slightly higher and lower positions
            y_offset = 0.1 if i % 2 == 0 else -0.1
            pos[i] = (0.1 + i * 0.2, 0.7 + y_offset)

        # Second row: P6-P10 (staggered vertically)
        for i in range(5, 10):
            # Alternate between slightly higher and lower positions
            y_offset = 0.1 if (i-5) % 2 == 0 else -0.1
            pos[i] = (0.1 + (i-5) * 0.2, 0.3 + y_offset)

        # Define node colors and sizes based on type
        node_colors = []
        node_sizes = []
        for node in G.nodes():
            if isinstance(node, str) and node.startswith("C"):
                # Club nodes
                if node == "C1":
                    node_colors.append('blue')
                else:
                    node_colors.append('green')
                node_sizes.append(1000)  # Larger club nodes
            else:
                # Person nodes
                i = node
                if self.club_affiliations[i, 0] == 1 and self.club_affiliations[i, 1] == 0:
                    node_colors.append('lightblue')  # C1 only
                elif self.club_affiliations[i, 0] == 0 and self.club_affiliations[i, 1] == 1:
                    node_colors.append('lightgreen')  # C2 only
                elif self.club_affiliations[i, 0] == 1 and self.club_affiliations[i, 1] == 1:
                    node_colors.append('orange')  # C1+C2
                else:
                    node_colors.append('lightgray')  # No clubs
                node_sizes.append(600)  # Larger person nodes

        # Draw the network with optimized edge styles
        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_sizes,
                              edgecolors='black', linewidths=1)

        # Draw friendship edges (solid blue lines)
        friendship_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('type') == 'friendship']
        nx.draw_networkx_edges(G, pos, edgelist=friendship_edges,
                              edge_color='blue', width=2, alpha=0.7)

        # Draw membership edges (dashed red lines)
        membership_edges = [(u, v) for u, v, d in G.edges(data=True) if d.get('type') == 'membership']
        nx.draw_networkx_edges(G, pos, edgelist=membership_edges,
                              edge_color='red', width=2, style='dashed', alpha=0.7)

        # Highlight new friendship edges in bold green
        if new_edges:
            new_edge_list = [(i, j) for i, j in new_edges]
            nx.draw_networkx_edges(G, pos, edgelist=new_edge_list,
                                  edge_color='green', width=4, alpha=0.9)

        # Highlight new membership edges in bold orange (dashed style)
        if new_membership_edges:
            nx.draw_networkx_edges(G, pos, edgelist=new_membership_edges,
                                  edge_color='orange', width=4, style='dashed', alpha=0.9)

        # Add clear labels with better formatting
        labels = {}
        for node in G.nodes():
            if isinstance(node, str) and node.startswith("C"):
                labels[node] = node
            else:
                labels[node] = f"P{node+1}"
        nx.draw_networkx_labels(G, pos, labels, font_size=12, font_weight='bold')

        # Add edge labels for better clarity
        edge_labels = {}
        for u, v, d in G.edges(data=True):
            if d.get('type') == 'friendship':
                edge_labels[(u, v)] = "Friendship"
            elif d.get('type') == 'membership':
                edge_labels[(u, v)] = "Membership"

        # Only label a few edges to avoid clutter
        if len(edge_labels) > 0:
            # Label first few edges of each type
            labeled_edges = list(edge_labels.keys())[:min(3, len(edge_labels))]
            nx.draw_networkx_edge_labels(G, pos,
                                       edge_labels={k: v for k, v in edge_labels.items() if k in labeled_edges},
                                       font_size=8, font_color='darkblue')

        # Calculate homophily measures
        homophily_measures = self.calculate_homophily_measures()

        plt.title(f"Network Evolution - Step {step}\n"
                 f"Simple Homophily: {homophily_measures['simple_homophily']:.3f} | "
                 f"E-I Index: {homophily_measures['ei_index']:.3f} | "
                 f"Modularity Q: {homophily_measures['modularity_q']:.3f}",
                 fontsize=12, fontweight='bold')
        plt.axis('off')

        # Enhanced legend with edge styles
        from matplotlib.patches import Patch
        from matplotlib.lines import Line2D

        legend_elements = [
            # Node legends
            Patch(facecolor='lightgray', label='No clubs'),
            Patch(facecolor='lightblue', label='C1 only'),
            Patch(facecolor='lightgreen', label='C2 only'),
            Patch(facecolor='orange', label='C1+C2'),
            Patch(facecolor='blue', label='C1 Club'),
            Patch(facecolor='green', label='C2 Club'),

            # Edge legends
            Line2D([0], [0], color='blue', lw=2, label='Friendship'),
            Line2D([0], [0], color='red', lw=2, linestyle='--', label='Membership'),
            Line2D([0], [0], color='green', lw=4, label='New Friendship'),
            Line2D([0], [0], color='orange', lw=4, label='New Membership')
        ]

        plt.legend(handles=legend_elements, loc='upper right',
                  bbox_to_anchor=(1.0, 1.0), fontsize=10)

        plt.tight_layout()

        # Save the figure alongside the assignment's recorded results.
        OUTPUT_DIR.mkdir(exist_ok=True)
        filename = OUTPUT_DIR / f"network_step_{step}.png"
        plt.savefig(filename, dpi=300, bbox_inches='tight', facecolor='white')
        print(f"Network visualization saved as: {filename}")

        # Also show the plot
        plt.show()

    def run_evolution(self, max_steps=10):
        """Run the network evolution process"""
        print("Initial Network:")
        print("Social Network (adjacency matrix):")
        print(self.social_network)
        print("\nClub Affiliations:")
        print(self.club_affiliations)

        # Calculate initial homophily measures BEFORE any evolution
        initial_measures = self.calculate_homophily_measures()
        print(f"\nInitial Homophily Measures:")
        print(f"  Simple Homophily: {initial_measures['simple_homophily']:.3f}")
        print(f"  E-I Index: {initial_measures['ei_index']:.3f}")
        print(f"  Modularity Q: {initial_measures['modularity_q']:.3f}")
        print(f"  Internal Edges: {initial_measures['internal_edges']}")
        print(f"  External Edges: {initial_measures['external_edges']}")
        print(f"  Total Edges: {initial_measures['total_edges']}")

        # Store initial club affiliations for tracking new memberships
        self.previous_club_affiliations = self.club_affiliations.copy()

        # Step 0: Show initial network state
        print(f"\n{'='*50}")
        print("Step 0: Initial State")
        print('='*50)
        print("No evolution applied yet")
        print(f"Homophily measures: Simple={initial_measures['simple_homophily']:.3f}, "
              f"E-I={initial_measures['ei_index']:.3f}, Q={initial_measures['modularity_q']:.3f}")

        # Visualize initial network (step 0)
        self.visualize_network(0)

        for step in range(1, max_steps + 1):
            print(f"\n{'='*50}")
            print(f"Step {step}:")
            print('='*50)

            # Store state before evolution for comparison
            social_before = self.social_network.copy()
            clubs_before = self.club_affiliations.copy()

            # Calculate homophily measures BEFORE applying closure mechanisms
            measures_before = self.calculate_homophily_measures()
            print(f"Homophily before evolution:")
            print(f"  Simple Homophily: {measures_before['simple_homophily']:.3f}")
            print(f"  E-I Index: {measures_before['ei_index']:.3f}")
            print(f"  Modularity Q: {measures_before['modularity_q']:.3f}")

            # Apply closure mechanisms (each mechanism considers the state at the beginning of the step)
            new_edges_1 = self.closure_mechanism_1()
            new_edges_2 = self.closure_mechanism_2()
            new_participations = self.closure_mechanism_3()

            # Combine all new edges
            all_new_edges = new_edges_1 + new_edges_2

            # Calculate homophily measures AFTER applying closure mechanisms
            measures_after = self.calculate_homophily_measures()

            # Store current club affiliations for next step comparison
            self.previous_club_affiliations = clubs_before.copy()  # Use state before this step

            # Print results
            if all_new_edges:
                print(f"New friendships formed: {[(i+1, j+1) for i, j in all_new_edges]}")
            else:
                print("No new friendships formed")

            if new_participations:
                print(f"New club participations: {[(i+1, j+1) for i, j in new_participations]}")
            else:
                print("No new club participations")

            print(f"Homophily after evolution:")
            print(f"  Simple Homophily: {measures_after['simple_homophily']:.3f}")
            print(f"  E-I Index: {measures_after['ei_index']:.3f}")
            print(f"  Modularity Q: {measures_after['modularity_q']:.3f}")
            print(f"Homophily changes:")
            print(f"  Simple: {measures_after['simple_homophily'] - measures_before['simple_homophily']:+.3f}")
            print(f"  E-I: {measures_after['ei_index'] - measures_before['ei_index']:+.3f}")
            print(f"  Q: {measures_after['modularity_q'] - measures_before['modularity_q']:+.3f}")

            # Visualize the network with optimized layout
            self.visualize_network(step, all_new_edges)

            # Check if no changes occurred (convergence)
            if not all_new_edges and not new_participations:
                print(f"\nNetwork converged at step {step}")
                break

        print(f"\n{'='*50}")
        print("Final Network State:")
        print('='*50)
        print("Social Network (adjacency matrix):")
        print(self.social_network)
        print("\nClub Affiliations:")
        print(self.club_affiliations)

        final_measures = self.calculate_homophily_measures()
        print(f"\nFinal Homophily Measures:")
        print(f"  Simple Homophily: {final_measures['simple_homophily']:.3f}")
        print(f"  E-I Index: {final_measures['ei_index']:.3f}")
        print(f"  Modularity Q: {final_measures['modularity_q']:.3f}")
        print(f"Total Homophily Changes:")
        print(f"  Simple: {final_measures['simple_homophily'] - initial_measures['simple_homophily']:+.3f}")
        print(f"  E-I: {final_measures['ei_index'] - initial_measures['ei_index']:+.3f}")
        print(f"  Q: {final_measures['modularity_q'] - initial_measures['modularity_q']:+.3f}")

# Run the simulation
if __name__ == "__main__":
    network = NetworkEvolution()
    network.run_evolution(max_steps=10)
