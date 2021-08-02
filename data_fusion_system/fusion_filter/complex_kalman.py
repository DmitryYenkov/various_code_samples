# -*- coding: utf-8 -*-
"""
Created on Tue Dec 24 15:42:11 2019

@author: yenkov
"""

import numpy as np
import sympy as sym
from numpy.linalg import LinAlgError


class ComplexKalman:
    
    def __init__(self, course):

        self.course = np.radians(course)
        self.dT = 1
        self.t_prev = -self.dT
        self.sigma_xy = [25, 25, 25]
        self.sigma_v = [0.2, 0.2, 0.2]
        self.sigma_a = [0.02, 0.02, 0.02]
        self.sigma_w = [0.7, 0.7, 0.7]
        self.acc_bias = [3.6 * 9.81 / 10**6, 3.6 * 9.81 / 10**6, 3.6 * 9.81 / 10**6]
        self.gyr_bias = [np.radians(2) / 3600, np.radians(2) / 3600, np.radians(2) / 3600]
        
        self.X_cur = np.zeros(15, dtype=np.float64)
        self.mP_cur = np.eye(15, dtype=np.float64)
        self.mR = np.eye(6, dtype=np.float64)
        self.mH = np.zeros((6, 15), dtype=np.float64)
        self.mQ = np.eye(15, dtype=np.float64)
        
        self.reinit()
        self.f_func, self.jF_func = self.init_update_func()
        
    def reinit(self):
        
        self.X_cur = np.zeros((15, 1))
        self.X_cur[-1, 0] = self.course
        for i in range(3):
            self.X_cur[i+6, 0] = self.acc_bias[i]
            self.X_cur[i+9, 0] = self.gyr_bias[i]
        
        self.mP_cur = np.eye(15, dtype=np.float64)
        self.mH = np.concatenate((np.eye(6, dtype=np.float64), np.zeros((6, 9), dtype=np.float64)), axis=1)
        
        self.mR = np.eye(6) * np.array([x**2 for x in self.sigma_xy] + [v**2 for v in self.sigma_v],
                                       dtype=np.float64)
        
        mw = np.expand_dims(np.array(self.sigma_a + self.sigma_w, dtype=np.float64), axis=1)
        mg = np.concatenate((np.concatenate((np.zeros((3, 3)), np.eye(3), np.zeros((9, 3))), axis=0),
                             np.concatenate((np.zeros((12, 3)), np.eye(3)), axis=0)), axis=1)
        mq = mg @ mw
        self.mQ = mq @ mq.T * self.dT**2

    @staticmethod
    def init_update_func():

        r = 6371000
        dsx, dsy, dsz, dvx, dvy, dvz, dax, day, daz, ex, ey, ez, ips, psi, fi, t = sym.symbols(
            'dsx dsy dsz dvx dvy dvz dax day daz ex ey ez ips psi fi t')
        x = sym.Matrix([dsx, dsy, dsz, dvx, dvy, dvz, dax, day, daz, ex, ey, ez, ips, psi, fi])

        mp = sym.Matrix([[sym.cos(psi), 0, -sym.sin(psi)],
                         [0, 1, 0],
                         [sym.sin(psi), 0,  sym.cos(psi)]])
        mr = sym.Matrix([[1, 0, 0],
                         [0, sym.cos(ips), -sym.sin(ips)],
                         [0, sym.sin(ips),  sym.cos(ips)]])
        my = sym.Matrix([[sym.cos(fi), -sym.sin(fi), 0],
                         [sym.sin(fi), sym.cos(fi), 0],
                         [0, 0, 1]])
        mc = mp @ mr @ my

        ds = sym.Matrix([dsx, dsy, dsz])
        dv = sym.Matrix([dvx, dvy, dvz])
        da = sym.Matrix([dax, day, daz])
        e = sym.Matrix([ex, ey, ez])
        u = sym.Matrix([ips, psi, fi])

        ds_func = ds + dv * t
        dv_func = dv + mc * da * t
        da_func = da
        e_func = e
        u_func = u + e * t - sym.Matrix([dvx * t / r, 0, dvz * t / r])

        f_system = sym.Matrix([ds_func, dv_func, da_func, e_func, u_func])
        jacobian_f = f_system.jacobian(x)

        f_func = sym.lambdify((dsx, dsy, dsz, dvx, dvy, dvz, dax, day, daz, ex, ey, ez, ips, psi, fi, t), f_system)
        jf_func = sym.lambdify((dax, day, daz, ips, psi, fi, t), jacobian_f)

        return f_func, jf_func

    def step(self, s_imu, s_gps, v_imu, v_gps, t, gps_valid=False):

        x_cur = np.squeeze(self.X_cur, axis=1).tolist()
        dt = t - self.t_prev

        # if np.allclose(s_imu, s_gps):
        if gps_valid == [] or gps_valid is None:

            x_pred = self.f_func(*x_cur, dt)
            return x_pred[:3, 0].tolist(), x_pred[3:6, 0].tolist()

        input_ds = s_imu - s_gps
        input_dv = v_imu - v_gps

        z = np.expand_dims(np.concatenate((input_ds, input_dv), axis=0), axis=1)
        x_pred = self.f_func(*x_cur, dt)
        mf = self.jF_func(*x_cur[6:9], *x_cur[12:15], dt)
        mp_pred = mf @ self.mP_cur @ mf.T + self.mQ
        z_pred = self.mH @ x_pred
        
        ms = self.mH @ mp_pred @ self.mH.T + self.mR
        try:
            inv_ms = np.linalg.inv(ms)
        except LinAlgError:
            inv_ms = np.linalg.pinv(ms)

        k = mp_pred @ self.mH.T @ inv_ms
        self.X_cur = x_pred + k @ (z - z_pred)
        self.mP_cur = mp_pred - k @ self.mH @ mp_pred

        self.t_prev = t
        return self.X_cur[:3, 0].tolist(), self.X_cur[3:6, 0].tolist()


