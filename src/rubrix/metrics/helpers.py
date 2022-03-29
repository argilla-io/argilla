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
    keys = [
        key.encode("unicode-escape").decode() if isinstance(key, str) else key
        for key in keys
    ]
    fig = go.Figure(data=go.Bar(y=values, x=keys))
    fig.update_layout(
        title=title,
        xaxis_title=x_legend,
        yaxis_title=y_legend,
    )
    return fig


def stacked_bar(
    x: list,
    y_s: Dict[str, list],
    title: str = "Bar",
    x_legend: str = "",
    y_legend: str = "",
):
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
        rows=1, cols=3, subplot_titles=["macro average", "micro average", "per label"]
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
    fig.add_bar(
        x=[k for k, v in data.items() if "macro" not in k and "micro" not in k],
        y=[v for k, v in data.items() if "macro" not in k and "micro" not in k],
        row=1,
        col=3,
    )
    fig.update_layout(showlegend=False, title_text=title)

    return fig
