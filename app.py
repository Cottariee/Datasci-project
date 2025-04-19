import streamlit as st
import pandas as pd
import pydeck as pdk
import networkx as nx
import plotly.express as px
from sklearn.cluster import DBSCAN
import matplotlib.pyplot as plt
from datetime import datetime
from pyvis.network import Network
import matplotlib.pyplot as plt
import numpy as np
import tempfile
import os
from typing import Dict, Optional, Tuple

st.set_page_config(page_title="DataScience Project Visualization", layout="wide")
st.title('DataScience Chulalongkorn Resources')

# Load and prepare data
@st.cache_data
def load_data():
    data = pd.read_csv('cleaned_city.csv')
    
    # Clean and prepare data
    # data['price'] = pd.to_numeric(data['price'], errors='coerce')
    # data = data.dropna(subset=['latitude', 'longitude', 'price'])
    return data

@st.cache_data
def load_data_notcleaned():
    data = pd.read_csv('original_city.csv')
    return data


# Load data
data = load_data()
not_cleaned_data = load_data_notcleaned()


@st.cache_data
def load_data_cat2018() :
  data = pd.read_csv('category_2018.csv')
  return data
@st.cache_data
def load_data_cat2019() :
  data = pd.read_csv('category_2019.csv')
  return data
@st.cache_data
def load_data_cat2020() :
 data = pd.read_csv('category_2020.csv')
 return data
@st.cache_data
def load_data_cat2021() :
  data = pd.read_csv('category_2021.csv')
  return data
@st.cache_data
def load_data_cat2022() :
 data = pd.read_csv('category_2022.csv')
 return data
@st.cache_data
def load_data_cat2023() :
 data = pd.read_csv('category_2023.csv')
 return data

# print(data[data['Latitude'] == 'No Data'])

# Sidebar filters
st.sidebar.header('Filters')

# Price range filter
# max_price = int(data['price'].max())
# min_price = int(data['price'].min())
# price_range = st.sidebar.slider(
#     'Price Range (THB)',
#     min_value=min_price,
#     max_value=max_price,
#     value=(min_price, max_price)
# )


# DBSCAN clustering parameters
st.sidebar.header('DBSCAN Parameters')

st.sidebar.write("eps (degree)")
epsilon_slider =  st.sidebar.slider(min_value=1.0 , max_value=5.0 ,step=0.1 , value=1.6 , label='epsilon dbscan',format="%.1f")
# st.sidebar.write("Create a slider for eps here")
                               
st.sidebar.write("min_samples")
min_samples_slider = st.sidebar.slider(min_value=3 , max_value=20 , value=3 , label='min_sample_dbscan')

top_number_slider = st.sidebar.slider(min_value=4 , max_value=7 , value=5 , label='how much top country to display ')


                            


# num_top_clusters = st.sidebar.slider('Number of Top Clusters to Show', 1, 10, 5)

# Map style selection
map_style = st.sidebar.selectbox(
    'Select Base Map Style',
    options=['Dark', 'Light', 'Road', 'Satellite'],
    index=0
)

# Define map style dictionary
MAP_STYLES = {
    'Dark': 'mapbox://styles/mapbox/dark-v10',
    'Light': 'mapbox://styles/mapbox/light-v10',
    'Road': 'mapbox://styles/mapbox/streets-v11',
    'Satellite': 'mapbox://styles/mapbox/satellite-v9'
}

# Filter data based on selections

coords = data[['Latitude', 'Longitude']] 
eps_degrees = epsilon_slider
min_samples = min_samples_slider
db = DBSCAN(eps=eps_degrees, min_samples=min_samples).fit(coords)
        
        # Add cluster labels to dataframe
data['cluster'] = db.labels_
        
        # Analyze clusters
clusters_count = data['cluster'].value_counts()
        # print(clusters_count)
clusters_count = clusters_count[clusters_count.index != -1]  # Exclude noise points
        # top_clusters = clusters_count.head(num_top_clusters) #เอา top กี่ตัวมาโชว์ เช่น top5

        # print(num_top_clusters)
        # print("eiei")
        # print(top_clusters)
        
        # Generate colors for clusters
