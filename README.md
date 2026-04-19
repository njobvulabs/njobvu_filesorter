# njobvu_filesorter

A lightweight Python CLI tool that automatically organizes files in your Downloads folder into categorized subfolders.

## Features

- **Automatic categorization** - Files are sorted by extension into appropriate folders
- **Dry-run mode** - Preview all file movements before executing
- **Watch mode** - Monitor folder continuously and sort new files automatically
- **Custom paths** - Target any folder, not just Downloads
- **Self-preserving** - Won't move itself or other sorter scripts
- **Zero config** - Works out of the box with sensible defaults

## File Categories

| Folder | Extensions |
|--------|------------|
| **Images** | .jpg, .jpeg, .png, .gif, .svg, .webp, .bmp, .ico, .tiff |
| **Documents** | .pdf, .doc, .docx, .txt, .odt, .xls, .xlsx, .ppt, .pptx, .rtf, .csv, .md |
| **Videos** | .mp4, .mkv, .avi, .mov, .webm, .flv, .wmv, .m4v |
| **Audio** | .mp3, .wav, .flac, .ogg, .m4a, .aac, .wma, .opus |
| **Archives** | .zip, .rar, .7z, .tar, .gz, .bz2, .xz, .iso |
| **Code** | .py, .js, .ts, .jsx, .tsx, .html, .css, .java, .cpp, .c, .go, .rs, .sh, .json, .yaml, etc. |
| **Others** | Any file type not listed above |

## Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Setup

1. Clone or download this repository
2. (Optional) Make the script executable:
   ```bash
   chmod +x njobvu_filesorter.py
   ```

3. For watch mode, install watchdog:
   ```bash
   pip install watchdog
   ```

## Usage

### Sort existing files (one-time)

```bash
# Sort default ~/Downloads folder
python njobvu_filesorter.py run

# Sort custom folder
python njobvu_filesorter.py --path /path/to/folder run
```

### Preview moves without executing

```bash
# Dry-run mode shows what would happen
python njobvu_filesorter.py --dry-run run

# Example output:
# [MOVE]  report.pdf -> Documents/
# [MOVE]  photo.jpg -> Images/
# [MOVE]  song.mp3 -> Audio/
```

### Watch mode (continuous)

Monitor a folder and automatically sort new files as they appear:

```bash
# Install watchdog first
pip install watchdog

# Start watching
python njobvu_filesorter.py watch

# Output:
# Watching folder: /home/user/Downloads
# Press Ctrl+C to stop...
```

### Recursive sorting

Sort files in all subfolders (not just root level):

```bash
python njobvu_filesorter.py --recursive run
```

## Command Reference

| Command | Description |
|---------|-------------|
| `run` | Sort existing files once |
| `watch` | Monitor folder continuously |
| `--path <dir>` | Specify target folder (default: ~/Downloads) |
| `--dry-run` | Preview moves without executing |
| `--recursive` | Include files in subfolders |

## Examples

```bash
# Basic usage
python njobvu_filesorter.py run

# Preview before sorting
python njobvu_filesorter.py --dry-run run

# Watch Downloads folder
python njobvu_filesorter.py watch

# Sort a different folder
python njobvu_filesorter.py --path ~/Desktop run

# Combine options
python njobvu_filesorter.py --path /shared/downloads --dry-run run
```

## Behavior

- **Folder creation**: Category folders are created automatically if they don't exist
- **Name conflicts**: Files with the same name in destination are skipped
- **Hidden files**: Files starting with `.` are ignored
- **Self-exclusion**: The sorter script itself is never moved
- **Root only**: By default, only files in the root of the folder are sorted (no recursion)

## Requirements

- Python 3.10+
- watchdog (optional, only for watch mode)

## License

MIT License - feel free to use, modify, and distribute.

## Contributing

Contributions welcome! Feel free to submit issues and pull requests.
