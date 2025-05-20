class Scanner:
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def scan_subnet(self, subnet):
        import subprocess
        result = subprocess.run(['nmap', '-sn', subnet], capture_output=True, text=True)
        return result.stdout

    def save_results(self, subnet, results):
        from db import insert_scan_result
        insert_scan_result(self.db_connection, subnet, results)