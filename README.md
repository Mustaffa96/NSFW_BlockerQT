# NSFW Blocker QT

A content filtering application built with PyQt5 that helps block unwanted NSFW content.

## Features

- System tray integration for background running
- URL and keyword-based content filtering
- Easy-to-use graphical interface
- Configurable blocking rules
- Activity logging

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

Run the application:
```bash
python main.py
```

The application will start in the system tray. Right-click the tray icon to access settings and controls.

## Requirements

- Python 3.7+
- PyQt5
- Windows OS (primary support)

## Building the Executable

1. Make sure you have Python installed
2. Download an icon file and save it as `app.ico` in the project folder
   - You can find free icons at IconEden or other icon websites
   - The icon must be in `.ico` format

3. Run the build script:
   ```batch
   build.bat
   ```

4. The executable will be created in the `dist` folder as `NSFW_Blocker.exe`

## Running the Application

1. The application requires administrator privileges to modify the hosts file
2. Right-click `NSFW_Blocker.exe` and select "Run as administrator"
3. The application will run in the system tray

## Credits

Created by Mustaffa96 (https://github.com/Mustaffa96/NSFW_BlockerQT)
