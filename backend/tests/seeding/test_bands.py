from tests.seeding.conftest import SeedDataset


def test_bands_are_ordered_and_unique(seeded_dataset: SeedDataset) -> None:
    bands = seeded_dataset.bands
    keys = {(band["title"], band["level"], band["country"]) for band in bands}

    assert len(bands) == len(keys)
    assert all(band["min_minor"] <= band["mid_minor"] <= band["max_minor"] for band in bands)
