import SwiftUI
import AppKit
import Foundation
import Speech

@main
struct InstantCaptureApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate
    
    var body: some Scene {
        Settings {
            EmptyView()
        }
    }
}

class AppDelegate: NSObject, NSApplicationDelegate {
    var statusItem: NSStatusItem?
    var captureWindow: CaptureWindow?
    
    func applicationDidFinishLaunching(_ notification: Notification) {
        // Hide dock icon
        NSApp.setActivationPolicy(.accessory)
        
        // Setup global hotkey (Cmd+Shift+T)
        setupGlobalHotkey()
        
        // Setup status bar item
        setupStatusBar()
        
        print("🎯 Instant AI Capture ready! Press Cmd+Shift+T anywhere")
    }
    
    func setupStatusBar() {
        statusItem = NSStatusBar.system.statusItem(withLength: NSStatusItem.variableLength)
        statusItem?.button?.title = "🎯"
        statusItem?.button?.action = #selector(showCapture)
        statusItem?.button?.target = self
    }
    
    func setupGlobalHotkey() {
        // Register Cmd+Shift+T
        let hotkey = MASShortcut(
            keyCode: kVK_ANSI_T,
            modifierFlags: [.command, .shift]
        )
        
        MASShortcutMonitor.shared().register(hotkey) { [weak self] in
            DispatchQueue.main.async {
                self?.showCapture()
            }
        }
    }
    
    @objc func showCapture() {
        if captureWindow == nil {
            captureWindow = CaptureWindow()
        }
        captureWindow?.showWindow()
    }
}

class CaptureWindow: NSWindow {
    private var captureView: CaptureView!
    
    override init(contentRect: NSRect, styleMask style: NSWindow.StyleMask, backing backingStoreType: NSWindow.BackingStoreType, defer flag: Bool) {
        super.init(contentRect: NSRect(x: 0, y: 0, width: 500, height: 350), styleMask: [.titled, .closable], backing: .buffered, defer: false)
        
        setupWindow()
        setupContent()
    }
    
    convenience init() {
        self.init(contentRect: .zero, styleMask: [.titled, .closable], backing: .buffered, defer: false)
    }
    
    func setupWindow() {
        title = "🎯 AI Capture"
        center()
        level = .floating // Always on top!
        isReleasedWhenClosed = false
        
        // Make it look modern
        titlebarAppearsTransparent = true
        isMovableByWindowBackground = true
        
        // Background blur effect
        if let visualEffect = NSVisualEffectView() as NSVisualEffectView? {
            visualEffect.blendingMode = .behindWindow
            visualEffect.material = .hudWindow
            visualEffect.state = .active
            contentView = visualEffect
        }
    }
    
    func setupContent() {
        captureView = CaptureView()
        let hostingView = NSHostingView(rootView: captureView)
        contentView?.addSubview(hostingView)
        
        hostingView.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            hostingView.topAnchor.constraint(equalTo: contentView!.topAnchor),
            hostingView.leadingAnchor.constraint(equalTo: contentView!.leadingAnchor),
            hostingView.trailingAnchor.constraint(equalTo: contentView!.trailingAnchor),
            hostingView.bottomAnchor.constraint(equalTo: contentView!.bottomAnchor)
        ])
    }
    
    func showWindow() {
        makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
        captureView.focusInput()
    }
}

struct CaptureView: View {
    @State private var taskText = ""
    @State private var isRecording = false
    @State private var statusMessage = ""
    @State private var statusType: StatusType = .normal
    
    enum StatusType {
        case normal, success, error, processing
        
        var color: Color {
            switch self {
            case .normal: return .secondary
            case .success: return .green
            case .error: return .red
            case .processing: return .blue
            }
        }
    }
    