class SimpleKalman:

    def __init__(self, state0, r_matrix, q_matrix=None,
                 p_matrix=None, f_matrix=None, h_matrix=None):

        self.state_prev = np.zeros(state0.shape, dtype='float64')
        self.state = state0
        if q_matrix is None:
            self.q_matrix = np.identity(state0.shape[0], dtype='float64')
        else:
            self.q_matrix = q_matrix
        if p_matrix is None:
            self.p_matrix = np.identity(state0.shape[0], dtype='float64')
        else:
            self.p_matrix = p_matrix
        if f_matrix is None:
            self.f_matrix = np.identity(state0.shape[0], dtype='float64')
        else:
            self.f_matrix = f_matrix
        if h_matrix is None:
            self.h_matrix = np.identity(state0.shape[0], dtype='float64')
        else:
            self.h_matrix = h_matrix

        self.r_matrix = r_matrix
        self.kalman_gain = 0.5

    def step(self, new_meas):
        state_estimate = np.dot(self.f_matrix, self.state)
        p_estimate = np.dot(np.dot(self.f_matrix, self.p_matrix), self.f_matrix.T) + self.q_matrix

        meas_estimate = np.dot(self.h_matrix, state_estimate)
        s_matrix = np.dot(np.dot(self.h_matrix, p_estimate), self.h_matrix.T) + self.r_matrix
        self.kalman_gain = np.dot(np.dot(p_estimate, self.h_matrix.T), np.linalg.inv(s_matrix))

        self.update_state(state_estimate + np.dot(self.kalman_gain, (new_meas - meas_estimate)))
        self.p_matrix = p_estimate - np.dot(np.dot(self.kalman_gain, self.h_matrix), p_estimate)

        return self.state

    def update_state(self, value):
        self.state_prev = self.state
        self.state = value


class SRNSKalman(SimpleKalman):

    def __init__(self, state0, r_matrix, dt, t=0, q_matrix=None, p_matrix=None,
                 f_matrix=None, h_matrix=None, b_matrix=None):
        super().__init__(state0, r_matrix, q_matrix=q_matrix, p_matrix=p_matrix,
                         f_matrix=f_matrix, h_matrix=h_matrix)

        if b_matrix is None:
            self.b_matrix = np.identity(state0.shape[0], dtype='float64')
        else:
            self.b_matrix = b_matrix

        self.dt = dt
        self.t = t

    def step(self, t, new_meas=None, new_ctrl=None):

        dt = t - self.t
        if dt < self.dt:
            return None
        self.t = t

        if new_ctrl is None:
            self.f_matrix = np.array([[1, 0, dt, 0], [0, 1, 0, dt], [0, 0, 1, 0], [0, 0, 0, 1]], dtype=np.float64)
            state_estimate = np.dot(self.f_matrix, self.state)
        else:
            self.f_matrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]], dtype=np.float64)
            self.b_matrix = np.array([[dt, 0], [0, dt], [1, 0], [0, 1]], dtype=np.float64)
            state_estimate = np.dot(self.f_matrix, self.state) + np.dot(self.b_matrix, new_ctrl)

        if new_meas is None:
            self.update_state(state_estimate)
            return self.state

        p_estimate = np.dot(np.dot(self.f_matrix, self.p_matrix), self.f_matrix.T) + self.q_matrix

        meas_estimate = np.dot(self.h_matrix, state_estimate)

        s_matrix = np.dot(np.dot(self.h_matrix, p_estimate), self.h_matrix.T) + self.r_matrix

        try:
            s_inv = np.linalg.inv(s_matrix)
        except LinAlgError:
            s_inv = np.linalg.pinv(s_matrix)
        self.kalman_gain = np.dot(np.dot(p_estimate, self.h_matrix.T), s_inv)

        self.update_state(state_estimate + np.dot(self.kalman_gain, (new_meas - meas_estimate)))

        self.p_matrix = p_estimate - np.dot(np.dot(self.kalman_gain, self.h_matrix), p_estimate)

        return self.state


class MyRunningMean:

    def __init__(self, length, width=3):
        self.buf = np.zeros((int(length), int(width)))
        self.sum = np.zeros((int(width)))

    def step(self, x):
        self.sum += x - self.buf[0]
        self.buf = np.vstack((self.buf, x))[1:]
        return self.sum / self.buf.shape[0]


if __name__ == '__main__':

    ckf = ComplexKalman(30)
    jF_out = ckf.jF_func(*list(range(1, 8)))
    np.set_printoptions(suppress=True, linewidth=120)
    print(np.around(jF_out[:, 8:], 8))
