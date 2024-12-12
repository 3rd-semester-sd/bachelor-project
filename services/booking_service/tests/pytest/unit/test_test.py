

def test_addition() -> None:
    """Test basic addition."""
    assert 1 + 1 == 2


def test_subtraction() -> None:
    """Test basic subtraction."""
    assert 5 - 3 == 2


def test_multiplication() -> None:
    """Test basic multiplication."""
    assert 2 * 3 == 6


def test_division() -> None:
    """Test basic division."""
    assert 8 / 2 == 4


def test_uppercase() -> None:
    """Test string uppercasing."""
    assert "hello".upper() == "HELLO"


# @pytest.mark.anyio
# async def test_client(client: AsyncClient) -> None:
#     """Test client."""
#     response = await client.get("/health")
#     assert response.status_code == 200