unique_clusters = data[data['cluster'].isin(clusters_count.index)]['cluster'].unique()
unique_clusters_withoutlier = data['cluster'].unique()

        # print(unique_clusters)
colormap = plt.get_cmap('hsv')
cluster_colors = {cluster: [int(x*255) for x in colormap(i/len(unique_clusters))[:3]] + [160] 
                        for i, cluster in enumerate(unique_clusters)}
        
cluster_colors_withoutlier = {cluster: [int(x*255) for x in colormap(i/len(unique_clusters))[:3]] + [160] 
                for i, cluster in enumerate(unique_clusters_withoutlier)}
        
        # Create visualization dataframe
        # viz_data = data[data['cluster'].isin(top_clusters.index)].copy()
viz_data = data.copy()
viz_data['color'] = viz_data['cluster'].map(cluster_colors)
        # print(viz_data['color'])
viz_data_withoutlier = data.copy()
viz_data_withoutlier['color'] = viz_data_withoutlier['cluster'].map(cluster_colors_withoutlier)

color_names = {
        '#8AEC20': 'blueee',      # Pastel Blue
        '#ffbb78': 'orange',    # Pastel Orange
        '#83EEC7': 'green',     # Pastel Green
        '#FFBFC0': 'red',       # Pastel Red
        '#c5b0d5': 'purple',    # Pastel Purple
        '#c7b19c': 'brown',     # Pastel Brown
        '#f7b7d2': 'pink',      # Pastel Pink
        '#bdbdbd': 'gray',      # Pastel Gray
        '#dbdb60': 'yellow',    # Pastel Yellow
        '#80e0f0': 'cyan'
        }

@st.cache_data
def load_network_from_file(file_path, file_format):
    """Load network from various file formats, either uploaded file or from a specific path"""
    try:
        # Handle CSV format
        if file_format == 'CSV':
            df = pd.read_csv(file_path, engine="python", sep=r",|\s+")
            if len(df.columns) < 2:
                raise ValueError("CSV file must have at least two columns for source and target nodes")
            source_col, target_col = df.columns[0], df.columns[1]
            G = nx.from_pandas_edgelist(df, source=source_col, target=target_col)
        
        # Handle GML format
        elif file_format == 'GML':
            G = nx.read_gml(file_path)
        
        # Handle GraphML format
        elif file_format == 'GraphML':
            G = nx.read_graphml(file_path)

        # Check if graph has nodes
        if len(G.nodes()) == 0:
            raise ValueError("The resulting graph has no nodes")
        
        return G
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None

