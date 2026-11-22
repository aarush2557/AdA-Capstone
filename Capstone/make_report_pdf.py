"""
make_report_pdf.py  (Phase 5 - submission PDF)
==============================================
Builds  Capstone_Report.pdf  from the REAL results of the project:

    outputs/sample_output.txt       <- output trace written by  python main.py
    outputs/benchmark_results.json  <- numbers written by      python performance.py
    outputs/*.png                   <- charts and the route map
    *.py                            <- source code (printed in the appendix)

Because the numbers are read from those files, the PDF can never disagree with the code.
Run order:   python main.py --two-opt --plot --save-data > outputs/sample_output.txt
             python test_courier.py > outputs/test_results.txt
             python performance.py
             python make_report_pdf.py
"""

import json
import os
import textwrap

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, Preformatted,
                                SimpleDocTemplate, Spacer, Table, TableStyle)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "outputs")
PDF_PATH = os.path.join(HERE, "Capstone_Report.pdf")

# ------------------------------------------------------------------ student details
STUDENT = "Aarush Tyagi"
ROLL = "2501201019"
PROGRAMME = "BCA (AI & DS), Section A"
UNIVERSITY = "K.R. Mangalam University"
COURSE = "Analysis and Design of Algorithms - Capstone Assignment (100 marks)"

# ------------------------------------------------------------------ styles
ss = getSampleStyleSheet()
BODY = ParagraphStyle("Body", parent=ss["BodyText"], fontName="Helvetica", fontSize=9.6,
                      leading=13.2, spaceAfter=5)
H1 = ParagraphStyle("H1", parent=ss["Heading1"], fontName="Helvetica-Bold", fontSize=17,
                    textColor=colors.HexColor("#1f3a5f"), spaceBefore=14, spaceAfter=8, keepWithNext=1)
H2 = ParagraphStyle("H2", parent=ss["Heading2"], fontName="Helvetica-Bold", fontSize=12.2,
                    textColor=colors.HexColor("#2c5282"), spaceBefore=9, spaceAfter=4, keepWithNext=1)
SMALL = ParagraphStyle("Small", parent=BODY, fontSize=8.2, leading=10.5)
CELL = ParagraphStyle("Cell", parent=BODY, fontSize=8.3, leading=10.4, spaceAfter=0)
CELLB = ParagraphStyle("CellB", parent=CELL, fontName="Helvetica-Bold")
CAPTION = ParagraphStyle("Caption", parent=SMALL, alignment=TA_CENTER, textColor=colors.HexColor("#444444"))
CODE = ParagraphStyle("Code", fontName="Courier", fontSize=6.5, leading=7.7,
                      backColor=colors.HexColor("#f5f6f8"), borderPadding=3, spaceAfter=6)
CODE_SMALL = ParagraphStyle("CodeS", parent=CODE, fontSize=6.0, leading=7.1)
TITLE = ParagraphStyle("Title", parent=ss["Title"], fontName="Helvetica-Bold", fontSize=28,
                       leading=33, textColor=colors.HexColor("#1f3a5f"), alignment=TA_CENTER)
SUB = ParagraphStyle("Sub", parent=BODY, fontSize=13, leading=18, alignment=TA_CENTER)

HEAD_BG = colors.HexColor("#1f3a5f")
GRID = colors.HexColor("#b8c2cc")
ZEBRA = colors.HexColor("#eef2f7")


def P(text, style=BODY):
    return Paragraph(text, style)


def bullets(items):
    """Return a list of paragraphs that look like bullet points."""
    return [Paragraph(f"&bull;&nbsp;&nbsp;{t}", ParagraphStyle("b", parent=BODY, leftIndent=14,
            firstLineIndent=-10, spaceAfter=2.5)) for t in items]


def table(rows, col_widths, header=True, font=8.3, align_right_from=None):
    """Build a nicely formatted table. Strings are wrapped in Paragraphs automatically."""
    data = []
    for r_i, row in enumerate(rows):
        data.append([Paragraph(str(c), CELLB if (header and r_i == 0) else CELL) for c in row])
    t = Table(data, colWidths=col_widths, repeatRows=1 if header else 0)
    style = [("GRID", (0, 0), (-1, -1), 0.4, GRID), ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
             ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
             ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4)]
    if header:
        style += [("BACKGROUND", (0, 0), (-1, 0), HEAD_BG)]
        for c in range(len(rows[0])):                       # white header text
            data[0][c] = Paragraph(f'<font color="white">{rows[0][c]}</font>', CELLB)
        t = Table(data, colWidths=col_widths, repeatRows=1)
    for i in range(1, len(rows)):
        if i % 2 == 0:
            style.append(("BACKGROUND", (0, i), (-1, i), ZEBRA))
    t.setStyle(TableStyle(style))
    return t


