# Main file
import numpy as np
from matplotlib import pyplot as plt
from driving.environment import Environment
import streamlit as st
import seaborn as sns

from driving.utils import get_dataframe_from_positions, plot_animated_race

if __name__ == "__main__":
    st.title("Self Driving Cars")
    st.subheader("By Kamil Benkirane")

    st.sidebar.title("Settings")
    st.sidebar.subheader("Environment")

    # Setup route
    # Add button to select route length
    route_length = st.sidebar.slider("Route length", 100, 400, 100)

    # Add button to select route width
    route_width = st.sidebar.slider("Route width", 10, 50, 10)

    # Add button to select number of cars
    nb_cars = st.sidebar.slider("Number of cars", 50, 200, 50)

    # Add button to select number of generations
    nb_gen = st.sidebar.slider("Number of generations", 10, 100, 10)

    # Add button to select number timesteps before simulation stops
    T_max = st.sidebar.slider("Maximum number of timesteps", 100, 1000, 100)

    # Generate route
    # Try 10 times to generate a route if no error otherwise say that it is impossible and need to change parameters

    st.subheader("Generate route:")
    try_iteration = 0
    while try_iteration <= 10:
        try_iteration += 1
        try:
            env = Environment(nb_cars=nb_cars, n_points=route_length, width=route_width)
            fig, ax = plt.subplots(1,1,figsize=(10,10))
            ax.plot(*env.route.polygon.exterior.xy, color='black')
            plt.axis("equal")
            st.pyplot(fig)
            # Ask if the route is ok otherwise continue generating routes (yes or no)
            if st.button("Generate a new route"):
                break
            else:
                try_iteration = 0
            break
        except:
            if try_iteration == 10:
                st.error("Impossible to generate a route with these parameters. Please change them.")
            else:
                continue

    dict_pos = {}
    for g in range(nb_gen):
        if g>0:
            env.make_new_gen(10, nb_mut=1)

        for car in env.cars:
            car.move_car(np.random.rand() * 2 - 1)

        dict_pos[g] = env.NN_sim_until_out_noplot_norprint(T_max=T_max)
        df = get_dataframe_from_positions(dict_pos)
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.plot(*env.route.polygon.exterior.xy, color='black')
        sns.scatterplot(data=df[df["Generation"] == g],
                        x="x", y="y", hue="alive", ax=ax)
        plt.axis("equal")
        st.pyplot(fig)

        st.subheader(f"Generation {g}")
        st.write(f"Mean fitness: {np.mean(env.fitnesses())}")
        st.write(f"Number of surviving cars: {np.sum([car['alive'] for i, car in dict_pos[g][max(dict_pos[g].keys())].items()])}")
        st.write(f"Number of Timesteps before all cars are out or T_max is reached: {max(dict_pos[g].keys())}")
        st.write(f"Max fitness: {max(env.fitnesses())}")

        fig = plot_animated_race(env, df, g)
        st.plotly_chart(fig)