    var body: some View {
        VStack(spacing: 20) {
            // Header
            VStack(spacing: 5) {
                Text("🎯 AI Capture")
                    .font(.title)
                    .fontWeight(.bold)
                
                Text("Tell your sidekick what's on your mind")
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
            
            // Text input
            TextEditor(text: $taskText)
                .frame(minHeight: 120)
                .padding(12)
                .background(Color(.textBackgroundColor).opacity(0.5))
                .cornerRadius(10)
                .overlay(
                    RoundedRectangle(cornerRadius: 10)
                        .stroke(Color.blue.opacity(0.3), lineWidth: 1)
                )
            
            // Buttons
            HStack(spacing: 12) {
                Button(action: startVoiceRecording) {
                    Label(isRecording ? "🎤 Listening..." : "🎤 Voice", systemImage: "")
                        .foregroundColor(isRecording ? .white : .red)
                }
                .padding(.horizontal, 20)
                .padding(.vertical, 10)
                .background(isRecording ? Color.red : Color.red.opacity(0.1))
                .cornerRadius(8)
                .disabled(isRecording)
                
                Button(action: sendToClaude) {
                    Label("🤖 Send to Claude", systemImage: "")
                        .foregroundColor(.white)
                }
                .padding(.horizontal, 20)
                .padding(.vertical, 10)
                .background(LinearGradient(colors: [.blue, .purple], startPoint: .leading, endPoint: .trailing))
                .cornerRadius(8)
                .disabled(taskText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                
                Button(action: closeWindow) {
                    Label("❌ Cancel", systemImage: "")
                }
                .padding(.horizontal, 20)
                .padding(.vertical, 10)
                .background(Color.gray.opacity(0.2))
                .cornerRadius(8)
            }
            
            // Status
            Text(statusMessage)
                .font(.caption)
                .foregroundColor(statusType.color)
                .frame(minHeight: 20)
        }
        .padding(30)
        .frame(width: 500, height: 350)
    }
    
    func focusInput() {
        // Focus will happen automatically with SwiftUI
    }
    
    func startVoiceRecording() {
        isRecording = true
        statusMessage = "🎤 Listening... speak now!"
        statusType = .processing
        
        // TODO: Implement speech recognition
        // For now, simulate recording
        DispatchQueue.main.asyncAfter(deadline: .now() + 3) {
            isRecording = false
            taskText = "Voice input captured (simulated)"
            statusMessage = "✅ Voice captured!"
            statusType = .success
        }
    }
    
    func sendToClaude() {
        guard !taskText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty else { return }
        
        statusMessage = "🤖 Processing with Claude..."
        statusType = .processing
        
        // TODO: Implement Claude API integration
        // For now, simulate API call
        DispatchQueue.main.asyncAfter(deadline: .now() + 2) {
            // Save to GTD file
            saveToGTD(task: taskText)
            
            statusMessage = "✅ Task captured and organized!"
            statusType = .success
            
            // Close window after brief delay
            DispatchQueue.main.asyncAfter(deadline: .now() + 1.5) {
                closeWindow()
            }
        }
    }
    
    func saveToGTD(task: String) {
        let timestamp = DateFormatter.localizedString(from: Date(), dateStyle: .short, timeStyle: .short)
        let entry = "- [ ] \(task) [\(timestamp)]\n"
        
        // Save to GTD inbox
        let gtdPath = FileManager.default.homeDirectoryForCurrentUser
            .appendingPathComponent("Projects/Plasmo/gtd/inbox.md")
        
        do {
            if !FileManager.default.fileExists(atPath: gtdPath.path) {
                try "# 📥 BRAIN DUMP INBOX\n\n".write(to: gtdPath, atomically: true, encoding: .utf8)
            }
            
            let handle = try FileHandle(forWritingTo: gtdPath)
            handle.seekToEndOfFile()
            handle.write(entry.data(using: .utf8)!)
            handle.closeFile()
            
            // Show native notification
            let notification = NSUserNotification()
            notification.title = "🎯 AI Capture Complete"
            notification.informativeText = "Task saved to GTD inbox"
            notification.soundName = NSUserNotificationDefaultSoundName
            NSUserNotificationCenter.default.deliver(notification)
            
        } catch {
            print("Error saving to GTD: \(error)")
        }
    }
    
    func closeWindow() {
        NSApp.windows.first(where: { $0.title == "🎯 AI Capture" })?.close()
        taskText = ""
        statusMessage = ""
        statusType = .normal
    }
}

// Add this for hotkey support (you'll need to add MASShortcut framework)
import Carbon

extension CaptureView {
    func setupKeyboardShortcuts() {
        // Cmd+Enter to send
        // Escape to cancel
    }
}
