from copy import deepcopy


def fcfs_schedule(processes):
    processes = deepcopy(processes)
    processes.sort(key=lambda item: (item["arrival"], item["pid"]))

    current_time = 0
    gantt = []
    timeline = []
    scheduled = []
    waiting_queue = []

    while processes or waiting_queue:
        if not waiting_queue:
            next_proc = processes.pop(0)
            if current_time < next_proc["arrival"]:
                timeline.append({"time": current_time, "queue": []})
                current_time = next_proc["arrival"]
            waiting_queue.append(next_proc)

        proc = waiting_queue.pop(0)
        if current_time < proc["arrival"]:
            current_time = proc["arrival"]

        timeline.append({"time": current_time, "queue": [item["pid"] for item in waiting_queue]})
        start_time = current_time
        end_time = start_time + proc["burst"]

        gantt.append({"pid": proc["pid"], "start": start_time, "end": end_time})
        proc["completion"] = end_time
        proc["turnaround"] = proc["completion"] - proc["arrival"]
        proc["waiting"] = proc["turnaround"] - proc["burst"]
        proc["response"] = start_time - proc["arrival"]

        current_time = end_time
        scheduled.append(proc)

        while processes and processes[0]["arrival"] <= current_time:
            waiting_queue.append(processes.pop(0))
            timeline.append({"time": current_time, "queue": [item["pid"] for item in waiting_queue]})

    total_processes = len(scheduled)
    avg_waiting = sum(item["waiting"] for item in scheduled) / total_processes
    avg_turnaround = sum(item["turnaround"] for item in scheduled) / total_processes
    first_arrival = min(item["arrival"] for item in scheduled)
    last_completion = max(item["completion"] for item in scheduled)
    busy_time = sum(item["burst"] for item in scheduled)
    cpu_util = round((busy_time / (last_completion - first_arrival)) * 100, 2) if last_completion > first_arrival else 100.0
    throughput = round(total_processes / (last_completion - first_arrival), 2) if last_completion > first_arrival else float(total_processes)

    return {
        "gantt": gantt,
        "process_table": scheduled,
        "timeline": timeline,
        "average_waiting": round(avg_waiting, 2),
        "average_turnaround": round(avg_turnaround, 2),
        "cpu_utilization": cpu_util,
        "throughput": throughput,
        "total_time": last_completion,
        "idle_time": round((last_completion - first_arrival) - busy_time, 2)
    }
