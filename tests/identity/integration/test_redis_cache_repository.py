import pytest


@pytest.mark.asyncio
async def test_set_and_get_round_trips_dict(cache_repo, cache_key):
    value = {"id": "abc-123", "name": "Ivan", "address": None}

    await cache_repo.set(cache_key, value)
    fetched = await cache_repo.get(cache_key)

    assert fetched == value


@pytest.mark.asyncio
async def test_get_missing_key_returns_none(cache_repo, cache_key):
    assert await cache_repo.get(cache_key) is None


@pytest.mark.asyncio
async def test_delete_removes_key(cache_repo, cache_key):
    await cache_repo.set(cache_key, {"name": "Ivan"})
    assert await cache_repo.get(cache_key) is not None

    await cache_repo.delete(cache_key)

    assert await cache_repo.get(cache_key) is None


@pytest.mark.asyncio
async def test_delete_missing_key_is_safe(cache_repo, cache_key):
    await cache_repo.delete(cache_key)
