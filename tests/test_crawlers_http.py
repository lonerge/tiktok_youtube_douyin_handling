import sys
import types
import unittest
from unittest.mock import Mock, patch


def _install_optional_dependency_stubs():
    requests = types.ModuleType('requests')
    requests.get = Mock()
    requests.post = Mock()
    sys.modules.setdefault('requests', requests)

    pymongo = types.ModuleType('pymongo')
    pymongo.MongoClient = object
    sys.modules.setdefault('pymongo', pymongo)
    sys.modules.setdefault('threadpool', types.ModuleType('threadpool'))
    sys.modules.setdefault('undetected_chromedriver', types.ModuleType('undetected_chromedriver'))
    sys.modules.setdefault('douyin_video', types.ModuleType('douyin_video'))


_install_optional_dependency_stubs()
from crawlers import Crawlers
import crawlers


class CrawlersSimpleGetTests(unittest.TestCase):
    def setUp(self):
        self.crawler = Crawlers.__new__(Crawlers)
        self.crawler.request_timeout = (2.0, 7.0)

    def test_uses_get_with_proxy_and_cookies(self):
        self.crawler.proxy = {'http': 'http://proxy', 'https': 'http://proxy'}
        response = Mock(status_code=200, text='ok')

        with patch.object(crawlers.requests, 'get', return_value=response) as get, patch.object(crawlers.requests, 'post') as post:
            result = self.crawler.simple_get('https://example.test', {'Accept': 'application/json'}, cookies={'a': 'b'})

        self.assertEqual(result, 'ok')
        get.assert_called_once_with(
            url='https://example.test',
            headers={'Accept': 'application/json'},
            timeout=(2.0, 7.0),
            proxies=self.crawler.proxy,
            cookies={'a': 'b'},
        )
        post.assert_not_called()

    def test_uses_get_without_proxy(self):
        self.crawler.proxy = None
        response = Mock(status_code=200, text='ok')

        with patch.object(crawlers.requests, 'get', return_value=response) as get, patch.object(crawlers.requests, 'post') as post:
            result = self.crawler.simple_get('https://example.test', {'Accept': 'application/json'})

        self.assertEqual(result, 'ok')
        get.assert_called_once_with(
            url='https://example.test',
            headers={'Accept': 'application/json'},
            timeout=(2.0, 7.0),
        )
        post.assert_not_called()

    def test_retries_http_errors_five_times_then_raises(self):
        self.crawler.proxy = None
        response = Mock(status_code=503, text='unavailable')

        with patch.object(crawlers.requests, 'get', return_value=response) as get, patch('crawlers.time.sleep') as sleep, patch('crawlers.random.uniform', return_value=0):
            with self.assertRaisesRegex(Exception, '接口: https://example.test 异常'):
                self.crawler.simple_get('https://example.test', {})

        self.assertEqual(get.call_count, 5)
        self.assertEqual(sleep.call_count, 5)

    def test_retries_timeouts_five_times_then_raises(self):
        self.crawler.proxy = None

        with patch.object(crawlers.requests, 'get', side_effect=TimeoutError('timed out')) as get, patch('crawlers.time.sleep') as sleep, patch('crawlers.random.uniform', return_value=0):
            with self.assertRaisesRegex(Exception, '接口: https://example.test 异常'):
                self.crawler.simple_get('https://example.test', {})

        self.assertEqual(get.call_count, 5)
        self.assertEqual(sleep.call_count, 5)
        self.assertEqual(get.call_args.kwargs['timeout'], (2.0, 7.0))
