from copy import deepcopy


def srtf_schedule(processes):
    processes = deepcopy(processes)
    processes.sort(key=lambda item: (item["arrival"], item["burst"], item["pid"]))

    current_time = 0
    gantt = []
    timeline = []
    remaining = {item["pid"]: item["burst"] for item in processes}
    completion = {}
    response = {}
    active = None
    active_start = 0
    ready_queue = []
    scheduled_order = []

    while processes or ready_queue or active:
        while processes and processes[0]["arrival"] <= current_time:
            ready_queue.append(processes.pop(0))
            timeline.append({"time": current_time, "queue": [item["pid"] for item in ready_queue]})

        if active:
            ready_queue.append(active)
            active = None

        if ready_queue:
            ready_queue.sort(key=lambda item: (remaining[item["pid"]], item["arrival"], item["pid"]))
            proc = ready_queue.pop(0)
            if proc["pid"] not in response:
                response[proc["pid"]] = current_time - proc["arrival"]
            if active is None or active["pid"] != proc["pid"]:
                if active is not None:
                    gantt.append({"pid": active["pid"], "start": active_start, "end": current_time})
                active = proc
                active_start = current_time

            current_time += 1
            remaining[proc["pid"]] -= 1
            timeline.append({
                "time": current_time,
                "queue": [item["pid"] for item in ready_queue]
            })

            if remaining[proc["pid"]] == 0:
                completion[proc["pid"]] = current_time
                gantt.append({"pid": proc["pid"], "start": active_start, "end": current_time})
                scheduled_order.append(proc)
                active = None
        else:
            if processes:
                timeline.append({"time": current_time, "queue": []})
                current_time = processes[0]["arrival"]
            else:
                break

    for proc in scheduled_order:
        proc["completion"] = completion[proc["pid"]]
        proc["turnaround"] = proc["completion"] - proc["arrival"]
        proc["waiting"] = proc["turnaround"] - proc["burst"]
        proc["response"] = response.get(proc["pid"], 0)

    total = len(scheduled_order)
    avg_waiting = sum(item["waiting"] for item in scheduled_order) / total
    avg_turnaround = sum(item["turnaround"] for item in scheduled_order) / total
    first_arrival = min(item["arrival"] for item in scheduled_order)
    last_completion = max(item["completion"] for item in scheduled_order)
    busy_time = sum(item["burst"] for item in scheduled_order)
    cpu_util = round((busy_time / (last_completion - first_arrival)) * 100, 2) if last_completion > first_arrival else 100.0
    throughput = round(total / (last_completion - first_arrival), 2) if last_completion > first_arrival else float(total)

    return {
        "gantt": gantt,
        "process_table": scheduled_order,
        "timeline": timeline,
        "average_waiting": round(avg_waiting, 2),
        "average_turnaround": round(avg_turnaround, 2),
        "cpu_utilization": cpu_util,
        "throughput": throughput,
        "total_time": last_completion,
        "idle_time": round((last_completion - first_arrival) - busy_time, 2)
    }
