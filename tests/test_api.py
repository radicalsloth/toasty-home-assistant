"""Exercise actual HTTP behavior without importing Home Assistant."""
import importlib.util
from pathlib import Path
import sys
import types
import unittest
import aiohttp
from aiohttp import web

folder = Path(__file__).resolve().parents[1] / 'custom_components/toasty'
package = types.ModuleType('toasty_client_test')
package.__path__ = [str(folder)]
sys.modules[package.__name__] = package
spec = importlib.util.spec_from_file_location('toasty_client_test.api', folder / 'api.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class ApiTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.status = 200
        self.payload = {'accountId': 'account', 'screens': [], 'applets': []}
        self.requests = []
        async def handle(request):
            self.requests.append((request.method, request.path, request.headers.get('Authorization'), await request.json() if request.method == 'POST' else None))
            return web.json_response(self.payload, status=self.status)
        app = web.Application()
        app.router.add_route('*', '/{tail:.*}', handle)
        self.runner = web.AppRunner(app)
        await self.runner.setup()
        site = web.TCPSite(self.runner, '127.0.0.1', 0)
        await site.start()
        self.original_url = module.BASE_URL
        module.BASE_URL = f'http://127.0.0.1:{site._server.sockets[0].getsockname()[1]}'
        self.session = aiohttp.ClientSession()
        self.api = module.ToastyApi(self.session, 'test-key')

    async def asyncTearDown(self):
        await self.session.close()
        await self.runner.cleanup()
        module.BASE_URL = self.original_url

    async def test_discovery_uses_bearer_and_returns_snapshot(self):
        self.assertEqual(await self.api.snapshot(), self.payload)
        self.assertEqual(self.requests, [('GET', '/api/v1/screens', 'Bearer test-key', None)])

    async def test_select_sends_only_applet(self):
        self.payload = {'screenId': 'bedroom', 'activeApp': 'earth'}
        self.assertEqual((await self.api.set_applet('bedroom', 'earth'))['activeApp'], 'earth')
        self.assertEqual(self.requests[0], ('POST', '/api/v1/screens/bedroom', 'Bearer test-key', {'activeApp': 'earth'}))

    async def test_revoked_key_has_distinct_auth_error(self):
        for status in (401, 403):
            self.status = status
            with self.assertRaises(module.ToastyAuthError):
                await self.api.snapshot()

    async def test_outage_is_not_auth_failure(self):
        self.status = 503
        with self.assertRaises(module.ToastyError) as caught:
            await self.api.snapshot()
        self.assertNotIsInstance(caught.exception, module.ToastyAuthError)
        self.assertNotIn('test-key', str(caught.exception))

    async def test_malformed_snapshot_rejected(self):
        self.payload = {'screens': []}
        with self.assertRaises(module.ToastyError):
            await self.api.snapshot()
