from typing import Any

from httpx import AsyncClient

PRODUCTS = "/api/v1/products"


def product_payload(**overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {"sku": "LAP-001", "name": "Laptop", "unit_price": "1200.50"}
    return payload | overrides


async def create_products(client: AsyncClient, *products: dict[str, Any]) -> None:
    for product in products:
        response = await client.post(PRODUCTS, json=product_payload(**product))
        assert response.status_code == 201


async def list_skus(client: AsyncClient, **params: Any) -> list[str]:
    response = await client.get(PRODUCTS, params=params)
    assert response.status_code == 200
    return [product["sku"] for product in response.json()["items"]]


# --- create / get / update ---------------------------------------------------


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


# --- list: pagination, filters, sorting --------------------------------------


async def test_list_returns_page_with_total(client: AsyncClient) -> None:
    await create_products(client, *({"sku": f"SKU-{n}"} for n in range(3)))

    response = await client.get(
        PRODUCTS, params={"limit": 2, "offset": 1, "sort_by": "sku", "sort_order": "asc"}
    )

    body = response.json()
    assert body["total"] == 3
    assert body["offset"] == 1
    assert body["limit"] == 2
    assert [product["sku"] for product in body["items"]] == ["SKU-1", "SKU-2"]


async def test_search_matches_name_or_sku_case_insensitive(client: AsyncClient) -> None:
    await create_products(
        client,
        {"sku": "LAP-1", "name": "Gaming Laptop"},
        {"sku": "MOU-1", "name": "Wireless Mouse"},
        {"sku": "XLAPTOP", "name": "Stand"},
    )

    skus = await list_skus(client, search="laptop", sort_by="sku", sort_order="asc")

    assert skus == ["LAP-1", "XLAPTOP"]


async def test_search_treats_percent_as_literal(client: AsyncClient) -> None:
    await create_products(client, {"sku": "A-1", "name": "50% discount bin"}, {"sku": "A-2"})

    assert await list_skus(client, search="%") == ["A-1"]


async def test_filter_by_price_range_and_active(client: AsyncClient) -> None:
    await create_products(
        client,
        {"sku": "CHEAP", "unit_price": "5"},
        {"sku": "MID", "unit_price": "50"},
        {"sku": "PRICEY", "unit_price": "500"},
    )
    mid = (await client.get(PRODUCTS, params={"search": "MID"})).json()["items"][0]
    await client.patch(f"{PRODUCTS}/{mid['id']}", json={"is_active": False})

    skus = await list_skus(client, min_price="10", max_price="1000", is_active="true")

    assert skus == ["PRICEY"]


async def test_sort_by_price_descending(client: AsyncClient) -> None:
    await create_products(
        client,
        {"sku": "B", "unit_price": "20"},
        {"sku": "A", "unit_price": "30"},
        {"sku": "C", "unit_price": "10"},
    )

    assert await list_skus(client, sort_by="unit_price", sort_order="desc") == ["A", "B", "C"]


async def test_invalid_list_params_return_422(client: AsyncClient) -> None:
    bad_requests = [
        {"min_price": "100", "max_price": "10"},
        {"sort_by": "password"},
        {"limit": "1000"},
        {"unexpected": "x"},
    ]
    for params in bad_requests:
        response = await client.get(PRODUCTS, params=params)
        assert response.status_code == 422, params
