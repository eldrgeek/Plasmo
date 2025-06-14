# My Plasmo Chrome Extension

A basic Chrome extension built with [Plasmo](https://www.plasmo.com/), demonstrating modern extension development with React, TypeScript, and hot reloading.

## Features

- 🎨 Modern React-based popup interface
- ⚙️ Full-featured options page
- 🔧 Background service worker
- 📄 Content script injection
- 💾 Chrome storage integration
- 🎯 TypeScript support
- 🔥 Hot reloading during development

## Project Structure

```
my-plasmo-extension/
├── popup.tsx              # Main popup component
├── style.css             # Popup styles
├── options.tsx           # Options page component
├── options.css           # Options page styles
├── background.ts         # Service worker background script
├── contents/
│   └── main.ts          # Content script
├── package.json         # Dependencies and scripts
└── README.md           # This file
```

## Getting Started

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- Google Chrome or Chromium

### Platform Support

#### 🍎 macOS (Native)
Follow the standard setup below.

#### 🐧 Linux (Full Support)
**Quick Linux Setup:**
```bash
git clone <your-repo-url>
cd my-plasmo-extension
chmod +x linux_setup.sh && ./linux_setup.sh
```
See `LINUX_QUICK_START.md` for details.

#### 🪟 Windows (Coming Soon)
Windows support is planned but not yet implemented.

### Installation

1. Clone this repository:
   ```bash
   git clone <your-repo-url>
   cd my-plasmo-extension
   ```

2. Install dependencies:
   ```bash
   npm install
   # or for Linux users after running linux_setup.sh:
   pnpm install
   ```

3. Start development server:
   ```bash
   npm run dev
   # or:
   pnpm dev
   ```

4. Open Chrome and navigate to `chrome://extensions/`

5. Enable "Developer mode" (toggle in top right)

6. Click "Load unpacked" and select the `build/chrome-mv3-dev` folder

### Building for Production

```bash
npm run build
npm run package
```

This creates a packaged extension in the `build/` directory.

## Extension Components

### Popup (`popup.tsx`)
- Main interface when clicking the extension icon
- Demonstrates React state management
- Integrates with Chrome APIs
- Opens options page

### Options Page (`options.tsx`)
- Full-featured settings page
- Saves preferences to Chrome storage
- Accessible via popup or `chrome://extensions`

### Background Script (`background.ts`)
- Service worker for background tasks
- Handles extension lifecycle events
- Manages notifications and tab updates
- Periodic background tasks

### Content Script (`contents/main.ts`)
- Runs on web pages
- Can modify page content
- Communicates with popup and background
- Adds floating button on specific sites

## Chrome APIs Used

- `chrome.storage` - Persistent settings storage
- `chrome.tabs` - Tab information and management
- `chrome.runtime` - Message passing between components
- `chrome.notifications` - System notifications
- `chrome.action` - Extension icon interactions

## Development Tips

### Hot Reloading
Plasmo provides automatic hot reloading during development. Changes to your code will automatically reload the extension.

### Debugging
- Use Chrome DevTools for popup and options page
- Check `chrome://extensions` for background script logs
- Use `console.log()` in content scripts (visible in page DevTools)

### Adding New Features

1. **New Content Scripts**: Create files in `contents/` directory
2. **Additional Pages**: Add new `.tsx` files in root directory
3. **Static Assets**: Place in `assets/` directory
4. **More Permissions**: Add to `manifest.permissions` in `package.json`

## Permissions

Current permissions:
- `activeTab` - Access current tab information
- `storage` - Save user preferences

To add more permissions, update the `manifest.permissions` array in `package.json`.

## Common Use Cases

### Sending Messages Between Components

```typescript
// From popup to background
chrome.runtime.sendMessage({ action: "doSomething" })

// From content script to popup
chrome.runtime.sendMessage({ action: "pageInfo", data: {...} })
```

### Storing User Data

```typescript
// Save data
chrome.storage.sync.set({ key: value })

// Load data
chrome.storage.sync.get(["key"], (result) => {
  console.log(result.key)
})
```

### Injecting Content Scripts

Content scripts automatically inject based on the `matches` pattern in the config. Modify `contents/main.ts` to change target sites.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## Resources

- [Plasmo Documentation](https://docs.plasmo.com/)
- [Chrome Extension APIs](https://developer.chrome.com/docs/extensions/reference/)
- [Manifest V3 Guide](https://developer.chrome.com/docs/extensions/mv3/intro/)

## License

MIT License - feel free to use this as a starting point for your own extensions!

## Gemini Native Injector

The `GeminiNativeInjector` class provides cross-platform automation for interacting with the Gemini AI chat interface using native keyboard inputs. This class is designed to work across macOS, Windows, and Linux platforms, leveraging platform-specific tools like AppleScript, PowerShell, and xdotool.

### Key Functions

- **`__init__`**: Initializes the injector and determines the platform.

- **`_execute_applescript`**: Executes AppleScript commands on macOS.

- **`_execute_powershell`**: Executes PowerShell commands on Windows.

- **`_execute_xdotool`**: Executes xdotool commands on Linux.

- **`copy_to_clipboard`**: Copies text to the system clipboard, with platform-specific implementations.

- **`paste_from_clipboard`**: Pastes text from the clipboard using native keyboard shortcuts.

- **`focus_browser`**: Focuses the specified web browser application.

- **`send_keyboard_shortcut`**: Sends a keyboard shortcut to the focused application.

- **`type_text`**: Types text into the focused input with an optional typing delay for more human-like input.

- **`send_enter`**: Sends the Enter key.

- **`send_tab`**: Sends the Tab key for navigation.

- **`click_at_coordinates`**: Clicks at specific screen coordinates.

- **`inject_gemini_prompt`**: Injects a prompt into the Gemini AI interface using native keyboard automation. It supports both clipboard and typing methods, with options for tab navigation and typing delay.

### Usage

The `GeminiNativeInjector` can be used via the command line to automate the injection of prompts into the Gemini AI chat interface. It supports various options for browser focus, clipboard usage, and typing delay, making it flexible for different automation needs.

### Integration

For integration with another Cursor instance, ensure that the platform-specific dependencies (AppleScript, PowerShell, xdotool) are available on the target system. The `inject_gemini_prompt` function is the primary entry point for automation and can be customized to fit specific integration requirements.

### Example

To use the injector from the command line:

```bash
python gemini_native_injector.py 'Your prompt here' --browser=Chrome --use-clipboard
```

This command will focus the Chrome browser, copy the prompt to the clipboard, and paste it into the Gemini AI chat interface.
