import os
import logging
import tempfile
import shutil
from src.db import setup_logger

def test_logging_and_rotation():
    # Временный лог-файл
    tmpdir = tempfile.mkdtemp()
    log_path = os.path.join(tmpdir, 'clearscan.log')
    logger = logging.getLogger('clearscan_test')
    handler = logging.handlers.RotatingFileHandler(log_path, maxBytes=1024, backupCount=2)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)
    # Записываем много строк для ротации
    for i in range(2000):
        logger.info(f"Test log {i}")
    logger.handlers[0].close()
    files = [f for f in os.listdir(tmpdir) if f.startswith('clearscan.log')]
    assert any('clearscan.log' in f for f in files)
    assert any('clearscan.log.1' in f for f in files)
    shutil.rmtree(tmpdir)
