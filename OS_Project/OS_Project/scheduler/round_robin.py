from copy import deepcopy


def round_robin_schedule(processes, quantum):
    processes = deepcopy(processes)
    processes.sort(key=lambda item: (item["arrival"], item["pid"]))

    current_time = 0
    queue = []
    gantt = []
    timeline = []
    completed = []
    remaining = {item["pid"]: item["burst"] for item in processes}
    response = {}

    while processes or queue:
        while processes and processes[0]["arrival"] <= current_time:
            queue.append(processes.pop(0))
            timeline.append({"time": current_time, "queue": [item["pid"] for item in queue]})

        if not queue:
            if processes:
                timeline.append({"time": current_time, "queue": []})
                current_time = processes[0]["arrival"]
                continue
            break

        proc = queue.pop(0)
        if proc["pid"] not in response:
            response[proc["pid"]] = current_time - proc["arrival"]

        start_time = max(current_time, proc["arrival"])
        run_time = min(quantum, remaining[proc["pid"]])
        end_time = start_time + run_time
        gantt.append({"pid": proc["pid"], "start": start_time, "end": end_time})

        remaining[proc["pid"]] -= run_time
        current_time = end_time

        while processes and processes[0]["arrival"] <= current_time:
            queue.append(processes.pop(0))
            timeline.append({"time": current_time, "queue": [item["pid"] for item in queue]})

        if remaining[proc["pid"]] > 0:
            queue.append(proc)
            timeline.append({"time": current_time, "queue": [item["pid"] for item in queue]})
        else:
            proc["completion"] = current_time
            proc["turnaround"] = proc["completion"] - proc["arrival"]
            proc["waiting"] = proc["turnaround"] - proc["burst"]
            proc["response"] = response.get(proc["pid"], 0)
            completed.append(proc)

    total_processes = len(completed)
    avg_waiting = sum(item["waiting"] for item in completed) / total_processes if total_processes else 0
    avg_turnaround = sum(item["turnaround"] for item in completed) / total_processes if total_processes else 0
    first_arrival = min(item["arrival"] for item in completed) if completed else 0
    last_completion = max(item["completion"] for item in completed) if completed else 0
    busy_time = sum(item["burst"] for item in completed)
    cpu_util = round((busy_time / (last_completion - first_arrival)) * 100, 2) if last_completion > first_arrival else 100.0
    throughput = round(total_processes / (last_completion - first_arrival), 2) if last_completion > first_arrival else float(total_processes)

    return {
        "gantt": gantt,
        "process_table": completed,
        "timeline": timeline,
        "average_waiting": round(avg_waiting, 2),
        "average_turnaround": round(avg_turnaround, 2),
        "cpu_utilization": cpu_util,
        "throughput": throughput,
        "total_time": last_completion,
        "idle_time": round((last_completion - first_arrival) - busy_time, 2)
    }
