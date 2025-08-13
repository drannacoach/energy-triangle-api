from base64 import b64encode
from io import BytesIO

import matplotlib.pyplot as plt
import uvicorn
from fastapi import FastAPI
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from pydantic import BaseModel, Field


# ------------------- Plotting related definitions ----------
def convert_bytes_io_t0_base64_encoded_string(img_bytes: BytesIO) -> str:
    return b64encode(img_bytes.getvalue()).decode()


def create_3d_plot(model: "MetricsModel"):
    performance = model.performance
    people = model.people
    personal = model.personal

    triangle = [
        (people, 0, 0),  # People
        (0, personal, 0),  # Personal
        (0, 0, performance),  # Performance
    ]
    optimal = 15
    optimal_triangle = [
        (optimal, 0, 0),  # People
        (0, optimal, 0),  # Personal
        (0, 0, optimal),  # Performance
    ]

    fig = plt.figure(figsize=(12, 8))
    ax = fig.add_subplot(111, projection="3d")

    # Triangle edges
    for i in range(len(triangle)):
        p1 = triangle[i]
        p2 = triangle[(i + 1) % len(triangle)]
        ax.plot(
            [p1[0], p2[0]], [p1[1], p2[1]], [p1[2], p2[2]], color="black", linewidth=2
        )

    # Transparent face
    ax.add_collection3d(
        Poly3DCollection(
            [triangle],
            facecolors="gold",
            alpha=0.0,  # fully transparent
            edgecolors="black",
            linewidths=3,
        )
    )

    ax.add_collection3d(
        Poly3DCollection(
            [optimal_triangle],
            facecolors="cyan",
            alpha=0.0,  # fully transparent
            edgecolors="grey",
            linewidths=1,
            linestyle="dashed",
        )
    )

    # create a custom z-axis at (0,0) position with a specific range
    # add a purple line and small number markers on the line
    text_color = "black"
    ax.plot([0, 0], [0, 0], [1, optimal], color="purple", linewidth=3)
    for i in range(0, optimal + 1, 5):
        if i == 0:
            number_text_position = (0, 0, 0)
        else:
            number_text_position = (2, 0, i)
        ax.text(
            *number_text_position,
            str(i),
            color=text_color,
            fontsize=12,
            ha="center",
            va="center",
        )

    # x-axis markers and line
    ax.plot([1, optimal], [0, 0], [0, 0], color="#ffde00", linewidth=3)
    for i in range(0, optimal + 1, 5):
        if i == 0:
            continue
        ax.text(
            i + 0.5,
            -1,
            0.5,
            str(i),
            color=text_color,
            fontsize=12,
            ha="center",
            va="center",
        )

    # y-axis markers and line
    ax.plot([0, 0], [1, optimal], [0, 0], color="#666666", linewidth=3)
    for i in range(0, optimal + 1, 5):
        if i == 0:
            continue
        ax.text(
            -1,
            i + 0.5,
            0.5,
            str(i),
            color=text_color,
            fontsize=12,
            ha="center",
            va="center",
        )

    # ------------ marker lines
    marker_length = [-0.2, 0.2]
    marker_width = 3
    for axis_number in range(3):
        for i in range(0, optimal):
            if i == 0:
                continue
            if axis_number == 0:
                # for x-axis
                ax.plot(
                    [i, i],
                    marker_length,
                    [0, 0],
                    color="#ffde00",
                    linewidth=marker_width,
                )
            elif axis_number == 1:
                # for y-axis
                ax.plot(
                    marker_length,
                    [i, i],
                    [0, 0],
                    color="#666666",
                    linewidth=marker_width,
                )
            elif axis_number == 2:
                # for z-axis
                ax.plot(
                    marker_length,
                    [0, 0],
                    [i, i],
                    color="purple",
                    linewidth=marker_width,
                )
    # ------------ texts

    # x-axis text
    _position = (10, -5, 5)
    ax.text(
        *_position,
        "People Energy",
        color="#ffde00",
        fontsize=18,
        fontweight="bold",
        ha="center",
        va="center",
    )

    # z-axis text
    _position = (
        -4,
        5,
        optimal,
    )
    ax.text(
        *_position,
        "Performance Energy",
        color="purple",
        fontsize=18,
        fontweight="bold",
        ha="center",
        va="center",
    )
    _position = (-5, 5, 0)
    ax.text(
        *_position,
        "Personal Energy",
        color="#666666",
        fontsize=18,
        fontweight="bold",
        horizontalalignment="left",
        verticalalignment="baseline",
        rotation=175,
        rotation_mode="anchor",
    )

    # # Axis limits
    ax.set_xlim3d(0, optimal)
    ax.set_ylim3d(0, optimal)
    ax.set_zlim3d(0, optimal)

    # Remove axis labels
    ax.set_xlabel("")
    ax.set_ylabel("")
    ax.set_zlabel("")

    # Axis tick colors
    ax.tick_params(axis="x", colors="gold", labelsize=0)
    ax.tick_params(axis="y", colors="grey", labelsize=0)
    ax.tick_params(axis="z", colors="purple", labelsize=0)
    ax.xaxis.set_ticks([])
    ax.yaxis.set_ticks([])
    ax.zaxis.set_ticks([])
    # turn off grid lines
    ax.grid(False)

    ax.xaxis.pane.set_facecolor((1, 1, 1, 0))
    ax.yaxis.pane.set_facecolor((1, 1, 1, 0))
    ax.zaxis.pane.set_facecolor((1, 1, 1, 0))

    # draw the 3 axis in 3 different colors but hide the default ones
    ax.xaxis.line.set_color("none")
    ax.yaxis.line.set_color("none")
    ax.zaxis.line.set_color("none")

    # Remove the panes (background faces)
    ax.xaxis.pane.set_visible(False)
    ax.yaxis.pane.set_visible(False)
    ax.zaxis.pane.set_visible(False)

    # Optionally hide the ticks and labels too
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])

    # View angle
    ax.view_init(elev=30, azim=40, vertical_axis="z")

    buffer = BytesIO()
    plt.savefig(buffer, dpi=300, transparent=False)
    buffer.seek(0)

    return buffer


# ------------------- FastAPI related stuff -----------------


# Define the data model that matches the expected request body
class MetricsModel(BaseModel):
    performance: int = Field(..., description="Performance metric", ge=0)
    people: int = Field(..., description="People metric", ge=0)
    personal: int = Field(..., description="Personal metric", ge=0)

    class Config:
        schema_extra = {"example": {"performance": 10, "people": 5, "personal": 8}}


# Create the FastAPI application
app = FastAPI(title="Metrics API")


@app.post("/metrics/")
async def process_metrics(metrics: MetricsModel):
    """
    Process metrics data.

    Returns the received data and a success status.
    """
    img_bytes = create_3d_plot(metrics)
    img_base64 = convert_bytes_io_t0_base64_encoded_string(img_bytes)
    return {
        "scores": metrics.model_dump(),
        "status": "success",
        "image": img_base64,
    }


# Add a simple health check endpoint (most automation platforms need this to know the service is running)
@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
