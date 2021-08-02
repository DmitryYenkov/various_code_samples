import os
import numpy as np
import pymap3d
from scipy.spatial.transform import Rotation
from itertools import combinations


def geo_conversion(pos, ell, ell_out):
    return pos


def restore_rotation(v1, v2):
    cos_a = np.dot(v1, v2) / np.linalg.norm(v1)
    angle = 0 if cos_a > 1.0 else np.arccos(cos_a)
    cross = np.cross(v1, v2)
    w = angle * cross / np.linalg.norm(cross)
    rot = Rotation.from_rotvec(w)
    return rot


def restore_position(u, pos0):
    q = restore_quat(u)
    return q.apply(pos0)


def restore_quat(u):
    qp = Rotation.from_rotvec(u[1] * np.array([0, 1, 0]))
    qy = Rotation.from_rotvec(u[2] * np.array([0, 0, 1]))
    qyp = qy * qp
    rx = qyp.apply(np.array([1, 0, 0]))
    rx = rx / np.linalg.norm(rx)

    k, l, m = rx
    z = np.sin(u[0])
    a = l ** 2 / k ** 2 + 1
    b = 2 * l * m * z / k ** 2
    c = z ** 2 * ((m / k) ** 2 + 1) - 1
    d = b ** 2 - 4 * a * c
    y = np.array([(-b - d ** 0.5) / a / 2, (-b + d ** 0.5) / a / 2])
    x = -(l * y + m * z) / k
    ry = np.array([x[0], y[0], z])
    rz = np.cross(rx, ry)
    if rz[2] < 0:
        ry = np.array([x[1], y[1], z])
    ry = ry / np.linalg.norm(ry)

    ry_h = qy.apply(np.array([0, 1, 0]))
    qr = restore_rotation(ry_h, ry)
    q_total = qr * qyp
    return q_total


def restore_rotation_speed(rx_1, rx, rz_1, rz):
    qz = restore_rotation(rz_1, rz)
    rxr = qz.apply(rx_1)
    qx = restore_rotation(rxr, rx)
    return qx * qz


def wwxr_correction(a, w, pos, z0=True):
    wxr = np.cross(w, pos, axisb=1)
    wwxr = np.cross(w, wxr, axisb=1)
    a -= wwxr
    if z0:
        a[:, 2] = 0
    return a


def get_middle(srns_points, get_mean=False):
    if srns_points.shape[0] < 3 or get_mean:
        return np.mean(srns_points, axis=0)

    pts = srns_points[:, :2]
    comb_indices = list(combinations(range(pts.shape[0]), 2))
    mid_pts, distances = [], []
    for ids in comb_indices:
        mid_pts.append(np.mean([pts[ids[0]], pts[ids[1]]], axis=0))
        distances.append(np.linalg.norm(pts[ids[0]] - pts[ids[1]]))

    mid_pts = np.multiply(np.array(mid_pts), np.tile(np.array(distances) / np.sum(distances), (2, 1)).T)
    middle = np.append(np.sum(mid_pts, axis=0), np.mean(srns_points[:, 2]))
    return middle


def join(*args):
    return os.path.join(*args).replace('\\', '/')
