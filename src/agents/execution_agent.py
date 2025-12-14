try:
    from src.automation.playwright_runner import PlaywrightRunner
except ImportError:
    # Support running the module as a script or in different import contexts
    try:
        from ..automation.playwright_runner import PlaywrightRunner
    except Exception as e:
        raise ImportError(
            "Could not import PlaywrightRunner. Run from project root or ensure package is installed."
        ) from e


class ExecutionAgent:
    def __init__(self):
        self.runner = PlaywrightRunner()

    def execute(self, script_content):
        return self.runner.run_script(script_content)