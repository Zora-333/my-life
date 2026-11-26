import copy
from collections import defaultdict, deque
from datetime import datetime, timedelta
import pandas as pd

def build_graph(tasks):
    succ = defaultdict(list)
    indegree = {t["id"]: 0 for t in tasks}
    for t in tasks:
        for p in t["predecessors"]:
            succ[p].append(t["id"])
            indegree[t["id"]] += 1
    return succ, indegree

def topological_sort(tasks):
    succ, indegree = build_graph(tasks)
    q = deque([tid for tid, d in indegree.items() if d == 0])
    order = []
    while q:
        cur = q.popleft()
        order.append(cur)
        for nxt in succ[cur]:
            indegree[nxt] -= 1
            if indegree[nxt] == 0:
                q.append(nxt)
    if len(order) != len(tasks):
        return None
    return order

def forward_pass(tasks, order):
    task_map = {t["id"]: t for t in tasks}
    ES, EF = {}, {}
    for tid in order:
        t = task_map[tid]
        ES[tid] = max([EF[p] for p in t["predecessors"]], default=0)
        EF[tid] = ES[tid] + t["duration"]
    return ES, EF

def backward_pass(tasks, order, EF):
    task_map = {t["id"]: t for t in tasks}
    succ, _ = build_graph(tasks)
    project_end = max(EF.values())
    LS, LF = {}, {}
    for tid in reversed(order):
        t = task_map[tid]
        LF[tid] = min([LS[s] for s in succ[tid]], default=project_end)
        LS[tid] = LF[tid] - t["duration"]
    return LS, LF

def compute_float(tasks, ES, LS):
    return {t["id"]: LS[t["id"]] - ES[t["id"]] for t in tasks}

def run_all(tasks):
    order = topological_sort(tasks)
    if order is None:
        return None
    ES, EF = forward_pass(tasks, order)
    LS, LF = backward_pass(tasks, order, EF)
    TF = compute_float(tasks, ES, LS)
    return {"order": order, "ES": ES, "EF": EF, "LS": LS, "LF": LF, "TF": TF}