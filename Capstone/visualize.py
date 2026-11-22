"""
visualize.py  (Phase 5 - visual evidence)
=========================================
Draws the road network and highlights the planned delivery route of a trip.
The picture is used as "screenshot evidence" in the README and the PDF report.
"""

import matplotlib
matplotlib.use("Agg")                    # draw to a file, no window needed
import matplotlib.pyplot as plt


def draw_route_map(graph, plan, filename, title=None):
    fig, ax = plt.subplots(figsize=(9, 7.5))

    # 1) all roads in light grey
    for u, v, w in graph.edge_list:
        (x1, y1), (x2, y2) = graph.coords[u], graph.coords[v]
        ax.plot([x1, x2], [y1, y2], color="#cfd4da", linewidth=1, zorder=1)

    # 2) the real road path travelled (Dijkstra paths joined together) in blue
    xs = [graph.coords[n][0] for n in plan.full_path]
    ys = [graph.coords[n][1] for n in plan.full_path]
    ax.plot(xs, ys, color="#1f77b4", linewidth=2.6, zorder=2)

    # 3) arrows showing the order in which the stops are visited (TSP route)
    for i in range(len(plan.route) - 1):
        (x1, y1) = graph.coords[plan.route[i]]
        (x2, y2) = graph.coords[plan.route[i + 1]]
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="->", color="#d62728", lw=1.3,
                                    linestyle="--", shrinkA=8, shrinkB=8,
                                    connectionstyle="arc3,rad=0.12"), zorder=3)

    # 4) nodes: plain customers grey, delivery stops orange, depot green star
    for n in range(graph.num_nodes):
        x, y = graph.coords[n]
        if n == 0:
            ax.scatter(x, y, s=330, marker="*", color="#2ca02c", zorder=5)
        elif n in plan.stops:
            ax.scatter(x, y, s=190, color="#ff7f0e", edgecolor="black", zorder=4)
        else:
            ax.scatter(x, y, s=60, color="#adb5bd", zorder=3)
        ax.annotate(graph.name(n), (x, y), textcoords="offset points",
                    xytext=(7, 7), fontsize=9, zorder=6)

    # 5) visiting order numbers next to the stops
    for order, node in enumerate(plan.route[1:-1], start=1):
        x, y = graph.coords[node]
        ax.annotate(str(order), (x, y), ha="center", va="center",
                    fontsize=8, fontweight="bold", color="white", zorder=7)

    # manual legend (clearer than automatic labels)
    from matplotlib.lines import Line2D
    handles = [
        Line2D([0], [0], marker="*", color="w", markerfacecolor="#2ca02c", markersize=16, label="Depot"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#ff7f0e", markeredgecolor="black",
               markersize=10, label="Delivery stop (number = visiting order)"),
        Line2D([0], [0], marker="o", color="w", markerfacecolor="#adb5bd", markersize=8, label="Other place"),
        Line2D([0], [0], color="#1f77b4", lw=2.6, label="Road path used (Dijkstra)"),
        Line2D([0], [0], color="#d62728", lw=1.3, linestyle="--", label="TSP visiting order"),
    ]
    ax.legend(handles=handles, loc="upper center", bbox_to_anchor=(0.5, -0.1),
              ncol=3, fontsize=8, framealpha=0.95)   # legend below the map so it hides nothing
    ax.set_title(title or f"Trip {plan.trip_no}: route length {plan.route_km:.1f} km")
    ax.set_xlabel("x (km)")
    ax.set_ylabel("y (km)")
    ax.set_aspect("equal")
    ax.grid(alpha=0.2)
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)
