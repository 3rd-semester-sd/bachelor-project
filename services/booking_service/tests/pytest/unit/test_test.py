from httpx import AsyncClient
import pytest


def test_addition():
    """Test basic addition."""
    assert 1 + 1 == 2


def test_subtraction():
    """Test basic subtraction."""
    assert 5 - 3 == 2


def test_multiplication():
    """Test basic multiplication."""
    assert 2 * 3 == 6


def test_division():
    """Test basic division."""
    assert 8 / 2 == 4


def test_uppercase():
    """Test string uppercasing."""
    assert "hello".upper() == "HELLO"


@pytest.mark.anyio
async def test_client(client: AsyncClient) -> None:
    """Test client."""
    response = await client.get("/health")
    assert response.status_code == 200
