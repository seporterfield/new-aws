import asyncio
import pytest
from datetime import datetime


@pytest.mark.asyncio
async def test_skyvern_aws_basic():
    """Basic Skyvern approach to AWS registration"""
    from skyvern import Skyvern
    
    skyvern = Skyvern()
    
    print("Starting basic AWS registration task...")
    task = await skyvern.run_task(
        url="https://portal.aws.amazon.com/billing/signup",
        prompt="Navigate to the AWS account creation form and identify all required fields"
    )
    
    print(f"Task result: {task}")
    return task


@pytest.mark.asyncio
async def test_skyvern_aws_step_by_step():
    """Step-by-step Skyvern approach"""
    from skyvern import Skyvern
    
    skyvern = Skyvern()
    
    # Step 1: Navigate to page
    print("Step 1: Navigating to AWS registration...")
    task1 = await skyvern.run_task(
        url="https://portal.aws.amazon.com/billing/signup",
        prompt="Load the AWS registration page and wait for it to fully render"
    )
    
    # Step 2: Analyze form
    print("Step 2: Analyzing registration form...")
    task2 = await skyvern.run_task(
        url="https://portal.aws.amazon.com/billing/signup",
        prompt="Find and list all input fields in the AWS registration form, including their labels and types"
    )
    
    print(f"Navigation result: {task1}")
    print(f"Form analysis result: {task2}")
    
    return task1, task2


@pytest.mark.asyncio
async def test_skyvern_aws_with_detailed_prompt():
    """Skyvern with very detailed prompts"""
    from skyvern import Skyvern
    
    skyvern = Skyvern()
    
    detailed_prompt = """
    Navigate to the AWS account registration page and perform the following analysis:
    1. Wait for the page to fully load (all JavaScript and dynamic content)
    2. Identify the main registration form
    3. List all input fields with their types (email, password, text, etc.)
    4. Note any dropdown menus or selection fields
    5. Check for CAPTCHA or verification requirements
    6. Look for any error messages or validation requirements
    7. Take note of the form submission button and its state
    8. Report any redirect attempts or additional authentication steps
    """
    
    print("Starting detailed AWS analysis...")
    task = await skyvern.run_task(
        url="https://portal.aws.amazon.com/billing/signup",
        prompt=detailed_prompt
    )
    
    print(f"Detailed analysis result: {task}")
    return task


@pytest.mark.asyncio
async def test_skyvern_aws_with_retry_logic():
    """Skyvern with retry logic for reliability"""
    from skyvern import Skyvern
    
    skyvern = Skyvern()
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}")
            
            task = await skyvern.run_task(
                url="https://portal.aws.amazon.com/billing/signup",
                prompt="Access AWS registration page and identify the email input field. If the page doesn't load properly, report the issue."
            )
            
            if task and hasattr(task, 'status') and task.status in ['completed', 'success']:
                print(f"Success on attempt {attempt + 1}")
                return task
            else:
                print(f"Attempt {attempt + 1} failed or incomplete")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2)  # Wait before retry
                    
        except Exception as e:
            print(f"Attempt {attempt + 1} error: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2)
            else:
                raise
    
    print("All attempts failed")
    return None


@pytest.mark.asyncio
async def test_skyvern_aws_form_filling_simulation():
    """Simulate form filling without actually submitting"""
    from skyvern import Skyvern
    
    skyvern = Skyvern()
    
    # Test data for simulation
    test_data = {
        "email": "test@example.com",
        "password": "TestPassword123!",
        "account_name": "TestAccount",
        "full_name": "Test User"
    }
    
    prompt = f"""
    Navigate to AWS registration page and simulate filling out the form with test data:
    - Email: {test_data['email']}
    - Password: {test_data['password']}
    - Account Name: {test_data['account_name']}
    - Full Name: {test_data['full_name']}
    
    DO NOT actually submit the form. Just identify where each field would be filled
    and report on the form structure and any validation requirements you observe.
    """
    
    print("Starting form filling simulation...")
    task = await skyvern.run_task(
        url="https://portal.aws.amazon.com/billing/signup",
        prompt=prompt
    )
    
    print(f"Form simulation result: {task}")
    return task


if __name__ == "__main__":
    # Run individual tests
    asyncio.run(test_skyvern_aws_basic())