import os
import subprocess
import shutil

# Create the target doc folder if not exists
os.makedirs("doc", exist_ok=True)

modules = [
    "habit_tracker.models",
    "habit_tracker.user",
    "habit_tracker.utils",
    "habit_tracker.services",
    "habit_tracker.analytics",
    "habit_tracker.cli",
]

for mod in modules:
    print(f"Generating docs for {mod}...")
    subprocess.run(["python", "-m", "pydoc", "-w", mod])
    output_filename = mod + ".html"
    shutil.move(output_filename, os.path.join("doc", os.path.basename(output_filename)))