class NetworkVisualizer:
    def __init__(self, G: nx.Graph):
        self.G = G
        self.colors = [
            "#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231", 
            "#911eb4", "#46f0f0", "#f032e6", "#bcf60c", "#fabebe",
            "#008080", "#e6beff", "#9a6324", "#fffac8", "#800000"
        ]

    def _get_layout(self, layout_type: str, G: nx.Graph, k_space: float = 2.0):
        """Calculate layout positions with adjustable spacing"""
        if layout_type == "spring":
            k = 1/np.sqrt(len(G.nodes())) * k_space
            return nx.spring_layout(G, k=k, iterations=50, seed=42)
        elif layout_type == "kamada_kawai":
            return nx.kamada_kawai_layout(G)
        elif layout_type == "circular":
            return nx.circular_layout(G)
        elif layout_type == "random":
            return nx.random_layout(G, seed=42)
        else:
            return nx.spring_layout(G)

    def create_interactive_network(
        self, 
        communities: Optional[Dict] = None,
        layout: str = "spring",
        centrality_metric: str = "degree",
        scale_factor: float = 1000,
        node_spacing: float = 2.0,
        node_size_range: Tuple[int, int] = (10, 50),
        show_edges: bool = True, 
        font_size: int = 14 
    ) -> str:
        # Get layout positions with adjustable spacing
        pos = self._get_layout(layout, self.G, node_spacing)
        
        # Scale positions
        pos = {node: (coord[0] * scale_factor, coord[1] * scale_factor) 
               for node, coord in pos.items()}

        # Calculate centrality
        try:
            if centrality_metric == "degree":
                centrality = nx.degree_centrality(self.G)
            elif centrality_metric == "betweenness":
                centrality = nx.betweenness_centrality(self.G)
            elif centrality_metric == "closeness":
                centrality = nx.closeness_centrality(self.G)
            else:  # pagerank
                centrality = nx.pagerank(self.G)
        except:
            centrality = nx.degree_centrality(self.G)
            st.warning(f"Failed to compute {centrality_metric} centrality, using degree centrality instead.")

        # Scale node sizes
        min_cent, max_cent = min(centrality.values()), max(centrality.values())
        min_size, max_size = node_size_range
        if max_cent > min_cent:
            size_scale = lambda x: min_size + (x - min_cent) * (max_size - min_size) / (max_cent - min_cent)
        else:
            size_scale = lambda x: (min_size + max_size) / 2

        # Create a copy of the graph to modify attributes
        G_vis = self.G.copy()

        # Prepare color map for communities if present
        if communities:
            unique_communities = sorted(set(communities.values()))
            color_map = {com: self.colors[i % len(self.colors)] 
                        for i, com in enumerate(unique_communities)}
         
        # Set node attributes all at once
        for node in G_vis.nodes():
            G_vis.nodes[node].update({
                'label': str(node),
                'size': size_scale(centrality[node]),
                'x': pos[node][0],
                'y': pos[node][1],
                'physics': False,
                'title': (f"Node: {node}\nDegree: {self.G.degree(node)}\nCommunity: {communities[node]}"
                         if communities else
                         f"Node: {node}\nDegree: {self.G.degree(node)}"),
                'color': color_map[communities[node]] if communities else None
            })

        # Create network
        nt = Network(
            height="720px",
            width="100%",
            bgcolor="#ffffff",
            font_color="black",
            directed=self.G.is_directed()
        )

        # Convert from networkx to pyvis
        nt.from_nx(G_vis)
        
        # Disable physics
        nt.toggle_physics(False)

        # Set visualization options
        nt.set_options("""
        {
            "nodes": {
                "font": {"size": %d},
                "borderWidth": 2,
                "borderWidthSelected": 3,
                "shape": "dot"
            },
            "edges": {
                "color": {"color": "#666666"},
                "width": 1.5,
                "smooth": {
                    "type": "continuous",
                    "roundness": 0.5
                },
                "hidden": %s
            },
            "physics": {
                "enabled": false
            },
            "interaction": {
                "hover": true,
                "multiselect": true,
                "navigationButtons": true,
                "tooltipDelay": 100,
                "zoomView": true,
                "dragView": true,
                "zoomSpeed": 0.5,
                "minZoom": 1.0,
                "maxZoom": 2.5
            }
        }
        """ % (font_size, str(not show_edges).lower()))

        with tempfile.NamedTemporaryFile(delete=False, suffix='.html', mode='w', encoding='utf-8') as tmp:
            nt.save_graph(tmp.name)
            return tmp.name

class NetworkAnalyzer:
    def __init__(self, G: nx.Graph):
        self.G = G
        
    def get_basic_stats(self) -> Dict:
        """Calculate basic network statistics"""
        try:
            diameter = nx.diameter(self.G)
        except:
            diameter = None
            
        return {
            "Nodes": len(self.G.nodes()),
            "Edges": len(self.G.edges()),
            "Density": nx.density(self.G),
            "Diameter": diameter
        }
    
    def get_centralities(self) -> pd.DataFrame:
        """Calculate various centrality metrics"""
        centrality_metrics = {}
        try:
            centrality_metrics['Degree'] = nx.degree_centrality(self.G)
            centrality_metrics['Betweenness'] = nx.betweenness_centrality(self.G)
            centrality_metrics['Closeness'] = nx.closeness_centrality(self.G)
            centrality_metrics['PageRank'] = nx.pagerank(self.G)
        except Exception as e:
            st.warning(f"Some centrality metrics couldn't be computed: {str(e)}")
        
        df = pd.DataFrame(centrality_metrics)
        df.index.name = 'Node'
        return df.reset_index()
    
    def plot_degree_distribution(self) -> plt.Figure:
        """Plot degree distribution"""
        degrees = [d for n, d in self.G.degree()]
        fig, ax = plt.subplots(figsize=(6, 4))
        plt.hist(degrees, bins=range(max(degrees) + 2), align='left', rwidth=0.8)
        ax.set_xlabel('Degree')
        ax.set_ylabel('Frequency')
        ax.set_title('Degree Distribution')
        plt.tight_layout()
        return fig

