from flask import Flask, render_template, request, redirect, url_for, flash
import json
import webbrowser
import threading
from scheduler.fcfs import fcfs_schedule
from scheduler.sjf import sjf_schedule
from scheduler.srtf import srtf_schedule
from scheduler.priority import priority_schedule
from scheduler.round_robin import round_robin_schedule

app = Flask(__name__)
app.secret_key = "cpu_scheduler_secret"

ALGORITHM_INFO = {
    "fcfs": {
        "name": "First Come First Serve",
        "short": "First Come First Serve scheduling with clear completion and waiting time analysis.",
        "detail": "<h3>Basic Idea</h3><p>The process that arrives first gets the CPU first. It works exactly like a queue in real life: first person entering the line gets served first. FCFS is the simplest scheduling algorithm.</p><h3>Type</h3><p>Non-Preemptive</p><p>Once a process starts execution, it cannot be interrupted until it finishes.</p><h3>Working Principle</h3><p>Processes are executed based on arrival time order. If two processes arrive together, the one appearing first in the ready queue runs first.</p><h3>Advantages</h3><ul><li>Very simple</li><li>Easy to implement</li><li>Fair according to arrival order</li></ul><h3>Disadvantages</h3><ul><li>Convoy Effect: small processes wait behind large processes.</li><li>One huge process blocks many short processes, increasing waiting time and response time.</li></ul><h3>Best Use Cases</h3><ul><li>Batch systems</li><li>Simple systems</li></ul>"
    },
    "sjf": {
        "name": "SJF Non-Preemptive",
        "short": "Shortest Job First scheduling without preemption for intelligent batch ordering.",
        "detail": "<h3>Basic Idea</h3><p>The process with the smallest burst time executes first.</p><h3>Type</h3><p>Non-Preemptive</p><p>Once started, the process continues until completion.</p><h3>Working Principle</h3><p>Among available processes, choose the one with the shortest CPU burst time.</p><h3>Why SJF is Important</h3><p>SJF gives minimum average waiting time. It is mathematically optimal for non-preemptive scheduling.</p><h3>Advantages</h3><ul><li>Better average waiting time</li><li>Better turnaround time</li><li>Efficient for short jobs</li></ul><h3>Disadvantages</h3><ul><li>Starvation: large processes may wait forever if short jobs keep arriving.</li><li>Burst Time Prediction Problem: OS usually does not know exact future burst time, so estimation is needed.</li></ul><h3>Best Use Cases</h3><ul><li>Batch processing</li><li>Systems where execution time is predictable</li></ul>"
    },
    "srtf": {
        "name": "SJF Preemptive",
        "short": "Shortest Remaining Time First for dynamic preemptive priority handling.",
        "detail": "<h3>Basic Idea</h3><p>Always execute the process with the shortest remaining burst time.</p><h3>Type</h3><p>Preemptive</p><p>CPU can interrupt the current process anytime.</p><h3>Working Principle</h3><p>When a new process arrives, compare its burst time with the remaining time of the current process. If the new process is shorter, preempt the current process and give CPU to the new process.</p><h3>Advantages</h3><ul><li>Excellent response time</li><li>Very efficient</li><li>Lower average waiting time</li></ul><h3>Disadvantages</h3><ul><li>Complex implementation</li><li>Many context switches</li><li>Higher overhead</li></ul><h3>Important Concept: Context Switching</h3><p>When CPU changes from one process to another, the OS saves the current state and loads the new state. This is called context switching. Too many switches reduce efficiency.</p><h3>Best Use Cases</h3><ul><li>Interactive systems</li><li>Real-time systems</li></ul>"
    },
    "priority": {
        "name": "Priority Scheduling",
        "short": "Priority-based scheduling with process ranking and accurate queue updates.",
        "detail": "<h3>Basic Idea</h3><p>CPU is assigned according to priority. Higher priority process executes first.</p><h3>Types</h3><p>Can be preemptive or non-preemptive.</p><h3>Working Principle</h3><p>Each process has a priority number. The scheduler selects the highest priority process. Sometimes lower number means higher priority, or higher number means higher priority depending on system design.</p><h3>Advantages</h3><ul><li>Important tasks execute faster</li><li>Useful in real-time systems</li></ul><h3>Disadvantages</h3><ul><li>Starvation: low-priority processes may never execute.</li><li>Solution: Aging. Gradually increase priority of waiting processes to prevent starvation.</li></ul><h3>Best Use Cases</h3><ul><li>Real-time operating systems</li><li>Critical systems</li><li>Embedded systems</li></ul>"
    },
    "round_robin": {
        "name": "Round Robin Scheduling",
        "short": "Time-slice scheduling with queue rotation and step-by-step quantum execution.",
        "detail": "<h3>Basic Idea</h3><p>Each process gets CPU for a fixed time called the time quantum. Processes execute in circular order.</p><h3>Type</h3><p>Preemptive</p><h3>Working Principle</h3><p>Process gets CPU for a fixed quantum. If the process finishes, remove it. If not finished, move it to the back of the ready queue.</p><h3>Advantages</h3><ul><li>Fair scheduling</li><li>Good response time</li><li>No starvation</li></ul><h3>Disadvantages</h3><ul><li>Too small quantum: too many context switches and high overhead.</li><li>Too large quantum: becomes similar to FCFS.</li></ul><h3>Best Use Cases</h3><ul><li>Time-sharing systems</li><li>Interactive systems</li><li>Modern operating systems</li></ul>"
    }
}

