# NSFW Blocker QT

A powerful content filtering application built with PyQt5 that helps protect users from unwanted NSFW (Not Safe For Work) content through intelligent URL blocking and content analysis.

## Key Features

- **Advanced Content Filtering**
  - URL and domain-based blocking
  - Keyword-based content detection
  - Separate explicit and moderate content categories
  - Real-time content analysis with scoring system
  - Bulk URL import capability

- **User-Friendly Interface**
  - Modern and intuitive PyQt5-based GUI
  - System tray integration for background operation
  - Clear visual indicators for content safety
  - Progress bars showing safety scores
  - Detailed match reporting

- **System Integration**
  - Runs efficiently in the background
  - Administrator mode for system-level blocking
  - Automatic DNS cache management
  - Persistent settings storage

## Installation

1. Clone the repository:
```bash
git clone https://github.com/Mustaffa96/NSFW_BlockerQT.git
cd NSFW_BlockerQT
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Run the application with administrator privileges:
```bash
python main.py
```

2. The application will start with a welcome screen and minimize to the system tray
3. Access features through the system tray icon:
   - Add/remove blocked URLs
   - Manage keyword filters
   - Toggle blocking on/off
   - View content analysis results

## Requirements

- Python 3.7+
- PyQt5
- Windows OS (primary support)
- Administrator privileges for system modifications

## Building the Executable

1. Ensure Python and required dependencies are installed
2. Place your desired application icon as `app.ico` in the project folder
3. Run the build script:
```batch
build.bat
```
4. Find the compiled executable in the `dist` folder as `NSFW_Blocker.exe`

## Running the Application

1. Right-click `NSFW_Blocker.exe` and select "Run as administrator"
2. The application will start and minimize to the system tray
3. Access all features through the tray icon
4. Monitor content safety through the main window

## Features in Detail

- **URL Management**
  - Add individual URLs or bulk import
  - Automatic URL validation
  - Easy enable/disable of blocking

- **Content Analysis**
  - Real-time webpage scanning
  - Content safety scoring
  - Keyword match highlighting
  - Categorized content detection

- **System Integration**
  - Automatic DNS cache flushing
  - Host file management
  - System startup integration
  - Background operation

## Credits

Created by [Mustaffa96](https://github.com/Mustaffa96/NSFW_BlockerQT)

## License

This project is open source and available under the MIT License.
