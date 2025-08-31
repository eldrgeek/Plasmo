// swift-tools-version:5.5
import PackageDescription

let package = Package(
    name: "InstantCapture",
    platforms: [
        .macOS(.v12)
    ],
    products: [
        .executable(name: "InstantCapture", targets: ["InstantCapture"])
    ],
    dependencies: [
        // Add MASShortcut for global hotkeys
        .package(url: "https://github.com/shpakovski/MASShortcut", from: "2.4.0")
    ],
    targets: [
        .executableTarget(
            name: "InstantCapture",
            dependencies: [
                "MASShortcut"
            ]
        )
    ]
)
