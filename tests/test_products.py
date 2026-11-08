from typing import Any

from httpx import AsyncClient

PRODUCTS = "/api/v1/products"


def product_payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {"sku": "LAP-001", "name": "Laptop", "unit_price": "1200.50"}
    return payload | overrides


async def test_create_product_returns_201_with_body(client: AsyncClient) -> None:
    response = await client.post(PRODUCTS, json=product_payload())

    assert response.status_code == 201
    body = response.json()
    assert body["id"] > 0
    assert body["sku"] == "LAP-001"
    assert body["unit_price"] == "1200.50"
    assert body["is_active"] is True


async def test_create_product_trims_sku(client: AsyncClient) -> None:
    response = await client.post(PRODUCTS, json=product_payload(sku="  LAP-002  "))

    assert response.json()["sku"] == "LAP-002"


async def test_create_duplicate_sku_returns_409_problem(client: AsyncClient) -> None:
    await client.post(PRODUCTS, json=product_payload())

    response = await client.post(PRODUCTS, json=product_payload(name="Another"))

    assert response.status_code == 409
    assert response.headers["content-type"] == "application/problem+json"
    assert response.json()["title"] == "Conflict"


async def test_create_invalid_product_returns_422(client: AsyncClient) -> None:
    response = await client.post(PRODUCTS, json=product_payload(sku="", unit_price="-1"))

    assert response.status_code == 422
    invalid_fields = {error["loc"][-1] for error in response.json()["detail"]}
    assert invalid_fields == {"sku", "unit_price"}


async def test_get_missing_product_returns_404(client: AsyncClient) -> None:
    response = await client.get(f"{PRODUCTS}/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Product 999999 was not found."


async def test_patch_updates_only_sent_fields(client: AsyncClient) -> None:
    created = (await client.post(PRODUCTS, json=product_payload())).json()

    response = await client.patch(f"{PRODUCTS}/{created['id']}", json={"unit_price": "999.00"})

    assert response.status_code == 200
    assert response.json()["unit_price"] == "999.00"
    assert response.json()["name"] == "Laptop"


async def test_list_respects_limit(client: AsyncClient) -> None:
    for number in range(3):
        await client.post(PRODUCTS, json=product_payload(sku=f"SKU-{number}"))

    response = await client.get(PRODUCTS, params={"limit": 2})

    assert response.status_code == 200
    assert [product["sku"] for product in response.json()] == ["SKU-0", "SKU-1"]
