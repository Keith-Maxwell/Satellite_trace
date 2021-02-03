import numpy as np
from calcul_trace_satellite_Louis_ETIENNE import determine_correction_for_t

EARTH_RADIUS = 6378  # km
EARTH_GRAV_CONST = 398600  # km³/s²


class Satellite:
    def __init__(
        self,
        semi_major_axis: float,
        eccentricity: float,
        inclination: float,
        longitude_ascending_node: float,
        argument_of_periapsis: float,
    ):
        self.sma = semi_major_axis  # km
        self.ecc = eccentricity
        self.inc = inclination  # deg
        self.LAN = longitude_ascending_node  # deg
        self.AOP = argument_of_periapsis  # deg
        self.radius_ap = self.sma * (1 + self.ecc)  # km
        self.radius_pe = self.sma * (1 - self.ecc)  # km
        self.altitude_ap = self.radius_ap + EARTH_RADIUS  # km
        self.altitude_pe = self.radius_pe + EARTH_RADIUS  # km
        self.period = 2 * np.pi * np.sqrt(np.power(self.sma, 3) / EARTH_GRAV_CONST)  # seconds
        self.velocity_ap = np.sqrt(
            2 * (-(EARTH_GRAV_CONST / (2 * self.sma)) + (EARTH_GRAV_CONST / self.radius_ap))
        )  # km/s
        self.velocity_pe = np.sqrt(
            2 * (-(EARTH_GRAV_CONST / (2 * self.sma)) + (EARTH_GRAV_CONST / self.radius_pe))
        )  # km/s

        self._heavy_stuff()

    def _heavy_stuff(self, step=30):
        # initialize
        self.nu_crit = round(np.degrees(np.arccos(-self.ecc)))
        nu_init = -self.AOP
        self.t_p = self._compute_t(nu_init)

        # compute t in function of nu
        self.nu_list = np.arange(-60, 360, step)
        self.t_list = np.array([self._compute_t(nu) - self.t_p for nu in self.nu_list])
        self.latitude_list = np.degrees(
            np.arcsin(np.sin(np.radians(self.inc) * np.sin(np.radians(self.AOP + self.nu_list))))
        )

        self.raw_longitude = np.array(
            [self._compute_longitude(nu, lat) for nu, lat in zip(self.nu_list, self.latitude_list)]
        )

    def _determine_correction_for_t(self, v_c, v):
        # Thanks to Louis ETIENNE for this code
        if -v_c <= v <= v_c:
            correction = 0
            factor = 1
        elif v < -v_c:
            k = 0
            while v <= -(2 * np.pi) * ((k + 1) // 2) + (-1) ** (k + 1) * v_c:
                k += 1
                correction = -k * np.pi
                factor = (-1) ** k
        else:
            k = 0
            while v >= (2 * np.pi) * ((k + 1) // 2) + (-1) ** k * v_c:
                k += 1
                correction = k * np.pi
                factor = (-1) ** k
        return correction, factor

    def _determine_correction_for_lo(self, aop, v):
        if -aop - np.pi / 2 <= v <= -aop + np.pi / 2:
            correction = 0
            factor = 1
        elif v < -aop - np.pi / 2:
            k = 0
            while v <= -aop - np.pi * (k + 0.5):
                k += 1
                correction = -k * np.pi
                factor = (-1) ** k
        else:
            k = 0
            while v >= -aop + np.pi * (k + 0.5):
                k += 1
                correction = k * np.pi
                factor = (-1) ** k

        if np.radians(self.inc) > np.pi / 2:
            correction *= -1
        return correction, factor

    def _compute_t(self, nu):
        correction, factor = self._determine_correction_for_t(
            np.radians(self.nu_crit), np.radians(nu)
        )
        return np.sqrt(self.sma ** 3 / EARTH_GRAV_CONST) * (
            correction
            + factor
            * np.arcsin(
                np.sqrt((1 - np.power(self.ecc, 2)))
                / (1 + self.ecc * np.cos(np.deg2rad(nu)))
                * np.sin(np.deg2rad(nu))
            )
            - self.ecc
            * (
                np.sqrt((1 - np.power(self.ecc, 2)))
                / (1 + self.ecc * np.cos(np.deg2rad(nu)))
                * np.sin(np.deg2rad(nu))
            )
        )

    def _compute_longitude(self, nu, lat):
        # input everything in degrees
        correction, factor = self._determine_correction_for_lo(
            np.radians(self.AOP), np.radians(nu)
        )
        return np.degrees(
            correction + factor * np.arcsin(np.tan(np.radians(lat)) / np.tan(np.radians(self.inc)))
        )

    def get_figure(self):
        pass

    def get_coords(self):
        pass


def multisat_plot(*args):
    pass


if __name__ == "__main__":
    sat = Satellite(40708, 0.8320, 61, 120, 270)
    print(sat.raw_longitude)