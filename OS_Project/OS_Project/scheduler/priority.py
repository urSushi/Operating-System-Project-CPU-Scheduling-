from copy import deepcopy


def priority_schedule(processes):
    processes = deepcopy(processes)
    processes.sort(key=lambda item: (item["arrival"], item["priority"] if item["priority"] is not None else 0, item["pid"]))

    current_time = 0
    gantt = []
    timeline = []
    scheduled = []
    ready_queue = []

    while processes or ready_queue:
        while processes and processes[0]["arrival"] <= current_time:
            ready_queue.append(processes.pop(0))
            timeline.append({"time": current_time, "queue": [item["pid"] for item in ready_queue]})

        if not ready_queue:
            next_process = processes.pop(0)
            if current_time < next_process["arrival"]:
                timeline.append({"time": current_time, "queue": []})
                current_time = next_process["arrival"]
            ready_queue.append(next_process)

        ready_queue.sort(key=lambda item: (item["priority"], item["arrival"], item["burst"], item["pid"]))
        proc = ready_queue.pop(0)
        timeline.append({"time": current_time, "queue": [item["pid"] for item in ready_queue]})

        start_time = max(current_time, proc["arrival"])
        end_time = start_time + proc["burst"]
        gantt.append({"pid": proc["pid"], "start": start_time, "end": end_time})

        proc["completion"] = end_time
        proc["turnaround"] = proc["completion"] - proc["arrival"]
        proc["waiting"] = proc["turnaround"] - proc["burst"]
        proc["response"] = start_time - proc["arrival"]

        current_time = end_time
        scheduled.append(proc)

    total = len(scheduled)
    avg_waiting = sum(item["waiting"] for item in scheduled) / total
    avg_turnaround = sum(item["turnaround"] for item in scheduled) / total
    first_arrival = min(item["arrival"] for item in scheduled)
    last_completion = max(item["completion"] for item in scheduled)
    busy_time = sum(item["burst"] for item in scheduled)
    cpu_util = round((busy_time / (last_completion - first_arrival)) * 100, 2) if last_completion > first_arrival else 100.0
    throughput = round(total / (last_completion - first_arrival), 2) if last_completion > first_arrival else float(total)

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
