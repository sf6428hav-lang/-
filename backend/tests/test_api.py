import pytest
import json
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_root_page(client):
    resp = await client.get('/')
    assert resp.status_code == 200

@pytest.mark.asyncio
async def test_get_settings(client):
    resp = await client.get('/api/settings')
    assert resp.status_code == 200
    data = resp.json()
    assert 'api_base_url' in data
    assert 'api_key' in data

@pytest.mark.asyncio
async def test_update_settings(client):
    resp = await client.put('/api/settings', json={
        'api_base_url': 'https://new-api.example.com',
        'api_key': 'new-test-key',
        'prompt_template': 'default'
    })
    assert resp.status_code == 200
    assert resp.json()['message'] == 'Settings saved'

@pytest.mark.asyncio
async def test_get_empty_history(client):
    resp = await client.get('/api/history')
    assert resp.status_code == 200
    data = resp.json()
    assert 'items' in data
    assert 'total' in data
    assert data['total'] == 0

@pytest.mark.asyncio
async def test_get_nonexistent_script(client):
    resp = await client.get('/api/scripts/nonexistent-id')
    assert resp.status_code == 404

@pytest.mark.asyncio
async def test_delete_nonexistent_script(client):
    resp = await client.delete('/api/history/nonexistent-id')
    assert resp.status_code == 404
