"""Gateway notebook for https://www.kaggle.com/competitions/ai-mathematical-olympiad-progress-prize-3"""

import os
from collections.abc import Generator

import kaggle_evaluation.core.templates
import polars as pl
from kaggle_evaluation.core.base_gateway import (
    GatewayRuntimeError,
    GatewayRuntimeErrorType,
)

# Set to True during the private rerun to disable shuffling
USE_PRIVATE_SET = False


class AIMO3Gateway(kaggle_evaluation.core.templates.Gateway):
    """
    Gateway class for the AI Mathematical Olympiad Progress Prize 3.
    Provides the interface between the competition platform and the TGI solver.
    """
    def __init__(self, data_paths: tuple[str] | None = None):
        """Initializes the AIMO gateway with data paths and sets a generous timeout.

        Args:
            data_paths (tuple[str] | None): Tuple containing the test CSV path.
        """
        super().__init__(data_paths, file_share_dir=None)
        self.data_paths = data_paths
        self.set_response_timeout_seconds(60 * 60 * 9)  # 9 hours / no timeout

    def unpack_data_paths(self):
        """Unpacks the provided data paths or uses default competition paths."""
        if not self.data_paths:
            self.test_path = (
                '/kaggle/input/ai-mathematical-olympiad-progress-prize-3/test.csv'
            )
        else:
            self.test_path = self.data_paths[0]

    def generate_data_batches(
        self,
    ) -> Generator[tuple[pl.DataFrame, pl.DataFrame], None, None]:
        """Generates batches of test data for evaluation.

        Returns:
            Generator[tuple[pl.DataFrame, pl.DataFrame], None, None]: Batches of (row, row_id).
        """
        # Generate a random seed from system entropy
        random_seed = int.from_bytes(os.urandom(4), byteorder='big')

        # Read the test set and shuffle
        test = pl.read_csv(self.test_path)
        if not USE_PRIVATE_SET:
            test = test.sample(
                fraction=1.0, shuffle=True, with_replacement=False, seed=random_seed
            )

        for row in test.iter_slices(n_rows=1):
            # Generate a problem instance and the validation id
            yield row, row.select('id')

    def competition_specific_validation(
        self, prediction_batch, row_ids, data_batch
    ) -> None:
        """Performs competition-specific validation on predictions."""
        pass


if __name__ == '__main__':
    if os.getenv('KAGGLE_IS_COMPETITION_RERUN'):
        gateway = AIMO3Gateway()
        # Relies on valid default data paths
        gateway.run()
    else:
        print('Skipping run for now')
