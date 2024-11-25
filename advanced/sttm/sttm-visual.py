import pandas as pd
import networkx as nx
import plotly.graph_objects as go
from pyvis.network import Network
import matplotlib.pyplot as plt


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

    def _get_hierarchical_layout(self):
        """Create hierarchical layout with sources on left and targets on right."""
        # Identify source and target nodes
        sources = set(self.df['Source Table'])
        targets = set(self.df['Target Table']) - sources

        # Create positions dictionary
        pos = {}

        # Position source nodes on the left
        source_y_spacing = 1.0 / (len(sources) + 1)
        for i, source in enumerate(sorted(sources), 1):
            pos[source] = (-1, i * source_y_spacing)

        # Position target nodes on the right
        target_y_spacing = 1.0 / (len(targets) + 1)
        for i, target in enumerate(sorted(targets), 1):
            pos[target] = (1, i * target_y_spacing)

        return pos

    def create_interactive_plotly(self, output_html='graph_plotly.html'):
        """Create interactive visualization using Plotly with improved layout."""
        pos = self._get_hierarchical_layout()

        # Create edges with curved paths
        edge_x = []
        edge_y = []
        for edge in self.G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]

            # Create curved path
            cx = (x0 + x1) / 2  # Control point x
            edge_x.extend([x0, cx, x1, None])
            edge_y.extend([y0, (y0 + y1) / 2, y1, None])

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines'
        )

        # Create nodes
        node_x = []
        node_y = []
        node_text = []
        node_colors = []

        for node in self.G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)

            # Format node text: split database and table name
            db, table = node.split('.')
            node_text.append(f"{db}<br>{table}")

            # Color nodes based on type (source or target)
            color = '#1f77b4' if x < 0 else '#ff7f0e'  # Blue for source, Orange for target
            node_colors.append(color)

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition="middle right" if any(x < 0 for x in node_x) else "middle left",
            marker=dict(
                size=30,
                color=node_colors,
                line=dict(width=2, color='white')
            )
        )

        # Create figure with improved layout
        fig = go.Figure(
            data=[edge_trace, node_trace],
            layout=go.Layout(
                title=dict(
                    text='Table Lineage Graph',
                    x=0.5,
                    y=0.95,
                    font=dict(size=20)
                ),
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                plot_bgcolor='white',
                xaxis=dict(
                    showgrid=False,
                    zeroline=False,
                    showticklabels=False,
                    range=[-1.2, 1.2]
                ),
                yaxis=dict(
                    showgrid=False,
                    zeroline=False,
                    showticklabels=False,
                    range=[-0.1, 1.1]
                ),
                height=600
            )
        )

        # Save to HTML file
        fig.write_html(output_html)
        return fig

    def create_static_graph(self, output_file='graph_static.png'):
        """Create static visualization using NetworkX and Matplotlib with improved layout."""
        plt.figure(figsize=(12, 8))
        pos = self._get_hierarchical_layout()

        # Draw edges with curved arrows
        nx.draw_networkx_edges(
            self.G, pos,
            edge_color='gray',
            arrows=True,
            arrowsize=20,
            connectionstyle='arc3,rad=0.2'
        )

        # Draw source nodes
        sources = set(self.df['Source Table'])
        nx.draw_networkx_nodes(
            self.G, pos,
            nodelist=sources,
            node_color='lightblue',
            node_size=2000,
            alpha=0.7
        )

        # Draw target nodes
        targets = set(self.df['Target Table']) - sources
        nx.draw_networkx_nodes(
            self.G, pos,
            nodelist=targets,
            node_color='lightcoral',
            node_size=2000,
            alpha=0.7
        )

        # Add labels with improved formatting
        labels = {}
        for node in self.G.nodes():
            db, table = node.split('.')
            labels[node] = f"{db}\n{table}"

        nx.draw_networkx_labels(
            self.G, pos,
            labels=labels,
            font_size=8,
            font_weight='bold'
        )

        plt.title("Table Lineage Graph", pad=20, size=16)
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

    # Create visualizer and generate visualizations
    visualizer = TableLineageVisualizer('sample_mapping.csv')
    visualizer.create_interactive_plotly()
    visualizer.create_static_graph()


if __name__ == "__main__":
    main()