@st.cache_data
def detect_communities(edges_str: str):
    """Community detection"""
    # Recreate graph from edges string
    edges = eval(edges_str)
    G = nx.Graph(edges)
    return list(nx.community.greedy_modularity_communities(G))

# tabs = st.tabs(["Data Vizualization"])
tab_main ,tab_viz, tab_analysis = st.tabs(["Data Vizualization","Network Visualization", "Network Analysis"])
with tab_main :
# Main content - Key metrics
    col1 , col2 = st.columns(2)
    with col1:
        st.metric("Total Unique City", len(data['City'].unique()))
    with col2:
        st.metric("Total Country", len(data['Country'].unique()))
    # with col3:
    #     st.metric("Average Reviews", f"{filtered_data['number_of_reviews'].mean():.1f}")
    # with col4:
    #     st.metric("Neighborhoods", filtered_data['neighbourhood'].nunique())

    # Price Distribution
    # st.header('Price Distribution')

    # fig_hist = px.histogram(
    #     filtered_data,
    #     x='price',
    #     nbins=100,  # You can adjust the number of bins
    #     title='Distribution of Listing Prices',
    #     labels={'price': 'Price (THB)', 'count': 'Number of Listings'},
    # )

    # st.plotly_chart(fig_hist)

    # Hotspot Analysis
    st.header('Author City Distribution')



    try:
        # Perform DBSCAN clustering
      
        
        
        # Create cluster layer
        scatter_layer = pdk.Layer(
            "ScatterplotLayer",
            viz_data,
            get_position="[Longitude,Latitude]",
            get_color = 'color',
            get_radius=10000,
            # opacity=0.5,
            pickable=True
        )

        # Create and display the map

        view_state_scatter = pdk.ViewState(
            latitude=26.9195,
            longitude=79.0847,
            zoom=1
        )
        
        # print(viz_data.columns)
        scatter_db = pdk.Deck(layers=[scatter_layer] , initial_view_state=view_state_scatter , tooltip={"text" : "color : {color}\nlatitude : {Latitude}\nlongitude : {Longitude}"} , map_style=MAP_STYLES[map_style])
        st.pydeck_chart(scatter_db)

        st.header("HeatMap Cities Distribution")
        
        # Create heatmap layer  

        scatter_layer_withoutlier = pdk.Layer(
            "ScatterplotLayer",
            viz_data_withoutlier,
            get_position="[Longitude,Latitude]",
            get_color = 'color',
            get_radius=10000,
            # opacity=0.5,
            pickable=True
        )


        heatmap_layer = pdk.Layer(
            "HeatmapLayer",
            viz_data,
            get_position=['Longitude','Latitude'],
            opacity=0.5,
            pickable=True
        )

        # # Create and display the map
        view_state_heatmap = pdk.ViewState(
            latitude=26.9195,
            longitude=79.0847,
            zoom=2
        )
    
        heatmap = pdk.Deck(layers=[heatmap_layer , scatter_layer_withoutlier] , initial_view_state=view_state_heatmap , tooltip={"text" : "latitude : {Latitude}\nlongitude :{Longitude}"})
        st.pydeck_chart(heatmap)


        st.header(f'Top {top_number_slider} Author Countries ')

        x_axis = not_cleaned_data['Country'].value_counts().head(top_number_slider).index
        y_axis = not_cleaned_data['Country'].value_counts().head(top_number_slider).values

     
        # Generate a list of color codes in hex format based on the number of bars
        color_list = list(color_names.keys())  # Get hex color codes
        dynamic_colors = color_list[:top_number_slider]  # Trim to fit the number of bars

    #     Map the hex color codes to their color names
        dynamic_color_names = [color_names.get(color, "Unknown") for color in dynamic_colors]
        # print(dynamic_colors)
        
        color_formap = {
            'Thailand' : '#83EEC7' , 
            'United States' : '#FFCC7E',
            'Japan' : '#DBDBDB',
            'India' : '#F5ABAB',
            'United Kingdom' : '#E4CFFF',
            'China' : '#FFCFE3' , 
            'Italy' : '#83EEC7'
            }
    
    

        fig = px.bar(x = x_axis.to_list() , y=y_axis,color=x_axis.tolist()  ,color_discrete_map=color_formap ,title=f"Top {top_number_slider} Countries")
        fig.update_layout(
            xaxis_title = 'Country',
            yaxis_title = 'Records'
        )

        # # Display the bar chart
        st.plotly_chart(fig)

        st.header('Pie Chart')

        other_value = not_cleaned_data['Country'].value_counts().sum() - not_cleaned_data['Country'].value_counts().head(top_number_slider).sum()

        pie_values = y_axis.tolist()
        pie_values.append(other_value)

        pie_names = x_axis.tolist()
        pie_names.append('Others')
        
        color_formap_pie = {
            'Thailand' : '#83EEC7' , 
            'United States' : '#FFCC7E',
            'Japan' : '#DBDBDB',
            'India' : '#FFCFE3',
            'United Kingdom' : '#E4CFFF',
            'Others' : '#A1F4FD' , 
            
        }

        fig = px.pie(values  =pie_values, names=pie_names, color=pie_names , color_discrete_map=color_formap_pie, title='Country Propotion By Pie chart')

        # Display the pie chart in Streamlit
        st.plotly_chart(fig)

     
        
        
        cat2018_data = load_data_cat2018()
        cat2019_data = load_data_cat2019()
        cat2020_data = load_data_cat2020()
        cat2021_data = load_data_cat2021()
        cat2022_data = load_data_cat2022()
        cat2023_data = load_data_cat2023()
        allcat_data = pd.concat([cat2018_data, cat2019_data , cat2020_data , cat2021_data , cat2022_data , cat2023_data], ignore_index=True)
        # print(len(cat2018_data))
        # print(len(cat2019_data))
        # print(len(allcat_data))
        

        # print(allcat_data['category'].value_counts().head(15).index.unique().to_list())
        category_options = allcat_data['category'].value_counts().head(15).index.unique().to_list()


        # df_test = load_data_test()
        fitered_top15 = allcat_data[allcat_data['category'].isin(category_options)]

        category_counts = fitered_top15.groupby('year')['category'].value_counts().reset_index(name='count')
        # df_test['count'] = category_counts.values
        # print(cat2023_data.groupby('year')['category'].value_counts())
        category_counts["proportion"] = category_counts.groupby("year")["count"].transform(lambda x: (x / x.sum() )*100)
    # Create an animated plot
        fig_cat = px.bar(
        category_counts,
        x="category",
        y="proportion",
        color="category",
        animation_frame="year",
        title="Category Trend Over Time (Top15)",
        labels={"Count": "Category Count", "Category": "Category"},
        # range_y=[0, category_counts['count'].max() + 1],  # Adjusting y-range dynamically
        )
        fig_cat.update_layout(
        yaxis_title = 'proportion (%)'
        )
    
        #  Show animation in Streamlit
        st.plotly_chart(fig_cat)

        #---------------------------------
        cat_selected_option = st.selectbox('Choose the category you like: ' , category_options)


        st.write(f'You selected: {cat_selected_option}')
        
        filtered_data = allcat_data[allcat_data['category'] == cat_selected_option]

        preference_cat = {
        'sourcetitle-abbrev': filtered_data['sourcetitle-abbrev'],
        'citation_title': filtered_data['citation_title'],
        'language': filtered_data['language'],
        'year': filtered_data['year'],
        'category': filtered_data['category']
        }

        df_pref_cat = pd.DataFrame(preference_cat)

        # Display table
        st.dataframe(df_pref_cat, height=300)
        # st.table(df_pref_cat.head(200))
        


        

        # st.write("Draw a hexagon map for clusters here")
        
        # # Create hexagon layer    
        
        # hexagon_layer = pdk.Layer(
        #     'HexagonLayer',
        #     viz_data ,
        #     get_position=['longitude' , 'latitude'],
        #     elevation_range = [0,3000],
        #     elevation_scale = 10,
        #     extruded = True
        # )

        # view_state_hexagon = pdk.ViewState(latitude=viz_data['latitude'].mean() , longitude=viz_data['longitude'].mean() ,zoom = 11 , pitch=30 )

        # # Create and display the map
        # hexagon = pdk.Deck(layers=[hexagon_layer] ,initial_view_state=view_state_hexagon , tooltip={"text" : "{cluster}\n{neighborhood}\n{color}"})
        
        # st.pydeck_chart(hexagon)
    
        
        # # Cluster Analysis
        # st.subheader('Cluster Statistics')

    except Exception as e:
        st.error(f"Error in clustering analysis: {e}")
