import time
import unittest

from probe.connectors.base import Item, RateLimiter, Response, build_headers, build_url


class TestBuildUrl(unittest.TestCase):
    def test_no_params_returns_url_unchanged(self):
        self.assertEqual(build_url("https://api.example.com/works", None),
                         "https://api.example.com/works")

    def test_params_are_appended_and_encoded(self):
        url = build_url("https://api.example.com/works", {"query": "a b", "rows": 5})
        self.assertIn("query=a+b", url)
        self.assertIn("rows=5", url)
        self.assertTrue(url.startswith("https://api.example.com/works?"))

    def test_bracketed_filter_params_survive_encoding(self):
        """OSF uses filter[provider]; the server must still receive the brackets."""
        url = build_url("https://api.osf.io/v2/preprints/", {"filter[provider]": "psyarxiv"})
        self.assertIn("filter%5Bprovider%5D=psyarxiv", url)


class TestBuildHeaders(unittest.TestCase):
    def test_always_sets_user_agent_and_accept(self):
        h = build_headers()
        self.assertIn("User-Agent", h)
        self.assertEqual(h["Accept"], "application/json")

    def test_extra_headers_are_merged(self):
        h = build_headers({"x-api-key": "abc"})
        self.assertEqual(h["x-api-key"], "abc")
        self.assertIn("User-Agent", h)


class TestRateLimiter(unittest.TestCase):
    def test_first_call_does_not_block(self):
        limiter = RateLimiter(0.5)
        start = time.monotonic()
        limiter.wait()
        self.assertLess(time.monotonic() - start, 0.1)

    def test_second_call_waits_the_interval(self):
        limiter = RateLimiter(0.2)
        limiter.wait()
        start = time.monotonic()
        limiter.wait()
        self.assertGreaterEqual(time.monotonic() - start, 0.15)


class TestItem(unittest.TestCase):
    def test_item_defaults_are_all_none_or_empty(self):
        item = Item()
        self.assertIsNone(item.doi)
        self.assertEqual(item.authors, ())
        self.assertEqual(item.extra_ids, {})

    def test_response_carries_total_items_and_raw(self):
        r = Response(total=3, items=[Item(title="x")], raw={"k": "v"})
        self.assertEqual(r.total, 3)
        self.assertEqual(r.items[0].title, "x")
        self.assertEqual(r.raw["k"], "v")
