from PIL import Image
import numpy as np
from pixelmatch import pixelmatch


class RegressionMonitorAgent:
    def compare(self, baseline_path, new_path):
        img1 = np.array(Image.open(baseline_path).convert("RGB"))
        img2 = np.array(Image.open(new_path).convert("RGB"))


        diff = pixelmatch(img1, img2)


        return {
        "baseline": baseline_path,
        "new": new_path,
        "difference": diff
        }