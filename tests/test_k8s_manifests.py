import pathlib

import pytest
import yaml

K8S_DIR = pathlib.Path(__file__).resolve().parent.parent / "k8s"


@pytest.mark.parametrize(
    "manifest_name, expected_kind",
    [
        ("deployment.yaml", "Deployment"),
        ("deployment-canary.yaml", "Deployment"),
        ("service.yaml", "Service"),
        ("hpa.yaml", "HorizontalPodAutoscaler"),
    ],
)
def test_k8s_manifests_load(manifest_name, expected_kind):
    path = K8S_DIR / manifest_name
    assert path.exists(), f"Manifest {manifest_name} missing"
    with path.open(encoding="utf-8") as handle:
        manifest = yaml.safe_load(handle)
    assert manifest["kind"] == expected_kind
    metadata = manifest.get("metadata", {})
    assert "name" in metadata and metadata["name"], "metadata.name required"


def test_canary_deployment_track_label():
    path = K8S_DIR / "deployment-canary.yaml"
    with path.open(encoding="utf-8") as handle:
        manifest = yaml.safe_load(handle)
    labels = manifest["spec"]["template"]["metadata"]["labels"]
    assert labels.get("track") == "canary"


def test_hpa_targets_deployment():
    path = K8S_DIR / "hpa.yaml"
    with path.open(encoding="utf-8") as handle:
        manifest = yaml.safe_load(handle)
    target = manifest["spec"]["scaleTargetRef"]
    assert target["kind"] == "Deployment"
    assert target["name"] == "api-factory"
