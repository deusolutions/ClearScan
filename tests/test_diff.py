import unittest
from datetime import datetime
from core.diff import Diff

class TestDiff(unittest.TestCase):
    def setUp(self):
        self.diff = Diff()
        self.current_scan = [
            {
                'timestamp': datetime.now(),
                'ip': '192.168.1.1',
                'port': 80,
                'status': 'open'
            },
            {
                'timestamp': datetime.now(),
                'ip': '192.168.1.2',
                'port': 443,
                'status': 'closed'
            }
        ]
        self.previous_scan = [
            {
                'timestamp': datetime.now(),
                'ip': '192.168.1.1',
                'port': 80,
                'status': 'closed'
            },
            {
                'timestamp': datetime.now(),
                'ip': '192.168.1.3',
                'port': 22,
                'status': 'open'
            }
        ]

    def test_compare_changes(self):
        changes = self.diff.compare(self.current_scan, self.previous_scan)
        
        # Должно быть 3 изменения:
        # 1. Изменение статуса порта 80 на 192.168.1.1
        # 2. Новый хост 192.168.1.2 с портом 443
        # 3. Удаленный хост 192.168.1.3 с портом 22
        self.assertEqual(len(changes), 3)
        
        # Проверка изменения статуса
        port_80_change = next(c for c in changes if c['ip'] == '192.168.1.1' and c['port'] == 80)
        self.assertEqual(port_80_change['old_status'], 'closed')
        self.assertEqual(port_80_change['new_status'], 'open')
        
        # Проверка нового хоста
        new_host = next(c for c in changes if c['ip'] == '192.168.1.2')
        self.assertEqual(new_host['old_status'], 'unknown')
        self.assertEqual(new_host['new_status'], 'closed')
        
        # Проверка удаленного хоста
        removed_host = next(c for c in changes if c['ip'] == '192.168.1.3')
        self.assertEqual(removed_host['old_status'], 'open')
        self.assertEqual(removed_host['new_status'], 'closed')

if __name__ == '__main__':
    unittest.main() 