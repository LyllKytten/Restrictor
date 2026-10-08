# C++ Olympiad roadmap (city level)

City level is usually in November–December, so this plan is about 8 weeks.
Rule: **1–2 problems every day** works better than 10 problems on Sunday.
If you are stuck on a problem for 30–40 minutes, read the solution (editorial), then write it yourself without looking.

## Week 1 — Base and speed
- Fast input/output: `ios::sync_with_stdio(false); cin.tie(nullptr);`
- `long long` overflow (when to use it), integer division and `%` with negative numbers
- STL: `vector`, `string`, `sort`, `pair`, `map`, `set`, `unordered_map`
- Practice: Codeforces Div 4 / Div 3 problems A–B (rating 800–1000)

## Week 2 — Complexity, prefix sums, two pointers
- Big-O: about 10^8 simple operations per second. Pick an algorithm by looking at n
- Prefix sums (1D and 2D), difference arrays
- Two pointers, sliding window
- Practice: rating 1000–1200

## Week 3 — Binary search and greedy
- `lower_bound` / `upper_bound`
- Binary search on the answer (the "can we do it with X?" type)
- Greedy + sorting (intervals, events)
- Practice: rating 1100–1300

## Week 4 — Math
- GCD/LCM, primes, sieve of Eratosthenes, factorization
- Fast exponentiation, modular arithmetic (`% 1'000'000'007`)
- Basic combinatorics (C(n,k), counting)
- Practice: rating 1200–1400

## Week 5 — Dynamic programming (very common at olympiads)
- 1D DP: stairs, coins, longest increasing subsequence (n²)
- 2D DP: grid paths, knapsack, LCS
- Practice: CSES "Dynamic Programming" section

## Week 6 — Graphs
- Adjacency list, DFS, BFS, connected components
- BFS on a grid, shortest path in an unweighted graph
- Dijkstra with `priority_queue`
- Practice: CSES "Graph Algorithms" (first 10 problems)

## Week 7 — Contests
- 2 virtual contests per week (Codeforces Div 3 or past city/regional olympiad problems)
- After each contest: **upsolve** every problem you didn't solve
- Optional topics: DSU (union-find), bitmasks, stack/queue tricks

## Week 8 — Before the olympiad
- Solve past years of your city's olympiad (search "муниципальный этап информатика <your city> <year>")
- Practice partial scores: if you can't solve the full problem, write a slow brute force for the small subtasks. **That gives points!**
- Sleep properly before the day. No new topics in the last 2 days.

## Where to practice
- **Codeforces** — contests + problemset filtered by rating
- **CSES Problem Set** (cses.fi) — perfect classic problems by topic
- **acmp.ru**, **informatics.msk.ru** — Russian school olympiad problems
- **algorithmica.org/ru**, **e-maxx.ru** — theory explanations

## At the olympiad
1. Read ALL problems first, start with the easiest
2. Brute force first for subtasks, then improve
3. Test on edge cases: n = 1, max n, all equal numbers, negative numbers
4. Check `long long` and array sizes before submitting