with tab_viz:
        # Directly use a specific file path and format (no file upload)
        file_path = "graph_output.gml"  # Set your desired GML file path here
        file_format = "GML"  # Specify the file format ("GML", "GraphML", etc.)
        
        # Load network from file
        G = load_network_from_file(file_path, file_format)
        
        if G is None:
            st.info("Please ensure the file path and format are correct.")
            st.stop()

        # Move input controls to sidebar
        with st.sidebar:
             
            # Visualization options
            st.markdown("---")  # Add separator
            st.subheader("Visualization Options")
            
            layout_option = st.selectbox(
                "Layout Algorithm",
                ["spring", "kamada_kawai", "circular", "random"]
            )
            centrality_option = st.selectbox(
                "Node Size By", 
                ["degree", "betweenness", "closeness", "pagerank"]
            )
            
            # Size controls 
            scale_factor = st.slider(
                "Graph Size", 
                min_value=500, 
                max_value=3000, 
                value=1000,
                step=100,
                help="Adjust the overall size of the graph"
            )
            
            if layout_option == "spring":
                node_spacing = st.slider(
                    "Node Spacing",
                    min_value=1.0,
                    max_value=20.0,
                    value=5.0,
                    step=1.0,
                    help="Adjust the spacing between nodes (only for spring layout)"
                )
            else:
                node_spacing = 2.0
            
            node_size_range = st.slider(
                "Node Size Range",
                min_value=5,
                max_value=200,
                value=(10, 50),
                step=5,
                help="Set the minimum and maximum node sizes"
            )
            
            # Node label font size
            font_size = st.slider(
                "Label Font Size",
                min_value=8,
                max_value=40,
                value=16,
                step=2,
                help="Adjust the font size of node labels"
            )                
            
            # Edge visibility
            show_edges = st.toggle(
                "Show Edges",
                value=True,  
                help="Toggle edge visibility"
            )
            
            # Community detection
            st.markdown("---")  # Add separator
            show_communities = st.checkbox("Detect Communities")
            
            # Initialize communities variable
            communities = None
            community_stats_container = st.empty()  # Create a placeholder for stats
            
            if show_communities:
                try:
                    edges_str = str(list(G.edges()))
                    communities_iter = detect_communities(edges_str)
                    communities = {}
                    
                    # Create a list to store community sizes
                    community_sizes = []
                    
                    for idx, community in enumerate(communities_iter):
                        community_sizes.append(len(community))
                        for node in community:
                            communities[node] = idx
                    
                    # Use the placeholder to display community statistics
                    with community_stats_container.container():
                        st.caption("Community Statistics")
                        st.metric("Number of Communities", len(communities_iter))
                        avg_size = sum(community_sizes) / len(community_sizes)
                        st.metric("Average Community Size", f"{avg_size:.1f}")
                        
                        # Sort communities by size in descending order
                        community_df = pd.DataFrame({
                            'Community': range(len(community_sizes)),
                            'Size': community_sizes
                        }).sort_values('Size', ascending=False)
                        
                        st.caption("Community Sizes (sorted by size):")
                        st.dataframe(
                            community_df,
                            hide_index=True,
                            height=min(len(community_sizes) * 35 + 38, 300)
                        )
                        
                except Exception as e:
                    st.warning(f"Could not detect communities: {str(e)}")
        
        # Main visualization area (now full width)
        if G is not None:
            # Initialize analyzers
            analyzer = NetworkAnalyzer(G)
            visualizer = NetworkVisualizer(G)
            
            # Display basic stats in a more compact form
            st.text(
                f"Nodes: {len(G.nodes())} | Edges: {len(G.edges())} | "
                f"Density: {nx.density(G):.3f}"
            )
            
            # Create and display visualization with increased height
            html_file = visualizer.create_interactive_network(
                communities=communities,
                layout=layout_option,
                centrality_metric=centrality_option,
                scale_factor=scale_factor,
                node_spacing=node_spacing,
                node_size_range=node_size_range,
                show_edges=show_edges,
                font_size=font_size
            )
            
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            st.components.v1.html(html_content, height=800)
            os.unlink(html_file)

    # Analysis tab content
