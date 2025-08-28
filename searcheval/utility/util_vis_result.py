import pandas as pd
import json
import ipywidgets as widgets
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from IPython.display import display, clear_output


def vis_search_eval_json(json_file: str):

    with open(json_file, "r") as f:
        data = json.load(f)

    # Transform the data into a DataFrame
    rows = []
    for query, details in data.items():
        row = {"query": query}
        for strategy, score_details in details["scores"].items():
            row[strategy] = score_details["ndgc"]
        rows.append(row)

    df = pd.DataFrame(rows)
    df.set_index("query", inplace=True)

    # Calculate the average scores and append as a new row
    average_scores = df.mean().to_dict()
    average_scores["query"] = "Average NDCG Score"
    average_df = pd.DataFrame([average_scores])
    average_df.set_index("query", inplace=True)
    df = pd.concat([df, average_df])

    # Sort columns by strategy name in ascending order
    df = df[sorted(df.columns)]

    # Create a custom colormap
    cmap = LinearSegmentedColormap.from_list("custom_cmap", ["red", "yellow", "green"])

    # Create a function to update the heatmap
    def update_heatmap():
        clear_output(wait=True)  # Clear the previous output
        
        plt.figure(figsize=(12, 8))
        ax = sns.heatmap(df, annot=True, cmap=cmap, cbar=True, vmin=0, vmax=1)
        plt.xlabel('Strategies')
        plt.ylabel('Queries')
        plt.title('Search Evaluation Heatmap', fontsize=20)  # Make the title bigger
        plt.xticks(rotation=45, ha='right')  # Angle the x-axis labels
        
        # Add a horizontal line to separate the average row
        ax.hlines(y=len(df)-1, xmin=0, xmax=len(df.columns), color='black', linewidth=2)
        
        # Make the average row text bolder
        for t in ax.texts:
            if t.get_text() == 'Average':
                t.set_weight('bold')
                t.set_fontsize(12)
        
        plt.show()

    # Create a button to update the heatmap
    update_button = widgets.Button(description="Update Heatmap")

    # Define the button click event
    def on_button_click(b):
        update_heatmap()

    # Attach the event to the button
    update_button.on_click(on_button_click)

    # Display the button and the initial heatmap
    display(update_button)
    update_heatmap()



def vis_deep_eval_correct_tests(json_file: str, title: str = "DeepEval Correctness Heatmap"):
    with open(json_file, "r") as f:
        data = json.load(f)

    # Transform the data into a DataFrame
    rows = []
    total_tokens = {strategy: 0 for strategy in list(data.values())[0]["strategies"].keys()}

    for query, details in data.items():
        row = {"query": details['query']}
        for strategy, strategy_details in details["strategies"].items():
            # row[strategy] = strategy_details["scores"]["Correctness (GEval)"]["score"]
            row[strategy] = strategy_details["scores"]["Citation Correctness"]["score"]
            total_tokens[strategy] += strategy_details["tokens_used"]
        rows.append(row)

    df = pd.DataFrame(rows)
    df.set_index("query", inplace=True)

    # Calculate the average scores and append as a new row
    average_scores = df.mean().to_dict()
    average_scores["query"] = "Average Correctness Score"
    average_df = pd.DataFrame([average_scores])
    average_df.set_index("query", inplace=True)
    df = pd.concat([df, average_df])

    # Sort columns by strategy name in ascending order
    df = df[sorted(df.columns)]

    # Update column labels to include total tokens used
    updated_columns = [f"{strategy}\nTokens: {total_tokens[strategy]:,}" for strategy in df.columns]
    df.columns = updated_columns

    # Create a custom colormap
    cmap = LinearSegmentedColormap.from_list("custom_cmap", ["red", "yellow", "green"])

    # Create a function to update the heatmap
    def update_heatmap2():
        clear_output(wait=True)  # Clear the previous output
        
        plt.figure(figsize=(12, 8))
        ax = sns.heatmap(df, annot=True, cmap=cmap, cbar=True, vmin=0, vmax=1)
        plt.xlabel('Strategies / RAG LLM Tokens')
        plt.ylabel('Queries')
        plt.title(title, fontsize=20)  # Make the title bigger
        plt.xticks(rotation=45, ha='right')  # Angle the x-axis labels
        
        # Add a horizontal line to separate the average row
        ax.hlines(y=len(df)-1, xmin=0, xmax=len(df.columns), color='black', linewidth=2)
        
        # Make the average row text bolder
        for t in ax.texts:
            if t.get_text() == 'Average':
                t.set_weight('bold')
                t.set_fontsize(12)
        
        plt.show()

    # Create a button to update the heatmap
    update_button = widgets.Button(description="Update Heatmap")

    # Define the button click event
    def on_button_click(b):
        update_heatmap2()

    # Attach the event to the button
    update_button.on_click(on_button_click)

    # Display the button and the initial heatmap
    display(update_button)
    update_heatmap2()


