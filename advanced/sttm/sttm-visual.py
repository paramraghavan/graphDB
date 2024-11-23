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