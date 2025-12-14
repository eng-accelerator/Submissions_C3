def test_runner_import():
    from src.automation.playwright_runner import PlaywrightRunner
    assert PlaywrightRunner is not None