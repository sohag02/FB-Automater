import os
import shutil

def clear_pycache(root_dir: str):
    for dirpath, dirnames, _ in os.walk(root_dir):
        if "__pycache__" in dirnames:
            pycache_path = os.path.join(dirpath, "__pycache__")
            shutil.rmtree(pycache_path)
            print(f"Deleted: {pycache_path}")

if __name__ == "__main__":
    clear_pycache(os.getcwd())
