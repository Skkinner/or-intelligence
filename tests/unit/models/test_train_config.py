"""Smoke tests for WBS 3.1.1 (Member B): the training config loads and matches the class contract."""

from pathlib import Path

import pytest

from src.common.contracts import class_names
from src.models.train import config_hash, load_train_config


def test_train_config_loads():
    cfg = load_train_config("configs/train.yaml")
    assert cfg["seed"] == 42
    assert cfg["data"].endswith("dataset.yaml")


def test_config_hash_is_stable():
    cfg = load_train_config("configs/train.yaml")
    assert config_hash(cfg) == config_hash(dict(cfg))


@pytest.mark.skipif(not Path("data/processed/dataset.yaml").exists(),
                    reason="needs data/processed/dataset.yaml from Member A (2.2.2)")
def test_dataset_names_match_contract():
    import yaml

    names = yaml.safe_load(Path("data/processed/dataset.yaml").read_text())["names"]
    names = [names[k] for k in sorted(names)] if isinstance(names, dict) else names
    assert names == class_names()
