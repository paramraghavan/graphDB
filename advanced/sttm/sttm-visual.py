import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from pyvis.network import Network
import matplotlib.pyplot as plt
import random


class TableLineageVisualizer:
    def __init__(self, mapping_csv):
        """Initialize visualizer with mapping CSV file."""
        self.df = pd.read_csv(mapping_csv)
        self.G = self._create_graph()

    def _create_graph(self):
        """Create NetworkX graph from DataFrame."""
        G = nx.DiGraph()
        for _, row in self.df.iterrows():
            G.add_edge(row['Source Table'], row['Target Table'])
        return G

    def create_interactive_plotly(self, output_html='graph_plotly.html'):
        """Create interactive visualization using Plotly."""
        # Create layout using Kamada-Kawai algorithm
        pos = nx.kamada_kawai_layout(self.G)

        # Create edges
        edge_x = []
        edge_y = []
        for edge in self.G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=0.5, color='#888'),
            hoverinfo='none',
            mode='lines')

        # Create nodes
        node_x = []
        node_y = []
        for node in self.G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=[str(node) for node in self.G.nodes()],
            textposition="bottom center",
            marker=dict(
                showscale=True,
                colorscale='YlGnBu',
                size=20,
                colorbar=dict(
                    thickness=15,
                    title='Node Connections',
                    xanchor='left',
                    titleside='right'
                )
            ))

        # Color nodes by number of connections
        node_adjacencies = []
        for node in self.G.nodes():
            node_adjacencies.append(len(list(self.G.neighbors(node))))

        node_trace.marker.color = node_adjacencies

        # Create figure
        fig = go.Figure(data=[edge_trace, node_trace],
                        layout=go.Layout(
                            title='Table Lineage Graph',
                            showlegend=False,
                            hovermode='closest',
                            margin=dict(b=20, l=5, r=5, t=40),
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
                        )

        # Save to HTML file
        fig.write_html(output_html)
        return fig

    def create_pyvis_network(self, output_html='graph_pyvis.html'):
        """Create interactive visualization using PyVis."""
        net = Network(height='750px', width='100%', directed=True)

        # Add nodes with different colors for source and target
        sources = set(self.df['Source Table'])
        targets = set(self.df['Target Table'])

        for node in self.G.nodes():
            color = '#97c2fc' if node in sources else '#ff9999'  # Blue for source, Red for target
            net.add_node(node, label=node, color=color)

        # Add edges
        for edge in self.G.edges():
            net.add_edge(edge[0], edge[1])

        # Set physics layout
        net.set_options('''
        var options = {
          "physics": {
            "forceAtlas2Based": {
              "gravitationalConstant": -50,
              "centralGravity": 0.01,
              "springLength": 200,
              "springConstant": 0.08
            },
            "maxVelocity": 50,
            "solver": "forceAtlas2Based",
            "timestep": 0.35,
            "stabilization": {"iterations": 150}
          }
        }
        ''')

        # Save to HTML file
        net.show(output_html)

    def create_static_graph(self, output_file='graph_static.png'):
        """
        Create static visualization using NetworkX and Matplotlib.
        For increasing spacing b/w nodes horizontally and vertically
        Key spacing adjustments:

            For GraphViz layout:

            Added -Gnodesep=1.0 for vertical spacing
            Added -Granksep=2.0 for horizontal spacing
            Scale positions by 1.5 for additional spacing

            For custom layout:

            Increased horizontal_spacing to 2.5
            Increased vertical_spacing to 2.0

            General improvements:

            Increased figure size to (24, 16)
            Increased node size to 3000
            Increased margins to 0.3
            Added min_target_margin and min_source_margin for edge spacing
            Increased font size to 10

            To adjust the spacing further, you can:

            Increase the figure size (24, 16) for overall more space
            Adjust horizontal_spacing and vertical_spacing in the custom layout
            Modify -Gnodesep and -Granksep values in the GraphViz layout
            Change the scaling factor (1.5) in the GraphViz position adjustment
        """
        try:
            import pygraphviz
            from networkx.drawing.nx_agraph import graphviz_layout

            # Increase figure size for more spacing
            plt.figure(figsize=(24, 16))

            # Use dot layout with custom spacing parameters
            pos = graphviz_layout(self.G, prog='dot',
                                  args='-Grankdir=LR -Gnodesep=1.0 -Granksep=2.0')
            # nodesep: Minimum vertical space between nodes (higher value = more vertical spacing)
            # ranksep: Minimum horizontal space between ranks (higher value = more horizontal spacing)

            # Scale up the positions for even more spacing
            pos = {node: (x * 1.5, y * 1.5) for node, (x, y) in pos.items()}

        except ImportError:
            plt.figure(figsize=(24, 16))

            def get_hierarchy_pos(G):
                roots = [n for n in G.nodes() if G.in_degree(n) == 0]
                levels = {}
                for node in G.nodes():
                    max_level = 0
                    for root in roots:
                        try:
                            path_length = len(nx.shortest_path(G, root, node)) - 1
                            max_level = max(max_level, path_length)
                        except nx.NetworkXNoPath:
                            continue
                    levels[node] = max_level

                # Assign positions with increased spacing
                width = max(levels.values()) + 1
                height = len(G.nodes())
                pos = {}
                nodes_at_level = {}

                for node, level in levels.items():
                    if level not in nodes_at_level:
                        nodes_at_level[level] = []
                    nodes_at_level[level].append(node)

                # Increase these multipliers for more spacing
                horizontal_spacing = 2.5  # Increase for more horizontal space
                vertical_spacing = 2.0  # Increase for more vertical space

                for level in range(width):
                    nodes = nodes_at_level.get(level, [])
                    n_nodes = len(nodes)
                    for i, node in enumerate(nodes):
                        pos[node] = (
                            level * horizontal_spacing,  # Horizontal spacing
                            (i - (n_nodes - 1) / 2) * vertical_spacing  # Vertical spacing
                        )

                return pos

            pos = get_hierarchy_pos(self.G)

        # Draw with larger node sizes and spacing
        nx.draw_networkx_nodes(self.G, pos,
                               node_color='lightblue',
                               node_size=3000,  # Increased node size
                               alpha=0.7)

        # Draw edges with more curvature to avoid overlap
        nx.draw_networkx_edges(self.G, pos,
                               edge_color='gray',
                               arrows=True,
                               arrowsize=20,
                               connectionstyle='arc3,rad=0.2',
                               min_target_margin=30,  # Space between edge and node
                               min_source_margin=30)  # Space between edge and node

        # Add labels with adjusted font size
        nx.draw_networkx_labels(self.G, pos,
                                font_size=10,  # Increased font size
                                font_weight='bold')

        plt.title("Table Lineage Graph")
        # Increase margins for more space around the graph
        plt.margins(x=0.3, y=0.3)
        plt.axis('off')
        plt.tight_layout()

        # Save with higher DPI for better quality
        plt.savefig(output_file, format='png', dpi=300, bbox_inches='tight')
        plt.close()

    def create_static_graph3(self, output_file='graph_static.png'):
        """Create static visualization using NetworkX and Matplotlib."""
        # Make figure wider than tall for left-to-right layout
        plt.figure(figsize=(20, 8))

        def assign_horizontal_layers(G):
            """Assign layers based on longest path from source nodes."""
            layers = {}
            # Start with nodes that have no predecessors (source/parent nodes)
            sources = [n for n in G.nodes() if G.in_degree(n) == 0]

            # Use topological sort to ensure parent nodes are processed before children
            for node in nx.topological_sort(G):
                if node in sources:
                    layers[node] = 0
                else:
                    # Place node one layer to the right of its leftmost parent
                    predecessors = list(G.predecessors(node))
                    max_parent_layer = max(layers[parent] for parent in predecessors)
                    layers[node] = max_parent_layer + 1
            return layers

        # Assign layers to nodes
        try:
            layers = assign_horizontal_layers(self.G)
            for node, layer in layers.items():
                self.G.nodes[node]['layer'] = layer

            # Use multipartite layout with increased spacing
            pos = nx.multipartite_layout(self.G,
                                         subset_key='layer',
                                         scale=3.0,
                                         align='horizontal')  # Left to right

            # Draw nodes
            nx.draw_networkx_nodes(self.G, pos,
                                   node_color='lightblue',
                                   node_size=2000,
                                   alpha=0.7)

            # Draw edges with slight curve for better visibility
            nx.draw_networkx_edges(self.G, pos,
                                   edge_color='gray',
                                   arrows=True,
                                   arrowsize=20,
                                   connectionstyle='arc3,rad=0.2')

            # Add labels
            nx.draw_networkx_labels(self.G, pos,
                                    font_size=8,
                                    font_weight='bold')

            plt.title("Table Lineage Graph")
            plt.margins(x=0.2, y=0.2)
            plt.axis('off')
            plt.tight_layout()

            # Save to file
            plt.savefig(output_file, format='png', dpi=300, bbox_inches='tight')
            plt.close()

        except nx.NetworkXUnfeasible:
            print("Error: Graph contains cycles. Cannot create a hierarchical layout.")
            plt.close()

    def create_static_graph2(self, output_file='graph_static.png'):
        """Create static visualization using NetworkX and Matplotlib."""
        plt.figure(figsize=(15, 10))

        # Assign layers based on distance from source nodes
        def assign_layers(G):
            layers = {}
            # Find source nodes (nodes with no incoming edges)
            sources = [n for n in G.nodes() if G.in_degree(n) == 0]

            # Assign layers using BFS
            for source in sources:
                for node in nx.bfs_tree(G, source):
                    # Get max distance from any source
                    dist = max([nx.shortest_path_length(G, s, node)
                                for s in sources if nx.has_path(G, s, node)])
                    layers[node] = dist
            return layers

        # Assign layers to nodes
        layers = assign_layers(self.G)
        for node, layer in layers.items():
            self.G.nodes[node]['layer'] = layer

        # Use multipartite layout for left-to-right arrangement
        pos = nx.multipartite_layout(self.G,
                                     subset_key='layer',
                                     scale=2.0,
                                     align='horizontal')  # Left to right

        # Draw nodes
        nx.draw_networkx_nodes(self.G, pos,
                               node_color='lightblue',
                               node_size=2000,
                               alpha=0.7)

        # Draw edges
        nx.draw_networkx_edges(self.G, pos,
                               edge_color='gray',
                               arrows=True,
                               arrowsize=20)

        # Add labels
        nx.draw_networkx_labels(self.G, pos,
                                font_size=8,
                                font_weight='bold')

        plt.title("Table Lineage Graph")
        plt.margins(0.2)  # Add some padding around the graph
        plt.axis('off')
        plt.tight_layout()

        # Save to file
        plt.savefig(output_file, format='png', dpi=300, bbox_inches='tight')
        plt.close()

    def create_static_graph1(self, output_file='graph_static.png'):
        """Create static visualization using NetworkX and Matplotlib."""
        plt.figure(figsize=(15, 10))

        # Use hierarchical layout
        pos = nx.spring_layout(self.G, k=1, iterations=50)


        # Draw nodes
        nx.draw_networkx_nodes(self.G, pos,
                               node_color='lightblue',
                               node_size=2000,
                               alpha=0.7)

        # Draw edges
        nx.draw_networkx_edges(self.G, pos,
                               edge_color='gray',
                               arrows=True,
                               arrowsize=20)

        # Add labels
        nx.draw_networkx_labels(self.G, pos,
                                font_size=8,
                                font_weight='bold')

        plt.title("Table Lineage Graph")
        plt.axis('off')
        plt.tight_layout()

        # Save to file
        plt.savefig(output_file, format='png', dpi=300, bbox_inches='tight')
        plt.close()


# Example usage
def main():
    # Create sample mapping data
    sample_data = pd.DataFrame({
        'Source Table': ['database1.table1', 'database1.table2', 'database2.table1', 'database3.table1'],
        'Target Table': ['database4.target1', 'database4.target1', 'database4.target2', 'database4.target2']
    })
    sample_data.to_csv('sample_mapping.csv', index=False)

    # Create visualizer
    visualizer = TableLineageVisualizer('sample_mapping.csv')

    # Generate all three types of visualizations
    visualizer.create_interactive_plotly()
    # problem with pyvis
    # visualizer.create_pyvis_network()
    visualizer.create_static_graph()


if __name__ == "__main__":
    main()