from copy import deepcopy

import numpy as np
from matplotlib import pyplot as plt

from driving.car import Car3
from driving.route import Route


class Environment(object):
    def __init__(self, nb_cars=1):
        self.nb_cars = nb_cars
        self.route = Route(n_points=100, width=20, max_theta_change=np.pi / 6)
        self.cars = [
            Car3(theta=self.route.initial_theta, speed=5) for i in range(self.nb_cars)
        ]

        self.UI = plt.figure(figsize=(8, 5), constrained_layout=True)
        gs = self.UI.add_gridspec(6, 6)
        self.ax_Game = self.UI.add_subplot(gs[0:-2, 2:])
        self.ax_Game.set_title("Game")

        self.ax_Map = self.UI.add_subplot(gs[0:2, 0])
        self.ax_Map.set_title("map")

        self.ax_NN = self.UI.add_subplot(gs[2:4, 0])
        self.ax_NN.set_title("Neural_ Network")

        self.ax_Settings1 = self.UI.add_subplot(gs[4:, 0:3])
        self.ax_Settings1.set_title("Settings1")

        self.ax_Settings2 = self.UI.add_subplot(gs[4:, 3:])
        self.ax_Settings2.set_title("Settings2")

    def plot_UI(self):
        # plot Game
        plt.figure()
        self.ax_Game.cla()
        self.ax_Game.plot(*self.route.polygon.exterior.xy)
        for car in self.cars:
            if self.route.polygon.contains(car.point):
                car.plot_pos(ax=self.ax_Game)

                # plot antennas intersects :
                try:
                    self.lengths, self.intersects = car._get_antennas_dist(self.route)
                    self.ax_Game.plot(*zip(*self.intersects), "x", color="orange")
                except Exception:
                    print("error !")

        self.ax_Game.axis("equal")
        self.ax_Game.set_xlim(
            [self.cars[0].pos[0] - car.R * 5, self.cars[0].pos[0] + self.cars[0].R * 5]
        )
        self.ax_Game.set_ylim(
            [self.cars[0].pos[1] - car.R * 5, self.cars[0].pos[1] + self.cars[0].R * 5]
        )

        # plot map
        self.ax_Map.cla()
        self.ax_Map.plot(*self.route.polygon.exterior.xy)
        for car in self.cars:
            car.plot_pos(ax=self.ax_Map)

        self.ax_Map.axis("equal")
        # plt.pause(.1)

    def rand_sim_until_out(self):
        for car in self.cars:
            car.move_car(np.random.rand() * 2 - 1)

        while self._get_nb_cars_in() > 0:
            self.plot_UI()
            # display.display(env.UI)
            # display.clear_output(wait=True)
            for car in self.cars:
                car.move_car(np.random.rand() * 2 - 1)
                if not self.route.polygon.contains(car.point):
                    self.cars.remove(car)

    def _get_nb_cars_in(self):
        nb_cars_in = 0
        for car in self.cars:
            if self.route.polygon.contains(car.point):
                nb_cars_in += 1
        return nb_cars_in

    def dist_to_finish(self):
        nb_cars_in = 0
        for car in self.cars:
            if self.route.polygon.contains(car.point):
                nb_cars_in += 1
        return nb_cars_in

    def NN_sim_until_out(self):
        for car in self.cars:
            car.move_car(car.predict_move(self.route))

        while self._get_nb_cars_in() > 0:
            self.plot_UI()
            # display.display(env.UI)
            # display.clear_output(wait=True)
            for idx, car in enumerate(self.cars):
                # print('car number {} : fitness = {}'.format(idx+1, car.fitness(self.route)) )
                car.move_car(car.predict_move(self.route))
                if not self.route.polygon.contains(car.point):
                    self.cars.remove(car)

    def fitnesses(self):
        fitnesses = []
        for car in self.cars:
            fitnesses.append(car.fitness(self.route))
        return fitnesses

    def NN_sim_until_out_noplot(self):
        for car in self.cars:
            car.move_car(np.random.rand() * 2 - 1)

        while self._get_nb_cars_in() > 0:
            for idx, car in enumerate(self.cars):
                if self.route.polygon.contains(car.point):
                    car.move_car(car.predict_move(self.route))

            print("maximum fitness = {}".format(max(self.fitnesses())))

    def NN_sim_until_out_noplot_norprint(self, T_max=200):
        dict_pos = {}
        T = 0
        dict_pos[T] = {}
        for idx, car in enumerate(self.cars):
            car.move_car(np.random.rand() * 2 - 1)
            dict_pos[T][idx] = {
                "position": car.pos,
                "alive": self.route.polygon.contains(car.point),
            }

        while self._get_nb_cars_in() > 0 and T < T_max:
            T += 1
            dict_pos[T] = {}
            for idx, car in enumerate(self.cars):
                if dict_pos[T - 1][idx]["alive"]:
                    car.move_car(car.predict_move(self.route))
                    dict_pos[T][idx] = {
                        "position": car.pos,
                        "alive": self.route.polygon.contains(car.point),
                    }
                else:
                    dict_pos[T][idx] = {"alive": False, "position": car.pos}
                    # self.cars.remove(car)
            # self.plot_UI()
            # self.UI.show()
            # plt.close()
        return dict_pos

    def select_best_cars(self, n_best=10):
        fitnesses = np.array(self.fitnesses())
        best_idx = fitnesses.argsort()[::-1][:n_best]
        best_cars = [self.cars[i] for i in best_idx]
        return best_idx, best_cars

    def make_new_gen(self, n_best, nb_mut=1):
        best_idx, best_cars = self.select_best_cars(10)
        pop_size = 100  # len(self.cars)
        new_pop = []
        n_same_cars = pop_size // n_best
        n_completely_random = pop_size - n_same_cars * n_best

        for car in best_cars:
            car.pos = (0, 0)
            new_car = Car3(theta=self.route.initial_theta)
            new_car.model = deepcopy(car.model)
            new_pop.append(new_car)
            for idx_n_same in range(n_same_cars - 1):
                copy_car = deepcopy(new_car)
                copy_car.mutate(nb_mut=nb_mut)
                new_pop.append(copy_car)
        for idx_new_rand_car in range(n_completely_random):
            new_pop.append(Car3(theta=self.route.initial_theta))
        self.cars = new_pop
