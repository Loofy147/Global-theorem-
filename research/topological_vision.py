import numpy as np
from PIL import Image
from typing import Dict, List, Tuple, Any, Optional
import os

class TopologicalVisionMapper:
    """
    TGI Vision Mapper.
    Lifts pixel data (x, y, color) into discrete topological manifolds (G_m^k).
    Enables spatial-color fibration analysis.
    """
    def __init__(self, m: int = 256, k: int = 5):
        # Default k=5: (x, y, R, G, B)
        self.m = m
        self.k = k

    def load_image(self, path: str, resize: Tuple[int, int] = (64, 64)) -> np.ndarray:
        """Loads and prepares an image for topological mapping."""
        if not os.path.exists(path):
            # Generate synthetic image if path doesn't exist for demo/testing
            img = np.zeros((resize[1], resize[0], 3), dtype=np.uint8)
            # Center square
            img[resize[1]//4:3*resize[1]//4, resize[0]//4:3*resize[0]//4] = [255, 0, 0] # Red square
            return img

        try:
            img = Image.open(path).convert('RGB')
            img = img.resize(resize)
            return np.array(img)
        except Exception:
            return self.load_image("force_synthetic", resize)

    def image_to_manifold(self, img_array: np.ndarray) -> List[Tuple[int, ...]]:
        """
        Maps image pixels to G_m^k coordinates.
        Standard mapping (k=5): (x_norm, y_norm, r, g, b)
        """
        h, w, _ = img_array.shape
        points = []

        # Scale coordinates to [0, m-1]
        for y in range(h):
            for x in range(w):
                x_m = int((x / (w - 1)) * (self.m - 1)) if w > 1 else 0
                y_m = int((y / (h - 1)) * (self.m - 1)) if h > 1 else 0
                r, g, b = img_array[y, x]
                # Scale color if m != 256
                if self.m != 256:
                    r = int((r / 255) * (self.m - 1))
                    g = int((g / 255) * (self.m - 1))
                    b = int((b / 255) * (self.m - 1))

                point = (x_m, y_m, r, g, b)
                # Trim or pad to k
                if len(point) > self.k:
                    point = point[:self.k]
                elif len(point) < self.k:
                    point = point + (0,) * (self.k - len(point))

                points.append(point)
        return points

    def calculate_spatial_entropy(self, img_array: np.ndarray) -> float:
        """Measures how distributed colors are across the spatial manifold."""
        points = self.image_to_manifold(img_array)
        if not points: return 0.0
        # Use only color components for entropy if k >= 5
        color_points = np.array([p[2:] for p in points]) if self.k >= 5 else np.array(points)
        _, counts = np.unique(color_points, axis=0, return_counts=True)
        probs = counts / np.sum(counts)
        return -float(np.sum(probs * np.log2(probs + 1e-10)))

    def lift_image(self, data: Any) -> Dict[str, Any]:
        """Performs full vision lifting to the TGI framework."""
        if isinstance(data, str):
            img = self.load_image(data)
        elif isinstance(data, np.ndarray):
            img = data
        else:
            img = self.load_image("synthetic.png") # Force synthetic

        points = self.image_to_manifold(img)
        entropy = self.calculate_spatial_entropy(img)

        return {
            "m": self.m,
            "k": self.k,
            "points_count": len(points),
            "topological_entropy": entropy,
            "dimensions": img.shape[:2],
            "manifold_sample": points[:5]
        }

if __name__ == "__main__":
    mapper = TopologicalVisionMapper(m=256, k=5)
    result = mapper.lift_image("test_image.png")
    print(f"Vision Manifold Lifted: {result['points_count']} points in G_{result['m']}^{result['k']}")
    print(f"Topological Entropy: {result['topological_entropy']:.4f}")
    print(f"Dimensions: {result['dimensions']}")
