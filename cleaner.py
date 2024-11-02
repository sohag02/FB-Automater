import os
import shutil

def clear_pycache(root_dir: str):
    """
    Recursively delete all __pycache__ folders in the specified directory.

    Args:
        root_dir (str): The root directory to start searching from.
    """
    for dirpath, dirnames, _ in os.walk(root_dir):
        # Check if __pycache__ is in the current directory's subdirectories
        if "__pycache__" in dirnames:
            pycache_path = os.path.join(dirpath, "__pycache__")
            shutil.rmtree(pycache_path)
            print(f"Deleted: {pycache_path}")

# Example usage
clear_pycache(os.getcwd())
