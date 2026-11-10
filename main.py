import unittest
import uuid
import random
import cloudscraper

# ---------- API-клиент ----------





class BaseRequest:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip('/')
        self.scraper = cloudscraper.create_scraper(
            browser='chrome',
            delay=5
        )

    def _request(self, url, method, data=None, params=None,
                 expected_error=False, retries=3):
        response = None
        for _ in range(retries):
            if method == 'GET':
                response = self.scraper.get(url, params=params)
            elif method == 'POST':
                response = self.scraper.post(url, json=data)
            elif method == 'PUT':
                response = self.scraper.put(url, json=data)
            elif method == 'DELETE':
                response = self.scraper.delete(url)
            else:
                raise ValueError(method)

            if expected_error or response.status_code == 200:
                break

        return response

    # ---- публичные методы, которых не хватало ----
    def get(self, path, params=None, expected_error=False):
        return self._request(f'{self.base_url}/{path}', 'GET',
                             params=params, expected_error=expected_error)

    def post(self, path, body, expected_error=False):
        return self._request(f'{self.base_url}/{path}', 'POST',
                             data=body, expected_error=expected_error)

    def put(self, path, body, expected_error=False):
        return self._request(f'{self.base_url}/{path}', 'PUT',
                             data=body, expected_error=expected_error)

    def delete(self, path, expected_error=False):
        return self._request(f'{self.base_url}/{path}', 'DELETE',
                             expected_error=expected_error)

# ---------- Тесты ----------

BASE_URL_PETSTORE = 'https://petstore.swagger.io/v2'


class TestPetstoreApi(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.api = BaseRequest(BASE_URL_PETSTORE)

    # ----- фабрики данных -----

    def make_user(self):
        return {
            'id': 0,
            'username': f'user_{uuid.uuid4().hex[:8]}',
            'firstName': 'Test',
            'lastName': 'User',
            'email': 'test@example.com',
            'password': 'qwerty123',
            'phone': '+70000000000',
            'userStatus': 1,
        }

    def make_order(self):
        return {
            'id': random.randint(10_000, 99_999),
            'petId': 1,
            'quantity': 1,
            'shipDate': '2025-01-01T00:00:00.000Z',
            'status': 'placed',
            'complete': False,
        }

    # ================= USER =================

    def test_user_01_create(self):
        user = self.make_user()
        resp = self.api.post('user', user)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('message', resp.json())
        # cleanup
        self.api.delete(f"user/{user['username']}", expected_error=True)

    def test_user_02_get(self):
        user = self.make_user()
        self.api.post('user', user)
        try:
            resp = self.api.get(f"user/{user['username']}")
            self.assertEqual(resp.status_code, 200)
            body = resp.json()
            self.assertEqual(body['username'], user['username'])
            self.assertEqual(body['email'], user['email'])
        finally:
            self.api.delete(f"user/{user['username']}", expected_error=True)

    def test_user_03_update(self):
        user = self.make_user()
        self.api.post('user', user)
        try:
            updated = dict(user, firstName='Updated', email='new@example.com')
            resp = self.api.put(f"user/{user['username']}", updated)
            self.assertEqual(resp.status_code, 200)

            check = self.api.get(f"user/{user['username']}")
            self.assertEqual(check.status_code, 200)
            self.assertEqual(check.json()['firstName'], 'Updated')
            self.assertEqual(check.json()['email'], 'new@example.com')
        finally:
            self.api.delete(f"user/{user['username']}", expected_error=True)

    def test_user_04_delete(self):
        user = self.make_user()
        self.api.post('user', user)

        resp = self.api.delete(f"user/{user['username']}")
        self.assertEqual(resp.status_code, 200)

        after = self.api.get(f"user/{user['username']}", expected_error=True)
        self.assertEqual(after.status_code, 404)

    # ================= STORE =================

    def test_store_01_create_order(self):
        order = self.make_order()
        resp = self.api.post('store/order', order)
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body['id'], order['id'])
        self.assertEqual(body['status'], 'placed')
        # cleanup
        self.api.delete(f"store/order/{order['id']}", expected_error=True)

    def test_store_02_get_order(self):
        order = self.make_order()
        self.api.post('store/order', order)
        try:
            resp = self.api.get(f"store/order/{order['id']}")
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json()['id'], order['id'])
        finally:
            self.api.delete(f"store/order/{order['id']}", expected_error=True)

    def test_store_03_inventory(self):
        resp = self.api.get('store/inventory')
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertIsInstance(body, dict)
        for key in ('available', 'pending', 'sold'):
            self.assertIn(key, body)

    def test_store_04_delete_order(self):
        order = self.make_order()
        self.api.post('store/order', order)

        resp = self.api.delete(f"store/order/{order['id']}")
        self.assertEqual(resp.status_code, 200)

        after = self.api.get(f"store/order/{order['id']}", expected_error=True)
        self.assertEqual(after.status_code, 404)


if __name__ == '__main__':
    unittest.main(verbosity=2)
