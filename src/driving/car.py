import numpy as np
import torch
from matplotlib import pyplot as plt
from shapely.geometry import LineString, MultiLineString, Point

from driving.utils import randfloat


class Car3(object):
    def __init__(self, pos=(0, 0), theta=0, speed=1, direction_size=20):
        self.pos = pos
        self.theta = theta
        self.point = Point(pos)
        self.speed = speed
        self.R = direction_size
        self.arrow_end = self._get_arrow_end()
        self.angles_list = [np.pi / 2, np.pi / 4, 0, -np.pi / 4, -np.pi / 2]
        self.antennas_endpoint, self.antennas_lines = self._get_antennas()
        self.model = self._make_model()

    def _get_arrow_end(self):
        return (
            self.pos[0] + self.R * np.cos(self.theta),
            self.pos[1] + self.R * np.sin(self.theta),
        )

    def plot_pos(self, **kwargs):
        if "ax" in kwargs:
            kwargs["ax"].plot(*zip(self.pos), "ob")
            kwargs["ax"].plot(*zip(*[self.pos, self.arrow_end]), "r--")

        else:
            plt.plot(*zip(self.pos), "ob")
            plt.plot(*zip(*[self.pos, self.arrow_end]), "r--")

    def move_car(self, amplitude, max_theta=np.pi / 8):
        if abs(amplitude) > 1:
            print(
                "error ! amplitude should be between -1 and 1. Here it is : {}".format(
                    amplitude
                )
            )

        theta = amplitude * max_theta
        self.pos = (
            self.pos[0] + self.speed * np.cos(theta + self.theta),
            self.pos[1] + self.speed * np.sin(theta + self.theta),
        )
        self.theta += theta
        self.point = Point(self.pos)
        self.arrow_end = self._get_arrow_end()
        self.antennas_endpoint, self.antennas_lines = self._get_antennas()

    def _get_antennas(self):
        antennas_endpoint = []
        for angle in self.angles_list:
            antennas_endpoint.append(
                (
                    self.pos[0] + 10 * self.R * np.cos(self.theta + angle),
                    self.pos[1] + 10 * self.R * np.sin(self.theta + angle),
                )
            )

        antennas_lines = []
        for endpoint in antennas_endpoint:
            antennas_lines.append(LineString([self.pos, endpoint]))

        return antennas_endpoint, antennas_lines

    def _get_antennas_dist(self, route):
        antennas_dist = []
        intersects = []
        for antenna_line in self.antennas_lines:
            intersect_line = route.polygon.intersection(antenna_line)
            if type(intersect_line) == MultiLineString:
                intersect_line = intersect_line[0]
            antennas_dist.append(intersect_line.length)
            intersects.append(
                (
                    intersect_line.boundary[1].xy[0][0],
                    intersect_line.boundary[1].xy[1][0],
                )
            )
        return antennas_dist, intersects

    def _make_model(self):
        model = car_nn()
        return model

    def predict_move(self, route):
        dist, points = self._get_antennas_dist(route)
        arr_dist = np.array(dist).reshape(1, -1)
        return self.model(torch.Tensor(arr_dist)).detach().numpy()[0]

    def fitness(self, route):
        line = LineString(route.points)
        return line.project(self.point)

    def mutate(self, nb_mut=1):
        for idx_mut in range(nb_mut):
            list_params = list(self.model.parameters())
            rand_layer = np.random.randint(len(list_params))
            if len(list_params[rand_layer].shape) == 1:
                i = np.random.randint(list_params[rand_layer].shape[0])
                list_params[rand_layer][i] += randfloat(-1, 1)
            elif len(list_params[rand_layer].shape) == 2:
                i = np.random.randint(list_params[rand_layer].shape[0])
                j = np.random.randint(list_params[rand_layer].shape[0])
                list_params[rand_layer][i, j] += randfloat(0, 1)


class car_nn(torch.nn.Module):
    def __init__(self):
        super().__init__()
        self.lin1 = torch.nn.Linear(5, 3)
        self.lin2 = torch.nn.Linear(3, 1)
        # Set requires_grad to False for each parameter
        for param in self.parameters():
            param.requires_grad = False

    def forward(self, x):
        x = torch.tanh(self.lin1(x))
        x = torch.tanh(self.lin2(x))
        return x