def vis_all_evaluation_metrics(json_file: str, title: str = "RAG Evaluation Metrics"):
    """Visualize all three evaluation metrics: Citation Correctness, Semantic Similarity, and Completeness"""
    with open(json_file, "r") as f:
        data = json.load(f)

    metrics = ["Citation Correctness", "Semantic Similarity", "Completeness"]
    
    # Create subplots for each metric
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle(title, fontsize=16, fontweight='bold')
    
    cmap = LinearSegmentedColormap.from_list("custom_cmap", ["red", "yellow", "green"])
    
    for idx, metric in enumerate(metrics):
        # Transform the data into a DataFrame for this metric
        rows = []
        total_tokens = {strategy: 0 for strategy in list(data.values())[0]["strategies"].keys()}

        for query, details in data.items():
            row = {"query": details['query']}
            for strategy, strategy_details in details["strategies"].items():
                row[strategy] = strategy_details["scores"][metric]["score"]
                if idx == 0:  # Only count tokens once
                    total_tokens[strategy] += strategy_details["tokens_used"]
            rows.append(row)

        df = pd.DataFrame(rows)
        df.set_index("query", inplace=True)

        # Calculate the average scores and append as a new row
        average_scores = df.mean().to_dict()
        average_scores["query"] = f"Avg {metric}"
        average_df = pd.DataFrame([average_scores])
        average_df.set_index("query", inplace=True)
        df = pd.concat([df, average_df])

        # Sort columns by strategy name in ascending order
        df = df[sorted(df.columns)]

        # Create heatmap
        ax = axes[idx]
        sns.heatmap(df, annot=True, cmap=cmap, cbar=True, vmin=0, vmax=1, ax=ax)
        ax.set_title(metric, fontsize=14, fontweight='bold')
        ax.set_xlabel('Strategies')
        ax.set_ylabel('Queries' if idx == 0 else '')
        
        # Rotate x-axis labels
        ax.tick_params(axis='x', rotation=45)
        
        # Add a horizontal line to separate the average row
        ax.hlines(y=len(df)-1, xmin=0, xmax=len(df.columns), color='black', linewidth=2)
    
    plt.tight_layout()
    plt.show()
    
    # Display summary statistics
    print("\n📊 Summary Statistics:")
    print("=" * 50)
    
    # Calculate overall averages for each metric and strategy
    summary_data = {}
    for metric in metrics:
        summary_data[metric] = {}
        for query, details in data.items():
            for strategy, strategy_details in details["strategies"].items():
                if strategy not in summary_data[metric]:
                    summary_data[metric][strategy] = []
                summary_data[metric][strategy].append(strategy_details["scores"][metric]["score"])
    
    # Create summary table
    summary_rows = []
    strategies = list(summary_data[metrics[0]].keys())
    
    for strategy in sorted(strategies):
        row = {"Strategy": strategy}
        for metric in metrics:
            scores = summary_data[metric][strategy]
            avg_score = sum(scores) / len(scores)
            row[f"{metric} (Avg)"] = f"{avg_score:.3f}"
        
        # Add token usage
        total_tokens_for_strategy = sum(
            details["strategies"][strategy]["tokens_used"] 
            for details in data.values()
        )
        row["Total Tokens"] = f"{total_tokens_for_strategy:,}"
        summary_rows.append(row)
    
    summary_df = pd.DataFrame(summary_rows)
    print(summary_df.to_string(index=False))
    
    return summary_df