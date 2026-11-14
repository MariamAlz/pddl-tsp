# PDDL Search Engine for Route Finding and TSP

> **Course:** COSC 604 Artificial Intelligence · MSc, Khalifa University

A PDDL/STRIPS-based search engine for problems in the navigation domain, such as route finding and the Travelling Salesperson Problem (TSP). It reads a PDDL domain and problem, turns the `connected` facts into a graph of cities, and runs a choice of uninformed and informed graph-search algorithms from the start city to a goal city, reporting the path, the exploration history and the run time.

## What it does

- **PDDL to search problem**: helper functions added to `pddl_parser/PDDL.py` extract the city graph (`create_connections`, `create_unique`), the start city from the `(at ...)` fact (`find_at_city`), goal cities from the `(visited ...)` goals (`reverse_goal_state`) and a heuristic table (`create_heuristics`). Every edge has cost 1.
- **Search algorithms** (`search.py`), all built on one `graph_search` routine with an explored set:
  - Breadth-first search (`bfs`, FIFO frontier)
  - Depth-first search (`dfs`, LIFO frontier)
  - Iterative deepening search (`ids`, repeated depth-limited DFS)
  - Uniform-cost search (`ucs`)
  - Greedy best-first search (`bfgs`)
  - A* search (`astar`)
- **Comparison mode** (`-search all`): runs all six algorithms on the same problem and plots their run times as a bar chart.
- **Random TSP generator** (`generate_random.py`): `randomly_generate(num_cities)` writes a `pb<num_cities>.pddl` problem with random two-way connections, a random start city, and a goal of visiting every city and returning to the start.
- **Large test problems**: 23 generated problems with 1,000 to 23,000 cities (`pb1000.pddl` to `pb23000.pddl`), plus the TSP examples in `examples/tsp/` (`pb1` and `pb2` with 5 and 10 named cities, `pb3` and `pb4` with 1,000 and 10,000 cities).

## Project structure

```
pddl-parser-update-master/
├── search_engine.py      # command-line entry point (my addition)
├── search.py             # graph search, frontiers and algorithms (my addition)
├── generate_random.py    # random TSP problem generator (my addition)
├── pb1000.pddl … pb23000.pddl   # generated TSP problems
├── pddl_parser/          # PDDL Parser library (+ TSP helper functions in PDDL.py)
├── examples/             # PDDL domains: tsp, blocksworld, dinner, dwr
├── test_PDDL.py, test_planner.py   # PDDL Parser tests
└── LICENSE               # GPL-3.0
```

## Getting started

Requirements: Python 3 with `networkx`, `numpy`, `matplotlib` and `pandas`.

```bash
pip install networkx numpy matplotlib pandas
cd pddl-parser-update-master
```

Run a search:

```
python search_engine.py -domain <domain.pddl> -problem <problem.pddl> -search [bfs|dfs|ids|ucs|bfgs|astar|all]
```

For example:

```bash
python search_engine.py -domain examples/tsp/tsp.pddl -problem examples/tsp/pb1.pddl -search bfs
python search_engine.py -domain examples/tsp/tsp.pddl -problem pb1000.pddl -search all
```

Each run prints the start and goal city, the solution path, the exploration history and the elapsed time. The script must be run from inside `pddl-parser-update-master/`, because `search.py` is imported from the working directory.

To generate random TSP problems, use the `randomly_generate(num_cities)` function:

```bash
python -c "from generate_random import randomly_generate; randomly_generate(50)"   # writes pb50.pddl
```

## Tech

Python, NetworkX, NumPy, pandas, Matplotlib, PDDL.

## Credits

Built on [PDDL Parser](https://github.com/pucrs-automated-planning/pddl-parser) by Mau Magnaguagno (GPL-3.0), which provides the `pddl_parser` package, the example domains, the tests and the original `README.md` inside `pddl-parser-update-master/`. I added the search engine (`search_engine.py`, `search.py`) with BFS, DFS, iterative deepening, UCS, greedy best-first and A* graph search, the TSP helper functions at the end of `pddl_parser/PDDL.py`, and the random TSP problem generator (`generate_random.py`).

## License

PDDL Parser is licensed under the GNU General Public License v3.0; see [`pddl-parser-update-master/LICENSE`](pddl-parser-update-master/LICENSE).
