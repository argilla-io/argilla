#  Copyright 2021-present, the Recognai S.L. team.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from typing import Dict


def empty_visualization(message: str = "No data found"):
    import plotly.graph_objects as go

    fig = go.Figure()
    fig.update_layout(
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[{"text": message, "showarrow": False, "font": {"size": 30}}],
    )
    return fig


def bar(data: dict, title: str = "Bar", x_legend: str = "", y_legend: str = ""):
    import plotly.graph_objects as go

    if not data:
        return empty_visualization()

    keys, values = zip(*data.items())
    keys = [key.encode("unicode-escape").decode() if isinstance(key, str) else key for key in keys]
    fig = go.Figure(data=go.Bar(y=values, x=keys))
    fig.update_layout(
        title=title,
        xaxis_title=x_legend,
        yaxis_title=y_legend,
    )
    return fig


def stacked_bar(x: list, y_s: Dict[str, list], title: str = "Bar", x_legend: str = "", y_legend: str = ""):
    import plotly.graph_objects as go

    if not x or not y_s:
        return empty_visualization()

    data = [go.Bar(name=name, x=x, y=y_values) for name, y_values in y_s.items()]

    fig = go.Figure(data=data)
    fig.update_layout(
        title=title,
        xaxis_title=x_legend,
        yaxis_title=y_legend,
        barmode="stack",
    )

    return fig


def histogram(data: dict, title: str = "Bar", x_legend: str = "", y_legend: str = ""):
    if not data:
        return empty_visualization()

    data = {float(k): v for k, v in data.items()}
    return bar(data, title, x_legend, y_legend)


def tree_map(labels, parents, values, title: str = "Tree"):
    import plotly.graph_objects as go

    if not values:  # TODO: review condition
        return empty_visualization()

    fig = go.Figure(
        go.Treemap(
            labels=labels,
            parents=parents,
            values=values,
        )
    )
    fig.update_layout(title=title, margin=dict(t=50, l=0, r=0, b=0))

    return fig


def multilevel_pie(labels, parents, values, title: str = "Pie"):
    import plotly.graph_objects as go

    fig = go.Figure(
        go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
        )
    )
    fig.update_layout(title=title, margin=dict(t=50, l=0, r=0, b=0))

    return fig


def f1(data: Dict[str, float], title: str):
    from plotly.subplots import make_subplots

    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=[
            "macro average",
            "micro average",
            "per label",
        ],
    )

    fig.add_bar(
        x=[k.split("_")[0] for k, v in data.items() if "macro" in k],
        y=[v for k, v in data.items() if "macro" in k],
        row=1,
        col=1,
    )
    fig.add_bar(
        x=[k.split("_")[0] for k, v in data.items() if "micro" in k],
        y=[v for k, v in data.items() if "micro" in k],
        row=1,
        col=2,
    )
    per_label = {k: v for k, v in data.items() if all(key not in k for key in ["macro", "micro", "support"])}

    fig.add_bar(
        x=[k for k, v in per_label.items()],
        y=[v for k, v in per_label.items()],
        row=1,
        col=3,
    )
    fig.update_layout(showlegend=False, title_text=title)

    return fig
