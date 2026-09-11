from __future__ import annotations
from scipy.optimize import linear_sum_assignment

def assignment_pairs(cost, gate):
    r,c=linear_sum_assignment(cost)
    return [(int(i),int(j)) for i,j in zip(r,c) if cost[i,j] <= gate]

def predict_constant_velocity(prev2, prev1):
    return prev1 + (prev1-prev2)
