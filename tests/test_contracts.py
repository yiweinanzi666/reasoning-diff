import pytest
import numpy as np
from reasoning_diff.schema import Task, Premise, Node, canonical_value
from reasoning_diff.events import parse_events, align_events, boundary_index
from reasoning_diff.measurement import dependency_densities, lcs_overlap
from reasoning_diff.splits import assign_split, assert_disjoint


def task():
    return Task("a", "a", "fixture", "p = 2", [Premise("p", "p = 2", 0, 5, "2")],
                [Node("q", ["p"], "4", ["q"], "p+p")], "q", "4")


def test_transitive_labels_and_cycle_rejection():
    item = task()
    item.nodes.append(Node("r", ["q"], "8"))
    assert item.ancestors()["r"] == {"p"}
    item.nodes[0].parents = ["r"]
    with pytest.raises(ValueError):
        item.validate()


def test_identity_does_not_use_values_and_repetition_is_versioned():
    a = parse_events("q = 4\nq = 5", task())
    b = parse_events("q = 6\nq = 7", task())
    assert len(align_events(a, b)["pairs"]) == 2
    assert a[0].identity != a[1].identity
    assert a[0].correct and not a[1].correct


def test_prospective_boundary_excludes_straddling_token():
    assert boundary_index([[0, 2], [2, 8], [8, 9]], 6) == 0
    assert boundary_index([[0, 2]], 0) is None


def test_empty_and_signed_densities():
    result = dependency_densities(np.array([[0, 1]]), np.array([[0, -1]]), np.array([[1, -1]]))
    assert result["rho_S_excess"] == -1
    assert result["rho_M_raw"] is None
    assert result["support_cells"] == 1


def test_values_lcs_and_split_isolation():
    assert canonical_value("1/2") == canonical_value("0.5")
    assert lcs_overlap([1, 2], [1, 3]) == 0.5
    assert lcs_overlap([], []) is None
    assert assign_split("same-family") == assign_split("same-family")
    with pytest.raises(ValueError):
        assert_disjoint({"train": {"a"}, "test": {"a"}})
