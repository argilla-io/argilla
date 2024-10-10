# app dashboard from https://huggingface.co/spaces/davanstrien/argilla-progress/blob/main/app.py
import os
from typing import List

import argilla as rg
import gradio as gr
import pandas as pd
import plotly.colors as colors
import plotly.graph_objects as go

client = rg.Argilla(
    api_url=os.getenv("ARGILLA_API_URL"),
    api_key=os.getenv("ARGILLA_API_KEY"),
)


def get_progress(dataset: rg.Dataset) -> dict:
    dataset_progress = dataset.progress(with_users_distribution=True)

    total, completed = dataset_progress["total"], dataset_progress["completed"]
    progress = (completed / total) * 100 if total > 0 else 0

    return {
        "total": total,
        "annotated": completed,
        "progress": progress,
        "users": {
            username: user_progress["completed"].get("submitted")
            for username, user_progress in dataset_progress["users"].items()
        },
    }


def create_gauge_chart(progress):
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number+delta",
            value=progress["progress"],
            title={"text": "Dataset Annotation Progress", "font": {"size": 24}},
            delta={"reference": 100, "increasing": {"color": "RebeccaPurple"}},
            number={"font": {"size": 40}, "valueformat": ".1f", "suffix": "%"},
            gauge={
                "axis": {"range": [None, 100], "tickwidth": 1, "tickcolor": "darkblue"},
                "bar": {"color": "deepskyblue"},
                "bgcolor": "white",
                "borderwidth": 2,
                "bordercolor": "gray",
                "steps": [
                    {"range": [0, progress["progress"]], "color": "royalblue"},
                    {"range": [progress["progress"], 100], "color": "lightgray"},
                ],
                "threshold": {
                    "line": {"color": "red", "width": 4},
                    "thickness": 0.75,
                    "value": 100,
                },
            },
        )
    )

    fig.update_layout(
        annotations=[
            dict(
                text=(
                    f"Total records: {progress['total']}<br>"
                    f"Annotated: {progress['annotated']} ({progress['progress']:.1f}%)<br>"
                    f"Remaining: {progress['total'] - progress['annotated']} ({100 - progress['progress']:.1f}%)"
                ),
                # x=0.5,
                # y=-0.2,
                showarrow=False,
                xref="paper",
                yref="paper",
                font=dict(size=16),
            )
        ],
    )

    fig.add_annotation(
        text=(
            f"Current Progress: {progress['progress']:.1f}% complete<br>"
            f"({progress['annotated']} out of {progress['total']} records annotated)"
        ),
        xref="paper",
        yref="paper",
        x=0.5,
        y=1.1,
        showarrow=False,
        font=dict(size=18),
        align="center",
    )

    return fig


def create_treemap(user_annotations, total_records):
    sorted_users = sorted(user_annotations.items(), key=lambda x: x[1], reverse=True)
    color_scale = colors.qualitative.Pastel + colors.qualitative.Set3

    labels, parents, values, text, user_colors = [], [], [], [], []

    for i, (user, contribution) in enumerate(sorted_users):
        percentage = (contribution / total_records) * 100
        labels.append(user)
        parents.append("Annotations")
        values.append(contribution)
        text.append(f"{contribution} annotations<br>{percentage:.2f}%")
        user_colors.append(color_scale[i % len(color_scale)])

    labels.append("Annotations")
    parents.append("")
    values.append(total_records)
    text.append(f"Total: {total_records} annotations")
    user_colors.append("#FFFFFF")

    fig = go.Figure(
        go.Treemap(
            labels=labels,
            parents=parents,
            values=values,
            text=text,
            textinfo="label+text",
            hoverinfo="label+text+value",
            marker=dict(colors=user_colors, line=dict(width=2)),
        )
    )

    fig.update_layout(
        title_text="User contributions to the total end dataset",
        height=500,
        margin=dict(l=10, r=10, t=50, b=10),
        paper_bgcolor="#F0F0F0",  # Light gray background
        plot_bgcolor="#F0F0F0",  # Light gray background
    )

    return fig


def get_datasets(client: rg.Argilla) -> List[rg.Dataset]:
    return client.datasets.list()


datasets = get_datasets(client)


def update_dashboard(dataset_idx: int | None = None):
    if dataset_idx is None:
        return [None, None, None]

    dataset = datasets[dataset_idx]
    progress = get_progress(dataset)

    gauge_chart = create_gauge_chart(progress)
    treemap = create_treemap(progress["users"], progress["total"])

    leaderboard_df = pd.DataFrame(
        list(progress["users"].items()), columns=["User", "Annotations"]
    )

    leaderboard_df = leaderboard_df.sort_values(
        "Annotations", ascending=False
    ).reset_index(drop=True)

    return gauge_chart, treemap, leaderboard_df


with gr.Blocks() as demo:
    gr.Markdown("# Argilla Dataset Dashboard")

    datasets_dropdown = gr.Dropdown(label="Select your dataset")
    datasets_dropdown.choices = [
        (dataset.name, idx) for idx, dataset in enumerate(datasets)
    ]

    def set_selected_dataset(dataset_idx) -> None:
        global selected_dataset

        dataset = datasets[dataset_idx]
        selected_dataset = dataset

    with gr.Row():
        gauge_output = gr.Plot(label="Overall Progress")
        treemap_output = gr.Plot(label="User contributions")

    with gr.Row():
        leaderboard_output = gr.Dataframe(
            label="Leaderboard", headers=["User", "Annotations"]
        )

    demo.load(
        update_dashboard,
        inputs=[datasets_dropdown],
        outputs=[gauge_output, treemap_output, leaderboard_output],
        every=5,
    )

    datasets_dropdown.change(
        update_dashboard,
        inputs=[datasets_dropdown],
        outputs=[gauge_output, treemap_output, leaderboard_output],
    )


if __name__ == "__main__":
    demo.launch()
