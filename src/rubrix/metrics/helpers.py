def bar(data: dict, title: str = "Bar", x_legend: str = "", y_legend: str = ""):
    import plotly.graph_objects as go

    keys, values = zip(*data.items())
    fig = go.Figure(data=go.Bar(y=values, x=keys))
    fig.update_layout(
        title=title,
        xaxis_title=x_legend,
        yaxis_title=y_legend,
    )
    return fig


def histogram(data, title: str = "Bar", x_legend: str = "", y_legend: str = ""):
    data = {float(k): v for k, v in data.items()}
    return bar(data, title, x_legend, y_legend)


def tree_map(labels, parents, values, title: str = "Tree"):
    import plotly.graph_objects as go

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
