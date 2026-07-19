# CPU Scheduling Simulator

A modern responsive CPU Scheduling Simulator built with Flask, Python, HTML5, CSS3, and Vanilla JavaScript.

## Features
- FCFS, SJF Non-Preemptive, SJF Preemptive (SRTF), Priority Scheduling, Round Robin
- Dynamic process input table with add/remove/edit controls
- Algorithm-specific fields for Priority and Round Robin
- Gantt chart visualization with animated process blocks
- Ready queue timeline showing queue states at each scheduling step
- Average waiting time, turnaround time, CPU utilization, throughput
- Dark/light theme toggle
- Responsive premium UI with glassmorphism and motion

## Project Structure
```
cpu_scheduler/
├── app.py
├── scheduler/
│   ├── fcfs.py
│   ├── sjf.py
│   ├── srtf.py
│   ├── priority.py
│   ├── round_robin.py
├── templates/
│   ├── index.html
│   ├── simulator.html
│   ├── result.html
├── static/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── images/
└── README.md
```

## Installation
1. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

2. Install Flask:
   ```bash
   pip install Flask
   ```

3. Run the application:
   ```bash
   python app.py
   ```

4. Open your browser and navigate to:
   ```
   http://127.0.0.1:5000/
   ```

## Usage
1. Click `Start Simulation` from the home page.
2. Select a scheduling algorithm.
3. Add or edit processes in the table.
4. For Priority Scheduling, set priority values.
5. For Round Robin, set the time quantum.
6. Click `Calculate Schedule` to view the results.

## Notes
- The backend uses modular scheduler functions for each algorithm.
- The UI uses vanilla JavaScript to manage dynamic forms and theme toggling.
- This package is designed for learning CPU scheduling with an attractive and polished interface.
