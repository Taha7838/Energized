# tests/test_health.py
import subprocess
import pytest
import requests


@pytest.fixture(scope="session", autouse=True)
def compose_stack():
    """
    Spin up the full stack before the test session and tear it down after.

    --wait tells Compose to block until all containers pass their healthchecks,
    so by the time tests run, every service is genuinely ready — no sleep/retry
    logic needed here.

    --env-file .env is required so GEMINI_API_KEY, TAVILY_API_KEY, and
    DOCKERHUB_USERNAME are available to the containers at runtime.
    """
    up_result = subprocess.run(
        ["docker", "compose", "--env-file", ".env", "up", "-d", "--wait"],
        capture_output=True,
        text=True,
    )
    if up_result.returncode != 0:
        pytest.fail(
            f"docker compose up failed:\n"
            f"STDOUT: {up_result.stdout}\n"
            f"STDERR: {up_result.stderr}"
        )

    yield

    subprocess.run(
        ["docker", "compose", "down"],
        capture_output=True,
        text=True,
    )


def test_rag_health():
    """RAG backend health check routed through nginx → /rag/api/health"""
    response = requests.get("http://localhost/rag/api/health", timeout=10)
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Body: {response.text}"
    )
    body = response.json()
    assert body.get("status") == "ok", (
        f"Unexpected body: {body}"
    )


def test_agent_health():
    """Agent backend health check routed through nginx → /api/health"""
    response = requests.get("http://localhost/api/health", timeout=10)
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Body: {response.text}"
    )
    body = response.json()
    assert body.get("status") == "ok", (
        f"Unexpected body: {body}"
    )


def test_frontend_health():
    """Frontend reachable through nginx → /"""
    response = requests.get("http://localhost/", timeout=10)
    assert response.status_code == 200, (
        f"Expected 200, got {response.status_code}. Body: {response.text[:200]}"
    )