from tests.seeding.conftest import generate_dataset


def test_same_seed_generates_identical_data() -> None:
    assert generate_dataset(seed=42, count=500) == generate_dataset(seed=42, count=500)


def test_different_seeds_generate_different_data() -> None:
    assert generate_dataset(seed=42, count=500) != generate_dataset(seed=43, count=500)