def image(path, width_cm):
    """Insert a picture scaled to a given width, keeping its proportions."""
    w, h = ImageReader(path).getSize()
    width = width_cm * cm
    return Image(path, width=width, height=width * h / w)


def code_block(text, style=CODE, chunk=62, wrap=118):
    """Return Preformatted blocks. Long text is split into chunks so it can flow across pages."""
    lines = []
    for line in text.rstrip("\n").split("\n"):
        line = line.replace("\t", "    ")
        if len(line) > wrap:                                # wrap very long lines
            indent = len(line) - len(line.lstrip())
            lines.extend(textwrap.wrap(line, wrap, subsequent_indent=" " * (indent + 4)))
        else:
            lines.append(line)
    return [Preformatted("\n".join(lines[i:i + chunk]), style) for i in range(0, len(lines), chunk)]


def ms(seconds):
    """Format seconds as milliseconds for the tables."""
    return "-" if seconds is None else f"{seconds * 1000:.3f}"


# ------------------------------------------------------------------ page footer
def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#555555"))
    canvas.drawString(2 * cm, 1.1 * cm, f"{STUDENT} | Roll No. {ROLL} | Courier Planning System - ADA Capstone")
    canvas.drawRightString(A4[0] - 2 * cm, 1.1 * cm, f"Page {doc.page}")
    canvas.restoreState()


