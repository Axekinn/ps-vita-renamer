# PS Vita PKG Renamer

A Python script to automatically rename PS Vita PKG files based on CSV data with proper game titles, update versions, and Title IDs.
This tool is provided along with [this csv](https://github.com/Axekinn/ps-vita-update-scraper/blob/main/psvita_updates_results.csv)

## 🎮 Overview

This tool helps organize your PS Vita PKG collection by renaming files from cryptic names like:
```
UP9000-PCSA00004_00-ESCPGAMEMASTERUS-A0104-V0100-1f2d79240c7e95736c49450d43f647ebbc83d7c5-PE.pkg
```

To clean, readable names like:
```
Escape Plan [UPDATE 01.04][PCSA00004].pkg
```

## ✨ Features

- **Smart Title ID Extraction**: Automatically extracts Title IDs from various PKG filename formats
- **CSV-Based Renaming**: Uses comprehensive game database from CSV files
- **Multi-Region Support**: Supports UP, EP, HP, JP region prefixes
- **Safe Operation**: Dry-run mode to preview changes before applying
- **Comprehensive Logging**: Detailed logs of all operations and errors
- **Duplicate Protection**: Prevents overwriting existing files
- **Format Validation**: Skips already correctly formatted files

## 🚀 Quick Start

### Prerequisites

- Python 3.6 or higher
- CSV file with game data (columns: `Media_ID`, `Title`, `Update_Version`)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/Axekinn/ps-vita-renamer.git
cd ps-vita-renamer
```

2. Run the script:
```bash
python ps-vita-renamer.py
```

### Usage

1. **Enter PKG directory path**: Path to folder containing your .pkg files
2. **Enter CSV file path**: Path to your game database CSV file
3. **Choose mode**: Simulation (default) or real renaming

```bash
=== PS Vita PKG Renamer ===

Enter PKG directory path: /path/to/your/pkg/files
Enter CSV file path: /path/to/your/games.csv
Run simulation (y/n)? [y]: y

=== SIMULATION MODE - No files will be renamed ===
```

## 📊 CSV Format

Your CSV file should contain the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| `Media_ID` | Game Title ID | PCSA00004 |
| `Title` | Game name | Escape Plan |
| `Update_Version` | Update version | 01.04 |

Example CSV structure:
```csv
Media_ID,Title,Update_Version
PCSA00004,Escape Plan,01.04
PCSA00008,Resistance Burning Skies,01.02
PCSB01464,Russian Subway Dogs,01.01
```

## 🎯 Supported Filename Patterns

The script recognizes PKG files with these patterns:
- `UP####-PCXX#####_...` (US region)
- `EP####-PCXX#####_...` (EU region)
- `HP####-PCXX#####_...` (Asia region)
- `JP####-PCXX#####_...` (Japan region)

Where `PCXX#####` represents the Title ID.

## 📋 Output Format

Files are renamed to the format:
```
{Game Title} [UPDATE {Version}][{Title_ID}](axekin.com).pkg
```

Examples:
- `Escape Plan [UPDATE 01.04][PCSA00004](axekin.com).pkg`
- `Russian Subway Dogs [UPDATE 01.01][PCSB01464](axekin.com).pkg`
- `ScourgeBringer [UPDATE 01.60][PCSH10308](axekin.com).pkg`

## 🛡️ Safety Features

- **Dry Run Mode**: Test renaming without making changes
- **Backup Protection**: Won't overwrite existing files
- **Comprehensive Logging**: All operations logged to `psvita_renamer.log`
- **Error Handling**: Graceful handling of missing data or file access issues

## 📝 Example Output

```
=== RESULTS ===
Files processed successfully: 8
Errors encountered: 2

Files that would be renamed:
  - EP0630-PCSB01464_00-RUSSUBDOGSPSV000-A0101-V0101.pkg -> Russian Subway Dogs [UPDATE 01.01][PCSB01464](axekin.com).pkg
  - HP2005-PCSH10308_00-SCOURGEBRINGER00-A0160-V0100.pkg -> ScourgeBringer [UPDATE 01.60][PCSH10308](axekin.com).pkg

Errors:
  - Title_ID PCSE01999 not found in CSV for: UP0999-PCSE01999_00-UNKNOWNGAME000.pkg
```

## 🔧 Troubleshooting

### Common Issues

**"Title_ID not found in CSV"**
- Ensure your CSV contains the correct `Media_ID` column
- Check that Title IDs match between filenames and CSV

**"Unable to extract Title_ID"**
- File might have an unsupported naming format
- Check the filename follows standard PKG conventions

**"No data loaded from CSV"**
- Verify CSV file path is correct
- Ensure CSV has proper headers and encoding (UTF-8)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🙏 Acknowledgments

- PS Vita homebrew community
- Contributors to PS Vita game databases

## 📞 Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

**⚠️ Disclaimer**: This tool is for organizing legally obtained PS Vita PKG files. Always ensure you comply with your local laws and Sony's terms of service.
