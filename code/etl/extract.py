import pandas as pd
from pathlib import Path


def extract_data(file_path):
    file_path = Path(file_path)

    try:
        df = pd.read_csv(file_path)

        if df.empty:
            raise ValueError("CSV file is empty")

        print(f"Extracted {len(df)} rows successfully!")

        return df

    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file cannot be found: {file_path}")

    except pd.errors.EmptyDataError:
        raise ValueError(f"CSV file contains no data: {file_path}")

    except Exception as e:
        raise RuntimeError(f"Extract failed: {e}")
