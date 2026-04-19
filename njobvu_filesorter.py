#!/usr/bin/env python3
"""
njobvu_filesorter - A CLI tool to organize files in your Downloads folder.
"""

import argparse
import shutil
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
except ImportError:
    Observer = None
    FileSystemEventHandler = object


@dataclass
class FileCategory:
    name: str
    extensions: set[str]


CATEGORIES = [
    FileCategory("Images", {".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp", ".bmp", ".ico", ".tiff"}),
    FileCategory("Documents", {".pdf", ".doc", ".docx", ".txt", ".odt", ".xls", ".xlsx", ".ppt", ".pptx", ".rtf", ".csv", ".md"}),
    FileCategory("Videos", {".mp4", ".mkv", ".avi", ".mov", ".webm", ".flv", ".wmv", ".m4v"}),
    FileCategory("Audio", {".mp3", ".wav", ".flac", ".ogg", ".m4a", ".aac", ".wma", ".opus"}),
    FileCategory("Archives", {".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso"}),
    FileCategory("Code", {".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".scss", ".java", ".cpp", ".c", ".h", ".hpp", ".cs", ".go", ".rs", ".rb", ".php", ".swift", ".kt", ".sh", ".bash", ".zsh", ".ps1", ".json", ".xml", ".yaml", ".yml", ".toml", ".sql"}),
]

EXTENSION_TO_CATEGORY: dict[str, str] = {}
for cat in CATEGORIES:
    for ext in cat.extensions:
        EXTENSION_TO_CATEGORY[ext] = cat.name


class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"


def get_category(extension: str) -> str:
    return EXTENSION_TO_CATEGORY.get(extension.lower(), "Others")


def iter_files(folder: Path, recursive: bool = False) -> Iterator[Path]:
    if recursive:
        return folder.rglob("*")
    return folder.iterdir()


EXCLUDED_FILES = {"njobvu_filesorter.py"}


def sort_files(folder: Path, dry_run: bool = True, recursive: bool = False) -> tuple[int, int]:
    moved_count = 0
    skipped_count = 0

    for file_path in iter_files(folder, recursive):
        if not file_path.is_file():
            continue
        if file_path.name.startswith("."):
            continue
        if file_path.name in EXCLUDED_FILES:
            continue

        extension = file_path.suffix.lower()
        category_name = get_category(extension)
        dest_folder = folder / category_name
        dest_file = dest_folder / file_path.name

        if not dest_folder.exists():
            if dry_run:
                print(f"{Colors.CYAN}[DRY-RUN] Would create folder: {category_name}/{Colors.RESET}")
            else:
                dest_folder.mkdir(exist_ok=True)
                print(f"{Colors.CYAN}[CREATE] Folder: {category_name}/{Colors.RESET}")

        if dest_file.exists():
            print(f"{Colors.YELLOW}[SKIP]  {file_path.name} -> {category_name}/ (already exists){Colors.RESET}")
            skipped_count += 1
            continue

        if dry_run:
            print(f"{Colors.GREEN}[MOVE]  {file_path.name} -> {category_name}/{Colors.RESET}")
        else:
            shutil.move(str(file_path), str(dest_file))
            print(f"{Colors.GREEN}[MOVED] {file_path.name} -> {category_name}/{Colors.RESET}")
        moved_count += 1

    return moved_count, skipped_count


class SortingEventHandler(FileSystemEventHandler):
    def __init__(self, folder: Path, recursive: bool = False):
        self.folder = folder
        self.recursive = recursive
        self.processed_files: set[str] = set()

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if str(file_path) in self.processed_files:
            return
        self.processed_files.add(str(file_path))

        if not file_path.exists():
            return
        if file_path.name.startswith("."):
            return
        if file_path.name in EXCLUDED_FILES:
            return

        time.sleep(0.5)

        extension = file_path.suffix.lower()
        category_name = get_category(extension)
        dest_folder = self.folder / category_name
        dest_file = dest_folder / file_path.name

        if dest_file.exists():
            print(f"{Colors.YELLOW}[SKIP]  {file_path.name} -> {category_name}/ (already exists){Colors.RESET}")
            return

        if not dest_folder.exists():
            dest_folder.mkdir(exist_ok=True)
            print(f"{Colors.CYAN}[CREATE] Folder: {category_name}/{Colors.RESET}")

        shutil.move(str(file_path), str(dest_file))
        print(f"{Colors.GREEN}[MOVED] {file_path.name} -> {category_name}/{Colors.RESET}")


def watch_folder(folder: Path, recursive: bool = False):
    if Observer is None:
        print(f"{Colors.RED}Error: watchdog library not installed.{Colors.RESET}")
        print("Install it with: pip install watchdog")
        sys.exit(1)

    event_handler = SortingEventHandler(folder, recursive)
    observer = Observer()
    observer.schedule(event_handler, str(folder), recursive=recursive)
    observer.start()

    print(f"{Colors.BOLD}{Colors.BLUE}Watching folder: {folder}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}Press Ctrl+C to stop...{Colors.RESET}\n")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Stopping watcher...{Colors.RESET}")
        observer.stop()
    observer.join()


def main():
    parser = argparse.ArgumentParser(
        description="njobvu_filesorter - Organize files into categories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python njobvu_filesorter.py run                        Sort Downloads folder
  python njobvu_filesorter.py --dry-run run              Preview what would be moved
  python njobvu_filesorter.py watch                      Monitor folder continuously
  python njobvu_filesorter.py --path ./myfiles run        Custom folder
        """
    )

    parser.add_argument(
        "--path",
        type=Path,
        default=Path.home() / "Downloads",
        help="Folder to organize (default: ~/Downloads)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview moves without actually moving files"
    )
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Sort files in subfolders too"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("run", help="Sort existing files once")
    subparsers.add_parser("watch", help="Monitor folder continuously")

    args = parser.parse_args()
    folder = args.path.expanduser().resolve()

    if not folder.exists():
        print(f"{Colors.RED}Error: Folder does not exist: {folder}{Colors.RESET}")
        sys.exit(1)

    print(f"\n{Colors.BOLD}{'='*50}{Colors.RESET}")
    print(f"{Colors.BOLD}  njobvu_filesorter{Colors.RESET}")
    print(f"{Colors.BOLD}{'='*50}{Colors.RESET}")
    print(f"{Colors.CYAN}Folder: {folder}{Colors.RESET}")
    print(f"{Colors.CYAN}Mode:   {'Dry-run (preview)' if args.dry_run else 'Live mode'}{Colors.RESET}")
    print(f"{Colors.CYAN}Scope:  {'Recursive' if args.recursive else 'Root only'}{Colors.RESET}\n")

    if args.command == "watch":
        watch_folder(folder, args.recursive)
    else:
        moved, skipped = sort_files(folder, dry_run=args.dry_run, recursive=args.recursive)
        
        print(f"\n{Colors.BOLD}{'='*50}{Colors.RESET}")
        if args.dry_run:
            print(f"{Colors.YELLOW}DRY-RUN complete: {moved} files would be moved, {skipped} skipped{Colors.RESET}")
        else:
            print(f"{Colors.GREEN}Sorting complete: {moved} files moved, {skipped} skipped{Colors.RESET}")


if __name__ == "__main__":
    main()
