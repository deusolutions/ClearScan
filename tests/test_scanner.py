import unittest
from core.scanner import Scanner

class FakePortScanner:
    def __init__(self):
        self.data = {
            '127.0.0.1': {
                'tcp': {
                    '80': {'state': 'open'},
                    '443': {'state': 'closed'}
                }
            }
        }
    def all_hosts(self):
        return ['127.0.0.1']
    def __getitem__(self, key):
        return self.data[key]
    def scan(self, *args, **kwargs):
        pass  # ничего не делает, т.к. данные уже заданы

class TestScanner(unittest.TestCase):
    def setUp(self):
        self.subnets = ["127.0.0.1"]
        self.ports = [80, 443]
        self.scanner = Scanner(self.subnets, self.ports)

    def test_scan(self):
        self.scanner.nm = FakePortScanner()
        results = self.scanner.scan()
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['ip'], '127.0.0.1')
        self.assertEqual(results[0]['port'], 80)
        self.assertEqual(results[0]['status'], 'open')
        self.assertEqual(results[1]['ip'], '127.0.0.1')
        self.assertEqual(results[1]['port'], 443)
        self.assertEqual(results[1]['status'], 'closed')

if __name__ == '__main__':
    unittest.main() 