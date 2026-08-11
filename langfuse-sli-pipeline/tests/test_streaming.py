"""Streaming aggregation must be byte-for-byte equivalent to the batch path, the
pipeline must consume a lazy iterator, --max-records must cap safely, and the
quality accumulator must match the batch scorer below its reservoir cap."""

from __future__ import annotations


from gateway_sli.config import Config
from gateway_sli.models import parse_observation
from gateway_sli.pipeline import run
from gateway_sli.quality import QualityAccumulator, group_completion_lengths, score_group
from gateway_sli.sli import Aggregator, _HistAcc, _hist_percentile, aggregate


class _IterOnlySource:
    """Source exposing ONLY iter_records() to prove the pipeline streams."""

    def __init__(self, rows):
        self._rows = rows
        self.read_calls = 0

    def iter_records(self):
        for row in self._rows:
            yield row


class _ListSource:
    def __init__(self, rows):
        self._rows = rows

    def read(self):
        return list(self._rows)


def _rows(make_raw, n):
    rows = []
    for i in range(n):
        rows.append(
            make_raw(
                id=f"obs-{i}",
                output={"usage": {"totalTokens": 100 + i, "completionTokens": 10 + (i % 7)}},
            )
        )
    return rows


def test_aggregator_matches_batch(make_raw):
    cfg = Config()
    observations = [parse_observation(r) for r in _rows(make_raw, 40)]
    batch_points, batch_stats = aggregate(observations, 0, cfg)

    agg = Aggregator(cfg)
    for obs in observations:
        agg.add(obs)
    stream_points, stream_stats = agg.build(0)

    assert [(p.name, p.type, p.dims, p.value) for p in stream_points] == [
        (p.name, p.type, p.dims, p.value) for p in batch_points
    ]
    assert stream_stats.observations == batch_stats.observations
    assert stream_stats.errors == batch_stats.errors


def test_histogram_estimate_uses_observed_edges_not_zero():
    acc = _HistAcc((100.0, 500.0))
    for value in (20.0, 20.0):
        acc.add(value)
    assert _hist_percentile(acc, 95) == 20.0


def test_pipeline_streams_from_iterator(make_raw):
    rows = _rows(make_raw, 25)
    src = _IterOnlySource(rows)
    result = run(src, Config())
    assert result.stats.records_read == 25
    assert result.stats.observations == 25
    assert result.stats.read_truncated is False


def test_max_records_truncates(make_raw):
    rows = _rows(make_raw, 100)
    src = _IterOnlySource(rows)
    result = run(src, Config(), max_records=10)
    assert result.stats.records_read == 10
    assert result.stats.observations == 10
    assert result.stats.read_truncated is True
    names = [p.name for p in result.points]
    assert "gateway.pipeline.read_truncated" in names


def test_no_truncation_flag_when_under_cap(make_raw):
    rows = _rows(make_raw, 5)
    result = run(_IterOnlySource(rows), Config(), max_records=1000)
    assert result.stats.read_truncated is False
    names = [p.name for p in result.points]
    assert "gateway.pipeline.read_truncated" not in names


def test_quality_accumulator_matches_batch(make_raw):
    cfg = Config()
    observations = [parse_observation(r) for r in _rows(make_raw, 60)]
    groups = group_completion_lengths(observations, cfg)
    batch = {k: score_group(v, cfg.anomaly) for k, v in groups.items()}

    acc = QualityAccumulator(cfg)
    for obs in observations:
        acc.add(obs)
    stream = acc.results()

    assert set(stream.keys()) == set(batch.keys())
    for key in batch:
        assert stream[key].status == batch[key].status
        assert stream[key].anomaly_count == batch[key].anomaly_count


def test_reservoir_is_bounded(make_raw):
    cfg = Config()
    acc = QualityAccumulator(cfg, sample_cap=100)
    for i in range(5000):
        acc.add(
            parse_observation(
                make_raw(
                    id=f"r-{i}",
                    output={"usage": {"totalTokens": 50, "completionTokens": 5 + (i % 3)}},
                )
            )
        )
    for samples in acc.groups.values():  # bounded reservoir per group
        assert len(samples) <= 100
