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
        self._organize_databases()

    def _create_graph(self):
        """Create NetworkX graph from DataFrame."""
        G = nx.DiGraph()
        for _, row in self.df.iterrows():
            G.add_edge(row['Source Table'], row['Target Table'])
        return G

    def _organize_databases(self):
        """Organize tables by database and create swim lanes."""
        # Extract unique databases
        self.source_dbs = sorted(set(table.split('.')[0] for table in self.df['Source Table']))
        self.target_dbs = sorted(set(table.split('.')[0] for table in self.df['Target Table']))

        # Create mapping of tables to their databases
        self.db_tables = {}
        for table in self.G.nodes():
            db = table.split('.')[0]
            if db not in self.db_tables:
                self.db_tables[db] = []
            self.db_tables[db].append(table)

        # Sort tables within each database
        for db in self.db_tables:
            self.db_tables[db] = sorted(self.db_tables[db])

    def _get_swimlane_layout(self):
        """Create layout with swim lanes based on databases."""
        pos = {}

        # Calculate total number of databases and spacing
        total_dbs = len(self.source_dbs) + len(self.target_dbs)
        db_height = 1.0 / total_dbs

        # Position source database lanes on the left
        for i, db in enumerate(self.source_dbs):
            tables = self.db_tables[db]
            table_spacing = db_height / (len(tables) + 1)
            lane_y = i * db_height

            # Position tables within the database lane
            for j, table in enumerate(tables, 1):
                pos[table] = (-1, lane_y + j * table_spacing)

        # Position target database lanes on the right
        for i, db in enumerate(self.target_dbs):
            tables = self.db_tables[db]
            table_spacing = db_height / (len(tables) + 1)
            lane_y = i * db_height

            # Position tables within the database lane
            for j, table in enumerate(tables, 1):
                pos[table] = (1, lane_y + j * table_spacing)

        return pos

    def create_interactive_plotly(self, output_html='graph_plotly.html'):
        """Create interactive visualization using Plotly with swim lanes."""
        pos = self._get_swimlane_layout()

        # Create figure with larger size
        fig = go.Figure()

        # Add swim lane backgrounds
        total_dbs = len(self.source_dbs) + len(self.target_dbs)
        db_height = 1.0 / total_dbs

        # Add source database swim lanes
        for i, db in enumerate(self.source_dbs):
            fig.add_shape(
                type="rect",
                x0=-1.2,
                x1=-0.8,
                y0=i * db_height,
                y1=(i + 1) * db_height,
                fillcolor="rgba(230, 240, 255, 0.5)",
                line=dict(color="rgba(0, 0, 0, 0.1)"),
                layer="below"
            )
            # Add database label
            fig.add_annotation(
                x=-1.3,
                y=(i + 0.5) * db_height,
                text=db,
                showarrow=False,
                textangle=-90,
                font=dict(size=12)
            )

        # Add target database swim lanes
        for i, db in enumerate(self.target_dbs):
            fig.add_shape(
                type="rect",
                x0=0.8,
                x1=1.2,
                y0=i * db_height,
                y1=(i + 1) * db_height,
                fillcolor="rgba(255, 240, 230, 0.5)",
                line=dict(color="rgba(0, 0, 0, 0.1)"),
                layer="below"
            )
            # Add database label
            fig.add_annotation(
                x=1.3,
                y=(i + 0.5) * db_height,
                text=db,
                showarrow=False,
                textangle=90,
                font=dict(size=12)
            )

        # Create edges with curved paths
        for edge in self.G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]

            fig.add_trace(go.Scatter(
                x=[x0, (x0 + x1) / 2, x1],
                y=[y0, (y0 + y1) / 2, y1],
                mode='lines',
                line=dict(color='rgba(136, 136, 136, 0.5)', width=1),
                hoverinfo='none'
            ))

        # Create nodes
        for node in self.G.nodes():
            x, y = pos[node]
            db, table = node.split('.')

            # Different colors and positions for source and target nodes
            is_source = x < 0
            color = '#1f77b4' if is_source else '#ff7f0e'
            text_pos = 'middle right' if is_source else 'middle left'

            fig.add_trace(go.Scatter(
                x=[x],
                y=[y],
                mode='markers+text',
                marker=dict(size=30, color=color, line=dict(width=2, color='white')),
                text=table,  # Show only table name
                textposition=text_pos,
                hovertext=f"{db}.{table}",  # Show full name on hover
                hoverinfo='text'
            ))

        # Update layout
        fig.update_layout(
            title=dict(
                text='Table Lineage Graph',
                x=0.5,
                y=0.95,
                font=dict(size=20)
            ),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=20, l=100, r=100, t=40),
            plot_bgcolor='white',
            xaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                range=[-1.5, 1.5]
            ),
            yaxis=dict(
                showgrid=False,
                zeroline=False,
                showticklabels=False,
                range=[-0.1, 1.1]
            ),
            height=800,
            width=1200
        )

        # Save to HTML file
        fig.write_html(output_html)
        return fig

    def create_static_graph(self, output_file='graph_static.png'):
        """Create static visualization using NetworkX and Matplotlib with swim lanes."""
        plt.figure(figsize=(15, 10))
        pos = self._get_swimlane_layout()

        # Draw swim lanes
        total_dbs = len(self.source_dbs) + len(self.target_dbs)
        db_height = 1.0 / total_dbs

        # Draw source database swim lanes
        for i, db in enumerate(self.source_dbs):
            plt.axhspan(i * db_height, (i + 1) * db_height,
                        xmin=0.1, xmax=0.45,
                        color='lightblue', alpha=0.2)
            plt.text(-1.4, (i + 0.5) * db_height, db,
                     rotation=90, verticalalignment='center')

        # Draw target database swim lanes
        for i, db in enumerate(self.target_dbs):
            plt.axhspan(i * db_height, (i + 1) * db_height,
                        xmin=0.55, xmax=0.9,
                        color='lightcoral', alpha=0.2)
            plt.text(1.4, (i + 0.5) * db_height, db,
                     rotation=-90, verticalalignment='center')

        # Draw edges with curved arrows
        nx.draw_networkx_edges(
            self.G, pos,
            edge_color='gray',
            arrows=True,
            arrowsize=20,
            connectionstyle='arc3,rad=0.2',
            alpha=0.5
        )

        # Draw nodes
        sources = set(self.df['Source Table'])
        nx.draw_networkx_nodes(
            self.G, pos,
            nodelist=sources,
            node_color='lightblue',
            node_size=2000,
            alpha=0.7
        )

        targets = set(self.df['Target Table']) - sources
        nx.draw_networkx_nodes(
            self.G, pos,
            nodelist=targets,
            node_color='lightcoral',
            node_size=2000,
            alpha=0.7
        )

        # Add labels
        labels = {node: node.split('.')[1] for node in self.G.nodes()}
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
    # Create sample mapping data with more varied examples
    sample_data = pd.DataFrame({
        'Source Table': [
            'database1.table1', 'database1.table2',
            'database2.table1', 'database2.table2',
            'database3.table1', 'database3.table2'
        ],
        'Target Table': [
            'database4.target1', 'database4.target1',
            'database4.target2', 'database5.target1',
            'database5.target1', 'database5.target2'
        ]
    })
    sample_data.to_csv('sample_mapping.csv', index=False)

    # Create visualizer and generate visualizations
    visualizer = TableLineageVisualizer('sample_mapping.csv')
    visualizer.create_interactive_plotly()
    visualizer.create_static_graph()


if __name__ == "__main__":
    main()