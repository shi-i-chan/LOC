import json
import requests
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from typing import NoReturn, Union, Tuple, List

from config import config


def get_data(repo: str) -> Union[str, bool]:
    url = f'https://api.codetabs.com/v1/loc/?github={config["username"]}/{repo}'
    with requests.Session() as s:
        data = s.get(url)
    if data.status_code == 200:
        return json.loads(data.text)
    return False


def get_results(config: dict) -> Tuple[List[str], List[int]]:
    results = {key: 0 for key in config['languages']}
    for repo in config['repos']:
        if data := get_data(repo):
            for element in data:
                lang = element['language']  # NOQA
                if lang in results:
                    results[lang] += int(element['linesOfCode'])  # NOQA
        else:
            print(f'Some error with {repo} repository. Try to restart.')
    return list(results.keys()), list(results.values())


def get_figure(save: bool = False) -> NoReturn:
    labels, values = get_results(config)

    colors = px.colors.qualitative.Plotly
    fig = make_subplots(rows=1, cols=2,
                        specs=[[{"type": "pie"}, {"type": "bar"}]])

    fig.add_trace(
        go.Pie(
            labels=labels,
            values=values,
            textinfo='label+percent',
            insidetextorientation='radial',
            showlegend=True,
        ),
        row=1, col=1,
    )

    fig.update_traces(
        hoverinfo='label+percent',
        marker=dict(colors=colors),
        row=1, col=1,
    )

    for idx, (label, value) in enumerate(zip(labels, values)):
        fig.add_trace(
            go.Bar(
                x=[label],
                y=[value],
                marker_color=colors[idx],
                showlegend=False,
                textposition='auto',
            ),
            row=1, col=2
        )

    fig.add_trace(
        go.Scatter(
            x=labels,
            y=values,
            text=values,
            mode='text',
            textposition='top center',
            textfont=dict(
                size=12,
            ),
            showlegend=False,
        ),
        row=1, col=2
    )

    fig.update_yaxes(title_text="LOC", row=1, col=2)
    fig.update_xaxes(title_text="Language", row=1, col=2)
    fig.update_layout(title_text="All public repositories lines of code", height=450, width=1000)

    if save:
        fig.write_image("LOC.png")
    else:
        fig.show()


get_figure(save=True)
