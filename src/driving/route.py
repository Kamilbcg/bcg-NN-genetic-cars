import numpy as np
from shapely.geometry import Polygon

from driving.utils import randfloat


class Route(object):
    def __init__(
        self,
        n_points=20,
        max_theta_change=np.pi / 8,
        dist_between_two_points=10,
        width=10,
    ):
        (
            self.points,
            self.lower_points,
            self.upper_points,
            self.initial_theta,
        ) = create_route(
            n_points=n_points,
            max_theta_change=max_theta_change,
            dist_between_two_points=dist_between_two_points,
            width=width,
        )
        self.polygon = Polygon(self.upper_points + list(reversed(self.lower_points)))


def create_route(
    n_points=20, max_theta_change=np.pi / 8, dist_between_two_points=10, width=5
):
    initial_pos = np.array([0, 0])
    initial_theta = randfloat(lower=0, upper=2 * np.pi)
    theta_to_horizontal = initial_theta

    first_pos = initial_pos + np.array(
        [
            dist_between_two_points * np.cos(initial_theta),
            dist_between_two_points * np.sin(initial_theta),
        ]
    )
    points = [initial_pos, first_pos]

    # Create Upper :

    initial_upper_pos = initial_pos + np.array(
        [
            width / 2 * np.cos(initial_theta + np.pi / 2),
            width / 2 * np.sin(initial_theta + np.pi / 2),
        ]
    )

    # Create Lower :
    initial_lower_pos = initial_pos + np.array(
        [
            width / 2 * np.cos(initial_theta - np.pi / 2),
            width / 2 * np.sin(initial_theta - np.pi / 2),
        ]
    )

    lower_points = [initial_lower_pos]
    upper_points = [initial_upper_pos]

    temp_nb_points = 2
    while temp_nb_points < n_points:
        temp_theta = randfloat(lower=-max_theta_change, upper=max_theta_change)
        theta_to_horizontal += temp_theta

        # Create Point
        temp_pos = points[-1] + np.array(
            [
                dist_between_two_points * np.cos(theta_to_horizontal),
                dist_between_two_points * np.sin(theta_to_horizontal),
            ]
        )
        points.append(temp_pos)

        # Create Upper
        temp_upper_pos = points[-2] + np.array(
            [
                width / 2 * np.cos(theta_to_horizontal + np.pi / 2),
                width / 2 * np.sin(theta_to_horizontal + np.pi / 2),
            ]
        )
        upper_points.append(temp_upper_pos)

        # Create Lower
        temp_lower_pos = points[-2] + np.array(
            [
                width / 2 * np.cos(theta_to_horizontal - np.pi / 2),
                width / 2 * np.sin(theta_to_horizontal - np.pi / 2),
            ]
        )
        lower_points.append(temp_lower_pos)

        temp_nb_points += 1
    # Create Upper
    temp_upper_pos = points[-1] + np.array(
        [
            width / 2 * np.cos(theta_to_horizontal + np.pi / 2),
            width / 2 * np.sin(theta_to_horizontal + np.pi / 2),
        ]
    )
    upper_points.append(temp_upper_pos)

    # Create Lower
    temp_lower_pos = points[-1] + np.array(
        [
            width / 2 * np.cos(theta_to_horizontal - np.pi / 2),
            width / 2 * np.sin(theta_to_horizontal - np.pi / 2),
        ]
    )
    lower_points.append(temp_lower_pos)

    return points, lower_points, upper_points, initial_theta
