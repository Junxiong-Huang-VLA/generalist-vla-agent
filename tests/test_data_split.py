from generalist_vla_agent.data.splits import SplitSpec, split_rows


def test_split_rows_has_expected_sizes() -> None:
    rows = [{"idx": i} for i in range(100)]
    splits = split_rows(rows, spec=SplitSpec(0.8, 0.1, 0.1), seed=7)
    assert len(splits["train"]) == 80
    assert len(splits["val"]) == 10
    assert len(splits["test"]) == 10


def test_split_rows_is_deterministic_for_seed() -> None:
    rows = [{"idx": i} for i in range(50)]
    a = split_rows(rows, seed=13)
    b = split_rows(rows, seed=13)
    assert a["train"][0]["idx"] == b["train"][0]["idx"]
