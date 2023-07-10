# Main file
import numpy as np
from matplotlib import pyplot as plt

from driving.environment import Environment

if __name__ == "__main__":
    env = Environment(nb_cars=50)
    dict_pos = {}
    G = 0
    for car in env.cars:
        car.move_car(np.random.rand() * 2 - 1)
    dict_pos[G] = env.NN_sim_until_out_noplot_norprint()
    nb_gen = 10

    for idx_gen in range(nb_gen):

        plt.figure()
        max_car = {"idx": 0, "fitness": 0}
        for i, car in enumerate(env.cars):
            car_fit = {"idx": i, "fitness": car.fitness(env.route)}
            if car_fit["fitness"] > max_car["fitness"]:
                max_car = car_fit
        # env.cars[max_car["idx"]].plot_pos()
        # plt.plot(*env.route.polygon.exterior.xy)
        # plt.axis("equal")
        # plt.show()
        print(" --- Generation {} : ".format(idx_gen), np.mean(env.fitnesses()))
        nb_surviving_cars = np.sum([car["alive"] for i, car in dict_pos[G][max(dict_pos[G].keys())].items()])
        print(f"Number of surviving cars: {nb_surviving_cars}")
        print(f"Number of Timesteps before all cars are out or T_max is reached: {max(dict_pos[G].keys())}")
        print('max fitness = {}'.format(max(env.fitnesses())))
        G += 1
        env.plot_UI()
        env.UI.show()
        # print(list(env.cars[max_car["idx"]].model.parameters()))
        env.make_new_gen(10, nb_mut=1)
        # print(list(env.cars[0].model.parameters()))
        for car in env.cars:
            car.move_car(np.random.rand() * 2 - 1)
        dict_pos[G] = env.NN_sim_until_out_noplot_norprint()
        # Print number of Timesteps before all cars are out or T_max is reached



    print(" === Last Generation {} : ".format(idx_gen + 1), np.mean(env.fitnesses()))
