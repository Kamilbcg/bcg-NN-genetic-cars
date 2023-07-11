import numpy as np
import pandas as pd


def randfloat(lower, upper):
    x = np.random.rand()
    return x * (upper - lower) + lower


def get_dataframe_from_positions(dict_pos):
    dict_pos_df = {"Generation": [], "T": [], "car": [], "x": [], "y": [], "alive": []}

    for gen in dict_pos.keys():
        for T in dict_pos[gen].keys():
            for car in dict_pos[gen][T].keys():
                dict_pos_df["Generation"].append(gen)
                dict_pos_df["T"].append(T)
                dict_pos_df["car"].append(car)
                x, y = dict_pos[gen][T][car]["position"]
                dict_pos_df["x"].append(x[0] if type(x) == np.ndarray else x)
                dict_pos_df["y"].append(y[0] if type(y) == np.ndarray else y)
                dict_pos_df["alive"].append(dict_pos[gen][T][car]["alive"])

    df = pd.DataFrame.from_dict(dict_pos_df)
    return df


import plotly.express as px


def plot_animated_race(env, df, g):
    fig = px.line(
        x=env.route.polygon.exterior.xy[0], y=env.route.polygon.exterior.xy[1]
    )

    fig = px.scatter(
        df[df["Generation"] == g],
        x="x",
        y="y",
        color="car",
        hover_name="car",
        animation_frame="T",
    )

    fig.add_trace(
        px.line(
            x=env.route.polygon.exterior.xy[0], y=env.route.polygon.exterior.xy[1]
        ).data[0]
    )
    # Make axis equal
    fig.update_xaxes(
        scaleanchor="y",
        scaleratio=1,
    )
    fig.update_yaxes(
        scaleanchor="x",
        scaleratio=1,
    )

    fig.layout.updatemenus[0].buttons[0].args[1]["frame"]["duration"] = 30
    fig.layout.updatemenus[0].buttons[0].args[1]["transition"]["duration"] = 5

    # Add route to the plot
    return fig
