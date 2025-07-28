import numpy as np
import joblib
import plotly.express as px
import os
from sklearn.decomposition import PCA
# These imports are here just to ensure the script runs standalone if needed
import pandas as pd
from gensim.models import Word2Vec

# Define the path to the saved Log Sequence Matrix
log_sequence_matrix_path = "log_sequence_matrix.joblib"

# --- Load the Log Sequence Matrix ---
# IMPORTANT: This part assumes log_sequence_matrix.joblib already exists from previous successful runs
# If it doesn't, you need to run the full data prep and matrix generation script first
if not os.path.exists(log_sequence_matrix_path):
    print(f"Error: Log Sequence Matrix file '{log_sequence_matrix_path}' not found.")
    print("Please ensure the data preparation and Word2Vec training/averaging steps were completed successfully and the matrix was saved.")
    print("If you haven't done so, please run the full script provided in our previous turns (the one that starts with '--- Ensuring Log Sequence Matrix is available ---').")
    exit()

try:
    log_sequence_matrix = joblib.load(log_sequence_matrix_path)
    print(f"Log Sequence Matrix loaded successfully. Shape: {log_sequence_matrix.shape}")
except Exception as e:
    print(f"Error loading Log Sequence Matrix: {e}")
    exit()

if log_sequence_matrix.shape[0] == 0:
    print("The Log Sequence Matrix is empty. Nothing to plot.")
    exit()

# --- PCA for 2 Dimensions ---
print("\nPerforming PCA for 2 dimensions...")
pca_2d = PCA(n_components=2)
log_sequence_pca_2d = pca_2d.fit_transform(log_sequence_matrix)
print(f"2D PCA transformed data shape: {log_sequence_pca_2d.shape}")

# Create 2D Plotly Visualization (Optimized for Density)
fig_2d = px.scatter(
    x=log_sequence_pca_2d[:, 0],
    y=log_sequence_pca_2d[:, 1],
    title='2D PCA Projection of Log Sequence Vectors (All Points Displayed)',
    labels={'x': 'Principal Component 1', 'y': 'Principal Component 2'},
    hover_name=range(log_sequence_pca_2d.shape[0]) # Show original index on hover for investigation
)
# Key for density: very small marker size and low opacity
fig_2d.update_traces(
    marker=dict(
        size=2, # Very small marker size
        opacity=0.1, # Low opacity to show density, but still reveal overlaps
        line=dict(width=0) # No border lines to reduce visual clutter
    )
)
fig_2d.update_layout(
    plot_bgcolor='black', # Often good for dense plots to make points pop
    xaxis=dict(showgrid=False, zeroline=False), # Minimal grid lines
    yaxis=dict(showgrid=False, zeroline=False),
    margin=dict(l=20, r=20, b=20, t=60) # Tight margins
)
fig_2d.show()

# --- PCA for 3 Dimensions ---
print("\nPerforming PCA for 3 dimensions...")
pca_3d = PCA(n_components=3)
log_sequence_pca_3d = pca_3d.fit_transform(log_sequence_matrix)
print(f"3D PCA transformed data shape: {log_sequence_pca_3d.shape}")

# Create 3D Plotly Visualization (Optimized for Density)
fig_3d = px.scatter_3d(
    x=log_sequence_pca_3d[:, 0],
    y=log_sequence_pca_3d[:, 1],
    z=log_sequence_pca_3d[:, 2],
    title='3D PCA Projection of Log Sequence Vectors (All Points Displayed)',
    labels={'x': 'Principal Component 1', 'y': 'Principal Component 2', 'z': 'Principal Component 3'},
    hover_name=range(log_sequence_pca_3d.shape[0]) # Show original index on hover
)
fig_3d.update_traces(
    marker=dict(
        size=2, # Very small marker size
        opacity=0.1, # Low opacity to show density
        line=dict(width=0)
    )
)
fig_3d.update_layout(
    scene=dict(
        xaxis=dict(showgrid=False, backgroundcolor='black', zeroline=False),
        yaxis=dict(showgrid=False, backgroundcolor='black', zeroline=False),
        zaxis=dict(showgrid=False, backgroundcolor='black', zeroline=False)
    ),
    margin=dict(l=20, r=20, b=20, t=60),
    plot_bgcolor='black' # Set overall background to black as well for consistency
)
fig_3d.show()

print("\n--- Plotly visualizations (2D and 3D) generated. ---")
print("Remember: In the interactive Plotly window, you MUST use the zoom and pan tools to explore the dense areas and see individual points.")
print("The opacity and size settings are designed to reveal density and overlap.")