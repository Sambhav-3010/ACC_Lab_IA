from lbml.workload import generate_workload


def test_workload_is_reproducible():
    assert generate_workload("E3", 30, 7).equals(generate_workload("E3", 30, 7))


def test_workload_has_positive_work():
    frame = generate_workload("E1", 30, 2)
    assert not frame.empty
    assert (frame["work_cpu_ms"] > 0).all()
