import functools
import time


def time_of_work_wraps(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print('Start function')
        start = time.perf_counter()

        result = func(*args, **kwargs)

        end = time.perf_counter()
        print(f'Time of work {func.__name__} - {(end - start):.6f}s')
        print('--')
        return result

    return wrapper


# from numba import njit
# @time_of_work_wraps
# @njit
# def do_bypass(n):
#     sum_count = 0
#     for i in range(n):
#         sum_count+=i
#     print(sum_count)
#
#
# do_bypass(1000)
# do_bypass(2300)
# do_bypass(6000)
# do_bypass(12600)


# import numpy as np
# from numba import njit
#
# @time_of_work_wraps
# @njit
# def t1est1():
#     ar = np.array([])
#
#     for i in range(100):
#         np.insert(ar, 3, {
#             f'{i}a':i,
#             f'{i}b':i,
#             f'{i}c':i,
#             f'{i}d':i,
#         })
#     print(ar)
#
# @time_of_work_wraps
# def t1est2():
#     ar = []
#
#     for i in range(100):
#         ar.append({
#             f'{i}a': i,
#             f'{i}b': i,
#             f'{i}c': i,
#             f'{i}d': i,
#         })
#
# t1est1()
# t1est2()