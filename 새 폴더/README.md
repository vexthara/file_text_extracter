# Game Text Translator

A high-performance hybrid Python/C++ tool for extracting and translating text from game files. Perfect for game localization projects!

## Features

- **Fast Text Extraction**: Uses C++ for high-speed file scanning and text extraction
- **Smart Pattern Recognition**: Automatically detects various text patterns in game files
- **Chunk Management**: Automatically splits long texts into manageable chunks (up to 50,000 characters)
- **Translation Management**: Easy-to-use GUI for managing translations
- **File Format Support**: Supports Python, C++, JavaScript, XML, JSON, and many other formats
- **Hybrid Architecture**: Falls back to pure Python if C++ module isn't available

## Installation

### Prerequisites

- Python 3.6 or higher
- C++ compiler (for building the optimized module)
- Windows, Linux, or macOS

### Quick Start

1. **Clone or download this repository**
2. **Run the build script**:
   ```bash
   # Windows
   build.bat
   
   # Linux/macOS
   chmod +x build.sh
   ./build.sh
   ```
3. **Run the program**:
   ```bash
   python game_translator.py
   ```

### Manual Installation

If the build script doesn't work, you can install manually:

```bash
# Install requirements
pip install -r requirements.txt

# Build C++ extension (optional, for better performance)
python setup.py build_ext --inplace

# Run the program
python game_translator.py
```

## Usage

### 1. Extract Texts

1. **Select Source Directory**: Choose the folder containing your game files
2. **Select Output Directory**: Choose where to save extracted texts
3. **Choose File Extensions**: Enter the file extensions you want to process (comma-separated, e.g., `.csv,.erb,.erh`)
   - Use preset buttons: **Code** (programming files), **Web** (web files), **All** (all supported types)
   - Default: `.csv,.erb,.erh`
4. **Click "Extract Texts"**: The program will scan files with selected extensions and extract text strings
5. **View Results**: Check the "Extracted Texts" tab to see all found texts

### 2. Translate Texts

1. **Select a Text**: Click on any text in the list
2. **Enter Translation**: Type your translation in the editor
3. **Save Translation**: Click "Save Translation" to store it
4. **Repeat**: Continue for all texts you want to translate

### 3. Manage Translations

- **Save Translation File**: Export all translations to a JSON file
- **Load Translation File**: Import previously saved translations
- **Apply Translations**: Replace original texts with translations in source files

### 4. View Statistics

Check the "Statistics" tab to see:
- Number of files processed
- Number of texts found
- Processing time
- Translation progress

## Supported File Types

The tool automatically detects text in these file types:

- **Data Files**: `.csv` (Comma-Separated Values), `.erb` (Embedded Ruby), `.erh` (Embedded Ruby Header) - **Default**
- **Programming Languages**: `.py`, `.cpp`, `.c`, `.h`, `.hpp`, `.cs`, `.java`, `.js`, `.ts`, `.jsx`, `.tsx`
- **Data Formats**: `.xml`, `.json`, `.yaml`, `.yml`, `.ini`, `.cfg`
- **Game Files**: `.unity`, `.prefab`, `.asset`, `.scene`
- **Scripts**: `.lua`, `.rpy`
- **Text Files**: `.txt`

## File Extension Selection

The tool allows you to specify which file types to process:

### Preset Buttons
- **Code**: `.py,.cpp,.c,.h,.hpp,.cs,.java` - Programming files
- **Web**: `.html,.css,.js,.ts,.jsx,.tsx,.json,.xml` - Web development files  
- **All**: All supported file types (comprehensive list)

### Custom Extensions
Enter any file extensions separated by commas:
- Examples: `.py,.cpp,.js` or `.txt,.xml,.json`
- Extensions are case-insensitive
- Must start with a dot (e.g., `.py` not `py`)

## Text Pattern Detection

The tool recognizes these common text patterns:

- Quoted strings: `"Hello World"`, `'Hello World'`
- Key-value pairs: `text: "Hello"`, `label: "Start"`
- XML tags: `<text>Hello</text>`, `<string>Hello</string>`
- And many more...

## Performance

- **With C++ Module**: 10-50x faster than pure Python
- **Without C++ Module**: Still fast with pure Python fallback
- **Memory Efficient**: Processes large codebases without memory issues
- **Chunked Processing**: Handles very long texts (up to 50,000 characters) by splitting them intelligently

## File Structure

```
game-text-translator/
├── game_translator.py      # Main Python GUI application
├── text_extractor.cpp      # C++ extension module
├── setup.py               # Build configuration
├── requirements.txt       # Python dependencies
├── build.bat             # Windows build script
├── build.sh              # Linux/macOS build script
└── README.md             # This file
```

## Troubleshooting

### C++ Module Won't Build

If you get errors building the C++ module:

1. **Install Visual Studio Build Tools** (Windows)
2. **Install Xcode Command Line Tools** (macOS)
3. **Install build-essential** (Linux): `sudo apt-get install build-essential`
4. **The program will still work** with pure Python mode

### Common Issues

- **"No module named text_extractor"**: C++ module didn't build - program will use Python fallback
- **"Permission denied"**: Make sure you have write access to output directory
- **"No texts found"**: Check that your source directory contains supported file types

## Advanced Usage

### Custom Text Patterns

You can modify the text patterns in `text_extractor.cpp` to match your specific game's text format.

### Batch Processing

For large projects, you can:
1. Extract texts from multiple directories
2. Save translation files for each
3. Merge translation files as needed
4. Apply translations in batches

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - feel free to use this tool for your game localization projects.

---

**Happy Translating!** 🎮🌍