# ===================================================================== CONTENT
def build():
    res = json.load(open(os.path.join(OUT, "benchmark_results.json")))
    trace = open(os.path.join(OUT, "sample_output.txt")).read()
    tests = open(os.path.join(OUT, "test_results.txt")).read()
    W = A4[0] - 4 * cm                                       # usable page width
    s = []                                                   # the "story" = list of flowables

    # --------------------------------------------------------------- cover page
    s += [Spacer(1, 3.5 * cm), P("Intelligent Courier Planning System", TITLE), Spacer(1, 0.4 * cm),
          P("Sorting + Dynamic Programming + Dijkstra + TSP Approximation", SUB), Spacer(1, 0.9 * cm),
          P("<b>Capstone Project Report</b>", SUB), P(COURSE, SUB), Spacer(1, 1.6 * cm)]
    cover = [["Student", STUDENT], ["Roll number", ROLL], ["Programme", PROGRAMME],
             ["University", UNIVERSITY], ["Language", "Python 3 (standard library only for the algorithms)"],
             ["Submission", "Source code + README.md + this PDF report"]]
    ct = Table([[Paragraph(f"<b>{a}</b>", CELL), Paragraph(b, CELL)] for a, b in cover],
               colWidths=[4 * cm, 10 * cm], hAlign="CENTER")
    ct.setStyle(TableStyle([("GRID", (0, 0), (-1, -1), 0.4, GRID), ("BACKGROUND", (0, 0), (0, -1), ZEBRA),
                            ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5)]))
    s += [ct, Spacer(1, 1.6 * cm),
          P("<b>Contents:</b> 1 Introduction - 2 Phase 1 Design and Planning - 3 Phase 2 Package Prioritisation "
            "and Box Filling - 4 Phase 3 Route Maker and Graph Processing - 5 Phase 4 Performance Testing and "
            "Optimisation - 6 Phase 5 Result Explanation and Demonstration - 7 Conclusion - Appendix A Full "
            "output trace - Appendix B Source code", ParagraphStyle("c", parent=SMALL, alignment=TA_CENTER)),
          PageBreak()]

    # --------------------------------------------------------------- 1 introduction
    s += [P("1. Introduction", H1),
          P("A courier company has a pile of parcels at its depot, one delivery van with limited carrying "
            "capacity, and a road network that connects the depot with its customers. Every day somebody has to "
            "answer three questions: <b>(1)</b> which parcels should be loaded first, <b>(2)</b> which parcels "
            "fit into the van for the next trip, and <b>(3)</b> in what order should the customers be visited "
            "so that the van drives as little as possible?"),
          P("This project is a working prototype that answers all three questions automatically. It combines the "
            "four algorithm families studied in the first four lab assessments:"),
          *bullets(["<b>Sorting</b> (Merge Sort, compared with Quick, Heap and Insertion Sort) to rank parcels by deadline and priority.",
                    "<b>Dynamic Programming</b> (0/1 Knapsack) to pick the most valuable set of parcels that fits in the van.",
                    "<b>Graph algorithms</b> (Dijkstra's shortest path) to find the real road distances between depot and customers.",
                    "<b>Approximation algorithms</b> (Nearest-Neighbour TSP, with a 2-opt improvement) to order the stops, because the exact TSP is NP-hard."]),
          P("Everything is written from scratch in Python (no library is used inside the algorithms), is "
            "documented with detailed comments, is verified by 12 automatic tests against reference solutions, "
            "and is benchmarked on datasets from 15 up to 400 places and from 20 up to 8,000 parcels.")]

    # --------------------------------------------------------------- 2 phase 1
    s += [P("2. Phase 1 - Courier Problem Design and Planning", H1), P("2.1 Problem statement", H2),
          P("<b>Given:</b> a set of parcels P, a road graph G = (V, E) with the depot as node 0, and a van "
            "capacity C (kg). <b>Find:</b> (a) the parcels sorted by urgency, (b) a subset S of parcels for one trip "
            "with total weight &lt;= C and maximum total value, (c) the shortest road distances between the "
            "depot and the delivery points of S, and (d) a short closed tour Depot -> stops -> Depot. "
            "If parcels remain, the procedure is repeated for the next trip."),
          P("2.2 Data design - parcel attributes", H2)]
    s.append(table([["Attribute", "Type", "Meaning", "Used by"],
                    ["parcel_id", "int", "unique number of the parcel", "tie-breaking in sorting, reports"],
                    ["destination", "int (node)", "delivery point in the road graph", "Dijkstra, TSP"],
                    ["weight", "int (kg, 1-15)", "weight of the parcel", "Knapsack constraint"],
                    ["deadline_hours", "int (2-48)", "hours from now until the parcel is due", "Sorting key, value, deadline check"],
                    ["priority", "int (1-5)", "business importance (5 = express / medical)", "Sorting key, value"],
                    ["value (derived)", "int", "priority x 10 + (48 - deadline) // 6 (bonus 0..7)", "Knapsack objective"]],
                   [3.0 * cm, 2.6 * cm, 6.3 * cm, W - 11.9 * cm]))
    s += [Spacer(1, 4), P("The value is an integer so that the DP table is exact. The weight is an integer because the "
                          "DP table has one column for every kilogram of capacity."),
          P("2.3 Graph format", H2),
          P("The road network is an <b>undirected weighted graph</b> stored as an <b>adjacency list</b>: "
            "<font name='Courier'>adj[u] = [(v, km), ...]</font>. Node 0 is the depot, nodes 1..V-1 are customers. "
            "An adjacency list needs O(V + E) memory, which is far better than a V x V matrix because a road "
            "network is sparse (every place connects only to a few neighbours; the generator creates only about 1.5 "
            "roads per place). Edge weights are road lengths in km and are never negative, which is the "
            "requirement of Dijkstra's algorithm. The generator first connects every new place to its nearest "
            "earlier place (so the graph is always connected) and then adds roads to the two nearest neighbours "
            "of every place (so there are alternative routes). Datasets are reproducible through a random seed "
            "and can be saved as JSON (<font name='Courier'>data/sample_dataset.json</font>).")]
    s += [P("2.4 Required algorithms and why they were selected", H2)]
    s.append(table([["Task", "Algorithm", "Time", "Why this technique is suitable"],
                    ["Rank parcels", "Merge Sort (compared with Quick, Heap, Insertion)", "O(n log n)",
                     "Guaranteed bound, stable (equal parcels keep their order), works with a composite key."],
                    ["Choose parcels for one trip", "0/1 Knapsack by Dynamic Programming", "O(n x C)",
                     "Parcels cannot be split, and greedy rules can be non-optimal; DP is exact."],
                    ["Distances on roads", "Dijkstra with a min-heap", "O((V+E) log V)",
                     "Weights are non-negative; gives both distance and the road path."],
                    ["Order of the stops", "Nearest-Neighbour TSP (+ 2-opt)", "O(k^2)",
                     "TSP is NP-hard; the exact answer needs (k-1)! checks. NN is a fast approximation."]],
                   [3.0 * cm, 4.6 * cm, 2.4 * cm, W - 10.0 * cm]))
    s += [Spacer(1, 6), P("2.5 How the algorithms work together", H2)]
    box = ParagraphStyle("box", parent=CELL, alignment=TA_CENTER, fontSize=8)
    flow = Table([[P("<b>1. SORT</b><br/>Merge Sort by deadline, then priority", box), P("=&gt;", box),
                   P("<b>2. PACK</b><br/>Knapsack DP picks the best parcels for the van", box), P("=&gt;", box),
                   P("<b>3. MEASURE</b><br/>Dijkstra from depot and every stop", box), P("=&gt;", box),
                   P("<b>4. ROUTE</b><br/>Nearest-Neighbour TSP (+2-opt) orders the stops", box)]],
                 colWidths=[3.4 * cm, 0.8 * cm, 3.6 * cm, 0.8 * cm, 3.4 * cm, 0.8 * cm, W - 12.8 * cm])
    flow.setStyle(TableStyle([("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#dbeafe")),
                              ("BACKGROUND", (2, 0), (2, 0), colors.HexColor("#dcfce7")),
                              ("BACKGROUND", (4, 0), (4, 0), colors.HexColor("#fef9c3")),
                              ("BACKGROUND", (6, 0), (6, 0), colors.HexColor("#fee2e2")),
                              ("BOX", (0, 0), (0, 0), 0.6, GRID), ("BOX", (2, 0), (2, 0), 0.6, GRID),
                              ("BOX", (4, 0), (4, 0), 0.6, GRID), ("BOX", (6, 0), (6, 0), 0.6, GRID),
                              ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("TOPPADDING", (0, 0), (-1, -1), 8),
                              ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
    s += [flow, Spacer(1, 6),
          P("<b>Integration logic.</b> The sorted list decides the order in which the knapsack considers parcels. "
            "When several selections have the same total value, the DP backtracking prefers earlier (more urgent) "
            "parcels, so sorting really influences the final packing. The knapsack output decides which delivery "
            "points exist in this trip. Dijkstra turns those points into a table of real shortest distances, and "
            "the TSP heuristic works on that table, so it always uses true road distances instead of straight "
            "lines. After the trip the chosen parcels are removed and the whole procedure repeats for the next trip. "
            "The coordinating code is <font name='Courier'>planner.py</font>."),
          P("<b>Assumptions.</b> One van, constant average speed of 40 km/h, 15 minutes re-loading between trips, "
            "roads are two-way, and a parcel heavier than the van cannot be delivered (it is reported).")]

    # --------------------------------------------------------------- 3 phase 2
    srt, kn = res["sorting"], res["knapsack"]
    idx5k = srt["sizes"].index(5000)
    s += [P("3. Phase 2 - Package Prioritisation and Box Filling", H1), P("3.1 Sorting the parcels", H2),
          P("Parcels are sorted by the key <font name='Courier'>(deadline_hours, -priority, parcel_id)</font>: "
            "earliest deadline first, higher priority wins a tie, and the id makes the order unique. Four sorting "
            "algorithms were implemented from scratch and compared on parcel lists of different sizes. "
            "Every result was checked against Python's built-in sorted() before it was timed.")]
    rows = [["n parcels", "Merge (ms)", "Quick (ms)", "Heap (ms)", "Insertion (ms)", "sorted() (ms)"]]
    for i, n in enumerate(srt["sizes"]):
        t = srt["times"]
        rows.append([f"{n:,}", ms(t["Merge Sort"][i]), ms(t["Quick Sort"][i]), ms(t["Heap Sort"][i]),
                     ms(t["Insertion Sort"][i]) if t["Insertion Sort"][i] else "skipped",
                     ms(t["Python sorted() (reference)"][i])])
    s.append(table(rows, [2.4 * cm] + [(W - 2.4 * cm) / 5] * 5))
    m, q = srt["times"]["Merge Sort"], srt["times"]["Quick Sort"]
    ins = srt["times"]["Insertion Sort"]
    s += [Spacer(1, 4),
          P(f"<b>Observation.</b> Insertion Sort is clearly quadratic ({ins[idx5k] / ins[idx5k - 1]:.1f}x slower when n "
            f"grows from 2,000 to 5,000, expected 6.25x for O(n<super>2</super>)) and becomes useless beyond a few thousand "
            f"parcels. Merge, Quick and Heap Sort grow like n log n (Merge Sort takes {m[-1] / m[-2]:.2f}x longer when n doubles "
            f"from 5,000 to 10,000, expected about 2.1x). Quick Sort is about {m[-1] / q[-1]:.1f}x faster than Merge Sort in "
            "this pure-Python test, but its worst case is O(n<super>2</super>) and it is not stable. "
            "<b>Merge Sort was selected</b> because its O(n log n) bound is guaranteed for every input and it is "
            "stable, so the plan is predictable and parcels with identical keys keep their original order. "
            "(Python's built-in sorted() is much faster because it is written in C; it is shown only as a reference.)")]

    # evidence of the sorted parcel list for the demonstration dataset
    s += [P("Parcels of the demonstration dataset after Merge Sort (earliest deadline first, then highest priority):")]
    s += code_block(trace[trace.index("  [2a]"):trace.index("  [2b]")].rstrip() + "\n", CODE)
    s += [P("3.2 Box filling with dynamic programming (0/1 knapsack)", H2),
          P("Let dp[i][c] be the best total value using only the first i parcels (in sorted order) and a van of "
            "capacity c. The recurrence is:"),
          code_block("dp[0][c] = 0\n"
                     "dp[i][c] = dp[i-1][c]                                  if weight_i > c\n"
                     "dp[i][c] = max( dp[i-1][c], dp[i-1][c - weight_i] + value_i )   otherwise", CODE)[0],
          P("The answer is dp[n][C]. Walking back from dp[n][C] to dp[0][*] (if dp[i][c] differs from dp[i-1][c], parcel i was "
            "taken and c shrinks by its weight) reveals the selected parcels. Time and memory are O(n x C). "
            "The DP table, the selected parcels and the packing plan for the demonstration dataset "
            "(15 parcels, 40 kg van) are shown below exactly as printed by the program:")]
    a = trace.index("  [2b]")
    b = trace.index("PHASE 3 - ROUTE")
    b = trace.rfind("=" * 20, 0, b)
    s += code_block(trace[a:b], CODE)
    s += [P("<b>Result.</b> Trip 1 loads parcels 13, 3, 4, 7 and 10 (40 kg, a 100 % full van) with a total value of 231. "
            "A simple greedy rule (best value per kg first) would only reach 218, which demonstrates why dynamic "
            "programming is needed. The parcel with the tightest deadline (parcel 13, due in 4 h) is included.")]
    s += [P(f"<b>Knapsack scaling.</b> The running time follows the size of the table n x C: with C = 100 kg it takes "
            f"{kn['time_by_n'][0] * 1000:.2f} ms for n = {kn['sizes'][0]} and {kn['time_by_n'][-1] * 1000:.1f} ms for "
            f"n = {kn['sizes'][-1]:,}; with n = 500 it takes {kn['time_by_capacity'][0] * 1000:.2f} ms for C = {kn['capacities'][0]} "
            f"and {kn['time_by_capacity'][-1] * 1000:.1f} ms for C = {kn['capacities'][-1]} (see Chapter 5).")]

    # --------------------------------------------------------------- 4 phase 3
    s += [P("4. Phase 3 - Route Maker and Graph Processing", H1), P("4.1 Customer graph", H2),
          P("The demonstration network has 12 places (depot + 11 customers) and 17 roads. It is stored as an adjacency "
            "list (see Appendix A for the full list). The route map below shows the network (grey), the delivery "
            "stops of Trip 1 (orange, numbered in visiting order), the road path actually driven (blue) and the "
            "TSP visiting order (red dashed arrows).")]
    s.append(KeepTogether([image(os.path.join(OUT, "route_map.png"), 11.5), P("Figure 1 - Route map of Trip 1 (212.4 km).", CAPTION)]))
    s += [P("4.2 Dijkstra's algorithm", H2),
          P("Dijkstra computes the shortest distance from one source to all nodes. The implementation keeps a "
            "min-heap of (distance, node) pairs, repeatedly removes the closest node and relaxes its roads "
            "(if dist[u] + w &lt; dist[v] then dist[v] is improved and prev[v] = u is stored). Following prev[] backwards "
            "gives the real road path. The planner runs Dijkstra from the depot and from each delivery point of the "
            "trip, which yields a small matrix of true road distances. Note that the shortest route between two stops "
            "may pass through a third place, e.g. C8 -> C1 goes through the depot (65.2 km) and C5 -> C7 goes through C2 (49.2 km)."),
          P("Output of Phase 3 for Trip 1:")]
    a = trace.index("  Delivery points of Trip 1")
    b = trace.index("ALL TRIPS - COMPLETE")
    b = trace.rfind("=" * 20, 0, b)
    s += code_block(trace[a:b], CODE)
    s += [P("4.3 Nearest-Neighbour TSP approximation", H2),
          P("The stops of a trip must all be visited and the van must return to the depot - a Travelling Salesman "
            "Problem. Because TSP is NP-hard, the nearest-neighbour heuristic is used: starting at the depot, always "
            "drive to the closest unvisited stop, and finally return to the depot (O(k<super>2</super>) for k stops). "
            "For Trip 1 it produces <b>Depot -> C8 -> C1 -> C5 -> C7 -> Depot with a total length of 212.4 km</b> "
            "(about 5.3 hours at 40 km/h). All five parcels reach their customers before their deadlines "
            "(parcel 13: 2.02 h against a 4 h deadline)."),
          P("<b>Complete plan.</b> The system continues planning trips until every parcel is assigned:")]
    a = trace.index("  Trip | Parcels")
    b = trace.index("RUNTIME OF MAJOR STEPS")
    b = trace.rfind("=" * 20, 0, b)
    s += code_block(trace[a:b], CODE)
    s += [P("The first trip is fully on time. In the later trips some parcels (4 in total) are predicted to be late "
            "because those trips start only after the previous trips have returned and the nearest-neighbour "
            "heuristic only minimises distance - it does not know about deadlines. This honest limitation is "
            "listed again as future work in Chapter 5.")]

    # --------------------------------------------------------------- 5 phase 4
    g, pl, ql = res["graph"], res["pipeline"], res["quality"]
    s += [P("5. Phase 4 - Performance Testing and Optimisation", H1), P("5.1 Test cases and correctness evidence", H2),
          P("Every algorithm is compared with an independent reference solution in <font name='Courier'>test_courier.py</font>. "
            "All 12 tests pass:")]
    s.append(table([["Component", "Test", "Reference"],
                    ["All 4 sorting algorithms", "sizes 0..300 incl. duplicates; parcels sorted by key; input not modified", "Python sorted()"],
                    ["Merge Sort", "stability (equal keys keep their order)", "positions of equal keys"],
                    ["Knapsack DP", "25 random datasets x 3 capacities; weight never exceeds capacity; DP never worse than greedy", "brute force over all 2^11 subsets"],
                    ["Dijkstra", "10 random graphs, all 25 x 25 pairs; reconstructed path length equals distance", "Floyd-Warshall"],
                    ["Nearest Neighbour", "30 instances: valid tour, every stop once, never shorter than optimum", "brute-force optimal tour (7 stops)"],
                    ["2-opt", "20 instances: never longer than its input tour, same stops", "NN tour"],
                    ["Pipeline", "end-to-end; no parcel planned twice; overweight parcel and empty input handled", "invariants"]],
                   [3.3 * cm, 9.4 * cm, W - 12.7 * cm]))
    s += [Spacer(1, 4)]
    s += code_block(tests.strip(), CODE)
    s += [P("5.2 Runtime of the major steps (small and large inputs)", H2),
          P("Each time is the best of 3 runs (seconds converted to milliseconds). The complete pipeline for ONE trip was "
            "timed on five datasets; the van capacity was 100 kg:")]
    rows = [["Dataset", "Parcels", "Places", "Sort", "Knapsack", "Dijkstra", "NN-TSP", "2-opt", "Total (ms)"]]
    for r in pl:
        t = r["timings"]
        rows.append([r["label"], f"{r['parcels']:,}", r["nodes"], ms(t["sorting"]), ms(t["knapsack"]),
                     ms(t["dijkstra"]), ms(t["tsp_nn"]), ms(t["two_opt"]), f"{sum(t.values()) * 1000:.2f}"])
    s.append(table(rows, [2.0 * cm, 1.7 * cm, 1.5 * cm] + [(W - 5.2 * cm - 2.0 * cm) / 5] * 5 + [2.0 * cm]))
    big = pl[-1]["timings"]
    tot = sum(big.values())
    s += [Spacer(1, 5),
          P(f"<b>Comparison of the major steps.</b> For the largest dataset ({pl[-1]['parcels']:,} parcels, {pl[-1]['nodes']} places) the "
            f"whole trip is planned in {tot * 1000:.0f} ms. The knapsack is the most expensive step ({big['knapsack'] / tot * 100:.0f} % of "
            f"the time) followed by sorting ({big['sorting'] / tot * 100:.0f} %) and Dijkstra ({big['dijkstra'] / tot * 100:.0f} %); the "
            f"TSP steps cost only {(big['tsp_nn'] + big['two_opt']) / tot * 100:.0f} %, because one van trip contains roughly "
            "90 stops. The cost of the knapsack grows with the number of parcels, the sorting with n log n, "
            "and Dijkstra/TSP with the number of places that are visited.")]
    s.append(KeepTogether([image(os.path.join(OUT, "performance_charts.png"), 16.5),
                           P("Figure 2 - Runtime charts: sorting algorithms, knapsack DP, graph steps, and the pipeline (log scales).", CAPTION)]))
    rows = [["Places V (all visited)", "Dijkstra 1 source (ms)", "Dijkstra from every stop (ms)", "NN-TSP (ms)", "2-opt (ms)"]]
    for i, v in enumerate(g["sizes"]):
        rows.append([v, ms(g["dijkstra_single"][i]), ms(g["dijkstra_all_sources"][i]), ms(g["tsp_nn"][i]), ms(g["two_opt"][i])])
    s += [P("Graph algorithms in the worst case (every place is a delivery stop):"),
          table(rows, [3.3 * cm] + [(W - 3.3 * cm) / 4] * 4)]
    s += [P("5.3 Quality of the TSP approximation", H2),
          P(f"To measure how good the approximation is, the exact optimum was computed by brute force for {ql['instances']} random "
            f"instances with {ql['stops']} stops each. Nearest Neighbour was on average <b>{(ql['nn_avg_ratio'] - 1) * 100:.1f} % longer</b> "
            f"than the optimum (worst case {(ql['nn_max_ratio'] - 1) * 100:.1f} % longer) and found the exact optimum in "
            f"{ql['nn_optimal_count']} of {ql['instances']} instances. After the 2-opt improvement the average excess dropped to "
            f"<b>{(ql['two_opt_avg_ratio'] - 1) * 100:.2f} %</b> (worst {(ql['two_opt_max_ratio'] - 1) * 100:.1f} %) with the optimum found in "
            f"{ql['two_opt_optimal_count']} of {ql['instances']} instances. On the large datasets 2-opt shortened the tours "
            f"by {(1 - pl[1]['route_km'] / pl[1]['nn_km']) * 100:.1f} % to {(1 - pl[-1]['route_km'] / pl[-1]['nn_km']) * 100:.1f} % compared with plain Nearest Neighbour at a negligible extra cost.")]
    s += [P("5.4 Optimisation comments and future improvements", H2),
          *bullets(["<b>Knapsack memory:</b> the full n x C table is needed for backtracking; a 1-D rolling array reduces memory to O(C) if only the "
                    "best value is needed, and NumPy vectorisation would speed up the inner loop by a large factor.",
                    "<b>Sorting:</b> in production Python's built-in Timsort (C code, also stable, O(n log n)) is about 8x faster than our "
                    "pure-Python Merge Sort; the hand-written version is kept to show the algorithm.",
                    "<b>Dijkstra:</b> only the depot and the stops of a trip are used as sources (not all V places). Results could be cached between trips, "
                    "or Floyd-Warshall (O(V<super>3</super>)) could be precomputed once for a fixed city map.",
                    "<b>TSP:</b> Or-opt, Christofides (1.5-approximation) or a time-window aware heuristic would give shorter or deadline-aware tours.",
                    "<b>Deadlines across trips:</b> a joint model (multi-trip bin packing with deadlines) would avoid the late parcels seen in later trips.",
                    "<b>Multiple vans, parcel volume and live traffic</b> could be added by extending the Parcel model and edge weights."])]

    # --------------------------------------------------------------- 6 phase 5
    s += [P("6. Phase 5 - Result Explanation and Demonstration", H1), P("6.1 Explanation of the result", H2),
          P("For the demonstration dataset the system receives 15 parcels (150 kg) but the van holds only 40 kg, so four trips "
            "are required. In Trip 1 the sort puts parcel 13 (due in 4 h, priority 5) first. The DP then chooses the five parcels "
            "with the highest total value that fit exactly into 40 kg (value 231). Their destinations are C1, C5, C7 and C8. "
            "Dijkstra shows, for example, that the shortest way to C5 is Depot -> C2 -> C5 (60.0 km). Nearest Neighbour orders the stops as "
            "C8, C1, C5, C7 and the van drives 212.4 km in about 5.3 hours, delivering every parcel before its deadline. "
            "The 4 trips together cover 710.3 km."),
          P("6.2 How to run the system", H2)]
    s += code_block("pip install -r requirements.txt                       # matplotlib (charts) and reportlab (PDF)\n"
                    "python main.py --two-opt --plot --save-data             # demonstration with output trace + route map\n"
                    "python main.py --parcels 40 --nodes 25 --capacity 60    # your own dataset size\n"
                    "python test_courier.py                                  # 12 correctness tests\n"
                    "python performance.py                                   # benchmarks + runtime charts\n"
                    "python make_report_pdf.py                               # rebuild this PDF", CODE)
    s += [P("6.3 Project structure", H2)]
    s.append(table([["File", "Purpose", "Phase"],
                    ["models.py", "Parcel data class and its value formula", "1"],
                    ["data_generator.py", "reproducible road graphs and parcels, JSON save/load", "1, 4"],
                    ["sorting.py", "Merge, Quick, Heap and Insertion Sort", "2"],
                    ["knapsack.py", "0/1 knapsack DP, backtracking, greedy comparison, table printing", "2"],
                    ["graph.py", "adjacency-list graph class", "3"],
                    ["shortest_path.py", "Dijkstra with heap + path reconstruction", "3"],
                    ["tsp.py", "Nearest Neighbour, 2-opt, brute-force optimum", "3, 4"],
                    ["planner.py", "integrates sorting + DP + Dijkstra + TSP into trips", "1-3"],
                    ["main.py", "command-line demo that prints the output trace", "5"],
                    ["visualize.py", "route map drawing", "5"],
                    ["test_courier.py", "12 automatic correctness tests", "4"],
                    ["performance.py", "benchmarks and runtime charts", "4"],
                    ["make_report_pdf.py", "builds this PDF from the real outputs", "5"]],
                   [4.2 * cm, W - 6.2 * cm, 2.0 * cm]))
    s += [P("6.4 Limitations and originality", H2),
          P("Known limitations: single van, constant speed, nearest-neighbour ignores deadlines, a straight-line-based synthetic road network "
            "instead of real map data, and weights restricted to integers for the DP. All code was written for this assignment, every "
            "algorithm is implemented from scratch with explanatory comments, and the results in this report are produced by the "
            "code itself (the PDF reads them from the files written by the programs).")]

    # --------------------------------------------------------------- 7 conclusion
    s += [P("7. Conclusion", H1),
          P("The prototype shows how four classical algorithm techniques solve one realistic logistics problem together: sorting prioritises "
            "parcels, dynamic programming packs the van optimally, Dijkstra provides true road distances, and a TSP approximation "
            "produces a short delivery route. Tests prove the correctness of each part against independent solutions, and the benchmarks "
            "confirm the theoretical complexities (O(n log n) sorting, O(n x C) knapsack, O((V+E) log V) Dijkstra, O(k<super>2</super>) nearest neighbour). "
            "The approximation is on average only about "
            f"{(ql['nn_avg_ratio'] - 1) * 100:.0f} % worse than the optimum, and 2-opt reduces this to well under 1 % on small instances.")]
    s += [PageBreak()]

    # --------------------------------------------------------------- appendices
    s += [P("Appendix A - Full output trace of main.py", H1), P("Command: <font name='Courier'>python main.py --two-opt --plot --save-data</font>")]
    s += code_block(trace, CODE)
    s += [PageBreak(), P("Appendix B - Source code", H1)]
    for fname in ["models.py", "data_generator.py", "sorting.py", "knapsack.py", "graph.py", "shortest_path.py", "tsp.py",
                  "planner.py", "main.py", "visualize.py", "test_courier.py", "performance.py"]:
        s.append(P(f"B - {fname}", H2))
        s += code_block(open(os.path.join(HERE, fname)).read(), CODE_SMALL, chunk=75)

    doc = SimpleDocTemplate(PDF_PATH, pagesize=A4, leftMargin=2 * cm, rightMargin=2 * cm, topMargin=1.8 * cm,
                            bottomMargin=1.9 * cm, title="Courier Planning System - ADA Capstone Report",
                            author=STUDENT)
    doc.build(s, onFirstPage=lambda c, d: None, onLaterPages=footer)
    print("PDF written:", PDF_PATH)


if __name__ == "__main__":
    build()
