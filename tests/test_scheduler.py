"""Tests for task scheduler."""

import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from clearscan.scheduler.scheduler import Scheduler, TaskConfig, TaskPriority
from clearscan.scheduler.tasks import ScanTask, NotificationTask

@pytest.fixture
def scheduler():
    """Create a scheduler instance."""
    return Scheduler()

@pytest.fixture
def mock_task():
    """Create a mock task."""
    return AsyncMock()

@pytest.mark.asyncio
async def test_scheduler_add_task(scheduler, mock_task):
    """Test adding tasks to scheduler."""
    config = TaskConfig(interval=60)
    scheduler.add_task("test_task", mock_task, config)
    
    assert "test_task" in scheduler.tasks
    assert scheduler.tasks["test_task"].func == mock_task
    assert scheduler.tasks["test_task"].config == config
    
    # Test duplicate task
    with pytest.raises(ValueError):
        scheduler.add_task("test_task", mock_task, config)

@pytest.mark.asyncio
async def test_scheduler_remove_task(scheduler, mock_task):
    """Test removing tasks from scheduler."""
    config = TaskConfig(interval=60)
    scheduler.add_task("test_task", mock_task, config)
    assert "test_task" in scheduler.tasks
    
    scheduler.remove_task("test_task")
    assert "test_task" not in scheduler.tasks
    
    # Test removing non-existent task
    scheduler.remove_task("non_existent")  # Should not raise

@pytest.mark.asyncio
async def test_task_execution(scheduler, mock_task):
    """Test task execution."""
    config = TaskConfig(interval=1)  # 1 second interval
    scheduler.add_task("test_task", mock_task, config)
    
    # Start scheduler
    asyncio.create_task(scheduler.start())
    await asyncio.sleep(2)  # Wait for execution
    
    # Stop scheduler
    await scheduler.stop()
    
    # Check if task was called
    assert mock_task.called
    assert mock_task.call_count >= 1

@pytest.mark.asyncio
async def test_task_retry(scheduler):
    """Test task retry mechanism."""
    failed_attempts = 0
    
    async def failing_task():
        nonlocal failed_attempts
        failed_attempts += 1
        raise Exception("Task failed")
    
    config = TaskConfig(
        interval=1,
        max_retries=2,
        retry_delay=1
    )
    scheduler.add_task("failing_task", failing_task, config)
    
    # Start scheduler
    asyncio.create_task(scheduler.start())
    await asyncio.sleep(5)  # Wait for retries
    
    # Stop scheduler
    await scheduler.stop()
    
    # Check retry count
    assert failed_attempts > 1
    task_history = scheduler.get_task_history("failing_task")
    assert len(task_history) > 0
    assert all(h["status"] == "error" for h in task_history)

@pytest.mark.asyncio
async def test_task_priority(scheduler):
    """Test task priority execution order."""
    execution_order = []
    
    async def task_low():
        execution_order.append("low")
        await asyncio.sleep(0.1)
    
    async def task_high():
        execution_order.append("high")
        await asyncio.sleep(0.1)
    
    # Add tasks with different priorities
    scheduler.add_task(
        "low_priority",
        task_low,
        TaskConfig(interval=1, priority=TaskPriority.LOW)
    )
    scheduler.add_task(
        "high_priority",
        task_high,
        TaskConfig(interval=1, priority=TaskPriority.HIGH)
    )
    
    # Start scheduler
    asyncio.create_task(scheduler.start())
    await asyncio.sleep(2)
    
    # Stop scheduler
    await scheduler.stop()
    
    # Check execution order
    assert execution_order[0] == "high"  # High priority should execute first

@pytest.mark.asyncio
async def test_task_status(scheduler, mock_task):
    """Test task status reporting."""
    config = TaskConfig(interval=60)
    scheduler.add_task("test_task", mock_task, config)
    
    status = scheduler.get_task_status("test_task")
    assert status is not None
    assert status["name"] == "test_task"
    assert status["is_running"] is False
    assert status["error_count"] == 0
    
    # Test non-existent task
    assert scheduler.get_task_status("non_existent") is None
    
    # Test all tasks status
    all_status = scheduler.get_all_task_status()
    assert len(all_status) == 1
    assert all_status[0]["name"] == "test_task"

@pytest.mark.asyncio
async def test_scan_task(db_session):
    """Test network scanning task."""
    from clearscan.models import Network
    
    # Create test network
    network = Network(
        name="Test Network",
        ip_range="127.0.0.1/32",
        is_active=True,
        scan_interval=3600
    )
    db_session.add(network)
    db_session.commit()
    
    # Create and run scan task
    task = ScanTask(db_session, network.id)
    await task()
    
    # Verify scan was recorded
    network = db_session.get(Network, network.id)
    assert network.last_scan is not None

@pytest.mark.asyncio
async def test_notification_task(db_session):
    """Test notification delivery task."""
    # Create mock bot
    mock_bot = MagicMock()
    mock_bot.send_notification = AsyncMock()
    
    # Create and run notification task
    task = NotificationTask(db_session, mock_bot)
    await task()
    
    # Note: Actual notification verification would depend on the notification system's implementation 