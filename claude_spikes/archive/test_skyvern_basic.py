import asyncio
import pytest


@pytest.mark.asyncio
async def test_skyvern_homepage_navigation():
    from skyvern import Skyvern
    
    skyvern = Skyvern()
    
    print("Starting Skyvern task...")
    task = await skyvern.run_task(
        url="https://example.com",
        prompt="Click on the first link on the page"
    )
    
    print(f"Task completed: {task}")
    assert task is not None
    
    # Check if task was successful
    if hasattr(task, 'status'):
        print(f"Task status: {task.status}")
        assert task.status in ['completed', 'success'], f"Task failed with status: {task.status}"
    
    print("Test passed!")