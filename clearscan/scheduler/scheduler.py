"""
Task Scheduler Module

This module provides task scheduling functionality for ClearScan.
Features:
- Async task execution
- Configurable intervals
- Task prioritization
- Error handling and retries
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
import traceback

logger = logging.getLogger(__name__)

class TaskPriority(Enum):
    """Task priority levels."""
    LOW = 0
    NORMAL = 1
    HIGH = 2

@dataclass
class TaskConfig:
    """Task configuration."""
    interval: int  # Interval in seconds
    priority: TaskPriority = TaskPriority.NORMAL
    max_retries: int = 3
    retry_delay: int = 60  # Delay between retries in seconds

@dataclass
class TaskInfo:
    """Task runtime information."""
    name: str
    func: Callable
    config: TaskConfig
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    retries: int = 0
    is_running: bool = False
    error_count: int = 0

class Scheduler:
    """Async task scheduler for ClearScan."""
    
    def __init__(self):
        """Initialize the scheduler."""
        self.tasks: Dict[str, TaskInfo] = {}
        self.running = False
        self._task_histories: Dict[str, List[Dict]] = {}
        
    def add_task(self, name: str, func: Callable, config: TaskConfig) -> None:
        """
        Add a task to the scheduler.
        
        Args:
            name: Unique task name
            func: Async function to execute
            config: Task configuration
        """
        if name in self.tasks:
            raise ValueError(f"Task {name} already exists")
            
        self.tasks[name] = TaskInfo(
            name=name,
            func=func,
            config=config,
            next_run=datetime.utcnow()
        )
        self._task_histories[name] = []
        logger.info(f"Added task: {name} with interval {config.interval}s")
        
    def remove_task(self, name: str) -> None:
        """Remove a task from the scheduler."""
        if name in self.tasks:
            del self.tasks[name]
            logger.info(f"Removed task: {name}")
            
    async def _execute_task(self, task: TaskInfo) -> None:
        """Execute a single task with error handling and retries."""
        if task.is_running:
            return
            
        task.is_running = True
        task.last_run = datetime.utcnow()
        
        try:
            await task.func()
            task.retries = 0
            task.error_count = 0
            self._log_task_history(task.name, "success")
        except Exception as e:
            task.error_count += 1
            error_msg = f"Task {task.name} failed: {str(e)}\n{traceback.format_exc()}"
            logger.error(error_msg)
            self._log_task_history(task.name, "error", error_msg)
            
            if task.retries < task.config.max_retries:
                task.retries += 1
                task.next_run = datetime.utcnow() + timedelta(seconds=task.config.retry_delay)
                logger.info(f"Scheduling retry {task.retries} for task {task.name}")
            else:
                task.retries = 0
                task.next_run = datetime.utcnow() + timedelta(seconds=task.config.interval)
        finally:
            if task.retries == 0:
                task.next_run = datetime.utcnow() + timedelta(seconds=task.config.interval)
            task.is_running = False
            
    def _log_task_history(self, task_name: str, status: str, error: str = None) -> None:
        """Log task execution history."""
        history = {
            "timestamp": datetime.utcnow(),
            "status": status,
            "error": error
        }
        self._task_histories[task_name].append(history)
        
        # Keep only last 100 entries
        if len(self._task_histories[task_name]) > 100:
            self._task_histories[task_name] = self._task_histories[task_name][-100:]
            
    def get_task_history(self, task_name: str, limit: int = 10) -> List[Dict]:
        """Get execution history for a task."""
        if task_name not in self._task_histories:
            return []
        return self._task_histories[task_name][-limit:]
            
    async def _scheduler_loop(self) -> None:
        """Main scheduler loop."""
        while self.running:
            now = datetime.utcnow()
            
            # Sort tasks by priority
            sorted_tasks = sorted(
                self.tasks.values(),
                key=lambda t: t.config.priority.value,
                reverse=True
            )
            
            # Execute due tasks
            for task in sorted_tasks:
                if task.next_run and now >= task.next_run:
                    asyncio.create_task(self._execute_task(task))
                    
            await asyncio.sleep(1)  # Check every second
            
    async def start(self) -> None:
        """Start the scheduler."""
        if self.running:
            return
            
        self.running = True
        logger.info("Starting scheduler")
        await self._scheduler_loop()
        
    async def stop(self) -> None:
        """Stop the scheduler."""
        self.running = False
        logger.info("Stopping scheduler")
        
    def get_task_status(self, name: str) -> Optional[Dict]:
        """Get current status of a task."""
        task = self.tasks.get(name)
        if not task:
            return None
            
        return {
            "name": task.name,
            "last_run": task.last_run,
            "next_run": task.next_run,
            "is_running": task.is_running,
            "error_count": task.error_count,
            "retries": task.retries,
            "priority": task.config.priority.name,
            "interval": task.config.interval
        }
        
    def get_all_task_status(self) -> List[Dict]:
        """Get status of all tasks."""
        return [
            self.get_task_status(name)
            for name in self.tasks
            if self.get_task_status(name) is not None
        ] 