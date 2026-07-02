from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

import inference_control_plane.db.session
from inference_control_plane.core.security import get_auth_context
from inference_control_plane.main import app
from inference_control_plane.services.auth import AuthContext


@pytest.fixture
def auth_headers():
    return {"x-api-key": "test-key"}


@pytest.fixture
def transport():
    return ASGITransport(app=app)


@pytest.mark.asyncio
async def test_health_live(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_health_ready_success(transport):
    with patch("inference_control_plane.api.routes.get_db_session") as mock_get_session:
        mock_session = AsyncMock()
        mock_get_session.return_value = mock_session

        with patch("inference_control_plane.api.routes.ping_redis", return_value=True):
            app.dependency_overrides[inference_control_plane.db.session.get_db_session] = lambda: mock_session

            try:
                async with AsyncClient(transport=transport, base_url="http://test") as ac:
                    response = await ac.get("/health/ready")
                assert response.status_code == 200
                assert response.json() == {"status": "ready"}
            finally:
                app.dependency_overrides.pop(inference_control_plane.db.session.get_db_session)


@pytest.mark.asyncio
async def test_health_ready_db_fail(transport):
    mock_session = AsyncMock()
    mock_session.execute.side_effect = Exception("db fail")

    app.dependency_overrides[inference_control_plane.db.session.get_db_session] = lambda: mock_session

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/health/ready")
        assert response.status_code == 503
        assert "not-ready" in response.text
        assert "database" in response.text
    finally:
        app.dependency_overrides.pop(inference_control_plane.db.session.get_db_session)


@pytest.mark.asyncio
async def test_health_ready_redis_fail(transport):
    mock_session = AsyncMock()

    app.dependency_overrides[inference_control_plane.db.session.get_db_session] = lambda: mock_session

    with patch("inference_control_plane.api.routes.ping_redis", return_value=False):
        try:
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get("/health/ready")
            assert response.status_code == 503
            assert "not-ready" in response.text
            assert "database" in response.text
        finally:
            app.dependency_overrides.pop(inference_control_plane.db.session.get_db_session)


@pytest.mark.asyncio
async def test_metrics(transport):
    with patch("inference_control_plane.api.routes.generate_latest", return_value=b"test metrics"):
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/metrics")
        assert response.status_code == 200
        assert response.content == b"test metrics"






@pytest.mark.asyncio
async def test_generate_route(transport):
    mock_auth = AuthContext(tenant_id="t-1", api_key_hash="hash", rate_limit_per_minute=100, role="tenant")
    app.dependency_overrides[get_auth_context] = lambda: mock_auth

    with patch("inference_control_plane.api.routes.handle_generate_request") as mock_handle:
        mock_handle.return_value = {
            "request_id": "123",
            "response": "resp",
            "model_used": "model",
            "cached": False,
            "latency_ms": 1.0,
            "tokens": 10,
            "cost": 0.01,
            "timestamp": "2024-01-01T00:00:00Z",
        }

        try:
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.post("/generate", json={"prompt": "test", "user_id": "u-1"})
            assert response.status_code == 200
        finally:
            app.dependency_overrides.pop(get_auth_context)




@pytest.mark.asyncio
async def test_usage_summary_route(transport):
    mock_auth = AuthContext(tenant_id="t-1", api_key_hash="hash", rate_limit_per_minute=100, role="admin")
    app.dependency_overrides[get_auth_context] = lambda: mock_auth
    app.dependency_overrides[inference_control_plane.db.session.get_db_session] = lambda: AsyncMock()

    with patch("inference_control_plane.api.routes.get_usage_summary") as mock_summary:
        mock_summary.return_value = {
            "user_id": "u-1",
            "requests": 1,
            "total_tokens": 10,
            "total_cost": 0.01,
        }
        try:
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get("/usage/summary?user_id=u-1")
            assert response.status_code == 200
        finally:
            app.dependency_overrides.pop(get_auth_context)


@pytest.mark.asyncio
async def test_usage_summary_route_forbidden(transport):
    mock_auth = AuthContext(tenant_id="t-1", api_key_hash="hash", rate_limit_per_minute=100, role="tenant")
    app.dependency_overrides[get_auth_context] = lambda: mock_auth
    app.dependency_overrides[inference_control_plane.db.session.get_db_session] = lambda: AsyncMock()

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/usage/summary?user_id=u-1")
        assert response.status_code == 403
    finally:
        app.dependency_overrides.pop(get_auth_context)


@pytest.mark.asyncio
async def test_usage_logs_route(transport):
    mock_auth = AuthContext(tenant_id="t-1", api_key_hash="hash", rate_limit_per_minute=100, role="admin")
    app.dependency_overrides[get_auth_context] = lambda: mock_auth
    app.dependency_overrides[inference_control_plane.db.session.get_db_session] = lambda: AsyncMock()

    with patch("inference_control_plane.api.routes.get_usage_logs") as mock_logs:
        mock_logs.return_value = {"user_id": "u-1", "limit": 10, "entries": []}
        try:
            async with AsyncClient(transport=transport, base_url="http://test") as ac:
                response = await ac.get("/usage/logs?user_id=u-1")
            assert response.status_code == 200
        finally:
            app.dependency_overrides.pop(get_auth_context)


@pytest.mark.asyncio
async def test_usage_logs_route_forbidden(transport):
    mock_auth = AuthContext(tenant_id="t-1", api_key_hash="hash", rate_limit_per_minute=100, role="tenant")
    app.dependency_overrides[get_auth_context] = lambda: mock_auth
    app.dependency_overrides[inference_control_plane.db.session.get_db_session] = lambda: AsyncMock()

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/usage/logs?user_id=u-1")
        assert response.status_code == 403
    finally:
        app.dependency_overrides.pop(get_auth_context)


@pytest.mark.asyncio
async def test_dashboard_metrics(transport):
    mock_auth = AuthContext(tenant_id="t-1", api_key_hash="hash", rate_limit_per_minute=100, role="admin")
    app.dependency_overrides[get_auth_context] = lambda: mock_auth

    mock_session = AsyncMock()
    app.dependency_overrides[inference_control_plane.db.session.get_db_session] = lambda: mock_session

    # Needs to return scalars for sum/count
    mock_execute = MagicMock()
    mock_execute.scalar.side_effect = [100, 1.5, 50, 15.2]
    mock_session.execute = AsyncMock(return_value=mock_execute)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/dashboard/metrics")
        assert response.status_code == 200
        assert len(response.json()["metrics"]) == 4
    finally:
        app.dependency_overrides.pop(get_auth_context)
        app.dependency_overrides.pop(inference_control_plane.db.session.get_db_session)


@pytest.mark.asyncio
async def test_dashboard_metrics_forbidden(transport):
    mock_auth = AuthContext(tenant_id="t-1", api_key_hash="hash", rate_limit_per_minute=100, role="tenant")
    app.dependency_overrides[get_auth_context] = lambda: mock_auth
    app.dependency_overrides[inference_control_plane.db.session.get_db_session] = lambda: AsyncMock()

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/dashboard/metrics")
        assert response.status_code == 403
    finally:
        app.dependency_overrides.pop(get_auth_context)


@pytest.mark.asyncio
async def test_dashboard_activity(transport):
    mock_auth = AuthContext(tenant_id="t-1", api_key_hash="hash", rate_limit_per_minute=100, role="admin")
    app.dependency_overrides[get_auth_context] = lambda: mock_auth

    mock_session = AsyncMock()
    app.dependency_overrides[inference_control_plane.db.session.get_db_session] = lambda: mock_session

    mock_execute = MagicMock()
    mock_execute.scalars.return_value.all.return_value = []
    mock_session.execute = AsyncMock(return_value=mock_execute)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/dashboard/activity")
        assert response.status_code == 200
        assert response.json()["activity"] == ["System operating normally."]
    finally:
        app.dependency_overrides.pop(get_auth_context)
        app.dependency_overrides.pop(inference_control_plane.db.session.get_db_session)


@pytest.mark.asyncio
async def test_dashboard_activity_forbidden(transport):
    mock_auth = AuthContext(tenant_id="t-1", api_key_hash="hash", rate_limit_per_minute=100, role="tenant")
    app.dependency_overrides[get_auth_context] = lambda: mock_auth
    app.dependency_overrides[inference_control_plane.db.session.get_db_session] = lambda: AsyncMock()

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            response = await ac.get("/dashboard/activity")
        assert response.status_code == 403
    finally:
        app.dependency_overrides.pop(get_auth_context)