with tab_analysis:
        if G is not None:
            # Initialize analyzer
            analyzer = NetworkAnalyzer(G)
            
            st.header("Network Analysis")
            
            # Get basic statistics
            stats = analyzer.get_basic_stats()
            
            # Basic Statistics
            st.subheader("Basic Statistics")
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Nodes", stats["Nodes"])
            with col2:
                st.metric("Edges", stats["Edges"])
            with col3:
                st.metric("Density", f"{stats['Density']:.3f}")
            with col4:
                if stats["Diameter"]:
                    st.metric("Diameter", stats["Diameter"])
            
            # Create columns for degree distribution and centrality analysis
            st.markdown("---")  # Add separator
            left_col, right_col = st.columns(2)
            
            # Degree Distribution in left column
            with left_col:
                st.subheader("Degree Distribution")
                fig = analyzer.plot_degree_distribution()
                st.pyplot(fig)
            
            # Centrality Analysis in right column
            with right_col:
                st.subheader("Centrality Analysis")
                centrality_df = analyzer.get_centralities()
                st.dataframe(
                    centrality_df,
                    height=400  # Fixed height to match the plot
                )
        else:
            st.info("Please ensure the file path is correct or select a network in the Visualization tab")

    # scatter_layer = pdk.Layer(
    #         "ScatterplotLayer",
    #         data,
    #         get_position="[Longitude,Latitude]",
    #         get_color = [0, 255, 0],
    #         get_radius=10000,
    #         # opacity=0.5,
    #         pickable=True
    #     )

    #       # Create and display the map

    # view_state_scatter = pdk.ViewState(
    #         latitude=data['Latitude'].mean(),
    #         longitude=data['Longitude'].mean(),
    #         zoom=5
    #     )

    # scatter_db = pdk.Deck(layers=[scatter_layer] , initial_view_state=view_state_scatter , tooltip={"text" : "eie"})
    # st.pydeck_chart(scatter_db)



    # Price by neighborhood
    # price_by_neighborhood = filtered_data.groupby('neighbourhood')['price'].agg(['mean', 'count']).reset_index()
    # # print(price_by_neighborhood)
    # price_by_neighborhood.columns = ['neighbourhood', 'avg_price', 'listings_count']

    # fig_scatter = px.scatter(price_by_neighborhood,
    #                         x='listings_count',
    #                         y='avg_price',
    #                         text='neighbourhood',
    #                         title='Average Price vs Number of Listings by Neighborhood',
    #                         labels={'listings_count': 'Number of Listings',
    #                                'avg_price': 'Average Price (THB)'})
    # fig_scatter.update_traces(textposition='top center')
    # st.plotly_chart(fig_scatter)

