from gateway_sli.config import Config
from gateway_sli.pipeline import run
from gateway_sli.sources.file_source import FileTraceSource


DEMO = "data/demo_runaway_traces.json"


def test_runaway_demo_closes_data_story_to_monitor_loop():
    result = run(FileTraceSource(DEMO), Config())
    points = [
        point
        for point in result.points
        if point.name == "gateway.tokens.completion_ratio"
        and point.dims.get("team") == "DevAgent"
        and point.dims.get("route") == "devagent-task"
    ]
    assert len(points) == 1
    assert points[0].value == 4.2
    assert points[0].value > 3
