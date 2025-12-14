import subprocess
import uuid
import os
import sys
from loguru import logger


class PlaywrightRunner:
    def __init__(self):
        os.makedirs("outputs/scripts", exist_ok=True)
        os.makedirs("outputs/screenshots", exist_ok=True)

    def run_script(self, script_content: str, timeout: int = 120):
        script_id = str(uuid.uuid4())
        script_path = f"outputs/scripts/{script_id}.py"

        # Write the script file
        try:
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)
        except Exception as e:
            logger.exception("Failed to write script to %s", script_path)
            return {"status": "error", "message": f"Failed to write script: {e}"}

        logger.info("Running script %s", script_path)

        # Run the script using the same Python interpreter that's running this process
        try:
            result = subprocess.run(
                [sys.executable, script_path],
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            output = result.stdout
            error = result.stderr
        except subprocess.TimeoutExpired as e:
            logger.exception("Script timed out: %s", script_path)
            return {
                "status": "error",
                "message": "Script timed out",
                "stdout": e.stdout or "",
                "stderr": e.stderr or "",
            }
        except Exception as e:
            logger.exception("Failed to run script: %s", script_path)
            return {"status": "error", "message": str(e)}

        screenshot_path = f"outputs/screenshots/{script_id}.png"
        return {
            "status": "success",
            "script_id": script_id,
            "stdout": output,
            "stderr": error,
            "screenshot": screenshot_path,
        }