ALGORITHMS = {key: value["name"] for key, value in ALGORITHM_INFO.items()}

COLOR_PALETTE = [
    "#5e84ff",
    "#42d6a4",
    "#ff6d85",
    "#f8cb6d",
    "#7a58ff",
    "#39b0fc",
    "#ff8f34",
    "#7edeff",
    "#ff63b1",
    "#8bc34a"
]


def build_color_map(process_list):
    palette = COLOR_PALETTE.copy()
    color_map = {}
    for idx, item in enumerate(process_list):
        color_map[item] = palette[idx % len(palette)]
    return color_map


def parse_processes(raw_data):
    try:
        processes = json.loads(raw_data)
    except (TypeError, ValueError):
        return []

    parsed = []
    for row in processes:
        pid = row.get("pid", "")
        try:
            arrival = float(row.get("arrival", 0))
            burst = float(row.get("burst", 0))
            priority = int(row.get("priority", 0)) if row.get("priority") not in [None, ""] else None
        except ValueError:
            continue

        if pid and arrival >= 0 and burst > 0:
            parsed.append({
                "pid": pid,
                "arrival": arrival,
                "burst": burst,
                "priority": priority,
                "remaining": burst
            })
    return parsed


@app.route("/")
def home():
    return render_template("index.html", algorithms=ALGORITHMS)


@app.route("/simulate")
def simulate():
    return render_template("simulator.html", algorithms=ALGORITHMS)


@app.route("/algorithm/<algo>")
def algorithm_detail(algo):
    algorithm = ALGORITHM_INFO.get(algo)
    if not algorithm:
        return redirect(url_for("home"))
    return render_template("algorithm_detail.html", algorithm_code=algo, algorithm=algorithm, algorithms=ALGORITHMS)


@app.route("/result", methods=["POST"])
def result():
    form = request.form
    algorithm = form.get("algorithm")
    process_data = form.get("process_data")
    quantum = form.get("quantum")

    processes = parse_processes(process_data)
    if not algorithm or algorithm not in ALGORITHMS:
        flash("Please select a valid algorithm.")
        return redirect(url_for("simulate"))
    if not processes:
        flash("Please add at least one valid process.")
        return redirect(url_for("simulate"))

    try:
        quantum = int(quantum) if quantum else None
    except ValueError:
        quantum = None

    if algorithm == "round_robin" and (quantum is None or quantum <= 0):
        flash("Time Quantum must be a positive integer for Round Robin.")
        return redirect(url_for("simulate"))

    if algorithm == "fcfs":
        result_data = fcfs_schedule(processes)
    elif algorithm == "sjf":
        result_data = sjf_schedule(processes)
    elif algorithm == "srtf":
        result_data = srtf_schedule(processes)
    elif algorithm == "priority":
        result_data = priority_schedule(processes)
    else:
        result_data = round_robin_schedule(processes, quantum)

    # Keep only the final queue state for each time unit in the ready queue timeline.
    if "timeline" in result_data:
        final_states = {}
        for step in result_data["timeline"]:
            final_states[step["time"]] = step
        result_data["timeline"] = [final_states[time] for time in sorted(final_states)]

    # Insert explicit idle segments into the Gantt data so idle periods are visible
    # Ensure we have a usable gantt list and a total time to bound the timeline.
    if "gantt" in result_data and isinstance(result_data["gantt"], list):
        gantt = sorted(result_data["gantt"], key=lambda s: float(s.get("start", 0)))
        new_gantt = []
        prev_end = 0.0
        for seg in gantt:
            try:
                start = float(seg.get("start", 0))
                end = float(seg.get("end", start))
            except (TypeError, ValueError):
                start = 0.0
                end = 0.0

            if start > prev_end:
                # add idle segment covering the gap
                new_gantt.append({
                    "pid": "Idle",
                    "start": prev_end,
                    "end": start,
                    "idle": True,
                })

            # preserve the original segment (ensure numeric start/end)
            seg["start"] = start
            seg["end"] = end
            seg.setdefault("idle", False)
            new_gantt.append(seg)
            prev_end = max(prev_end, end)

        # if timeline ends with idle before total_time, append final idle
        total_time = float(result_data.get("total_time") or (prev_end))
        if prev_end < total_time:
            new_gantt.append({
                "pid": "Idle",
                "start": prev_end,
                "end": total_time,
                "idle": True,
            })

        result_data["gantt"] = new_gantt

    color_map = build_color_map([row["pid"] for row in result_data["process_table"]])
    return render_template(
        "result.html",
        algorithm_code=algorithm,
        algorithm_name=ALGORITHMS[algorithm],
        result=result_data,
        color_map=color_map,
        quantum=quantum
    )


def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == "__main__":
    threading.Timer(1.0, open_browser).start()
    app.run(debug=True)
