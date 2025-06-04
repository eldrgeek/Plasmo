import type { PlasmoCSConfig } from "plasmo"

export const config: PlasmoCSConfig = {
  matches: ["<all_urls>"],
  all_frames: true
}

console.log("Content script loaded on:", window.location.href)

// Function to highlight text on the page
const highlightText = (text: string, color: string = "#ffff00") => {
  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    null,
    false
  )

  const textNodes: Text[] = []
  let node: Node | null

  while ((node = walker.nextNode())) {
    if (node.nodeValue && node.nodeValue.toLowerCase().includes(text.toLowerCase())) {
      textNodes.push(node as Text)
    }
  }

  textNodes.forEach((textNode) => {
    const parent = textNode.parentNode
    if (!parent) return

    const text = textNode.nodeValue || ""
    const regex = new RegExp(`(${text})`, "gi")
    const parts = text.split(regex)

    const fragment = document.createDocumentFragment()
    parts.forEach((part) => {
      if (part.toLowerCase() === text.toLowerCase()) {
        const span = document.createElement("span")
        span.style.backgroundColor = color
        span.style.padding = "2px"
        span.style.borderRadius = "2px"
        span.textContent = part
        fragment.appendChild(span)
      } else {
        fragment.appendChild(document.createTextNode(part))
      }
    })

    parent.replaceChild(fragment, textNode)
  })
}

// Listen for messages from popup or background script
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  console.log("Content script received message:", request)

  switch (request.action) {
    case "highlight":
      highlightText(request.text, request.color)
      sendResponse({ success: true, message: "Text highlighted" })
      break

    case "getPageInfo":
      sendResponse({
        title: document.title,
        url: window.location.href,
        wordCount: document.body.innerText.split(/\s+/).length
      })
      break

    case "scrollToTop":
      window.scrollTo({ top: 0, behavior: "smooth" })
      sendResponse({ success: true })
      break

    case "injectCSS":
      const style = document.createElement("style")
      style.textContent = request.css
      document.head.appendChild(style)
      sendResponse({ success: true })
      break

    default:
      sendResponse({ error: "Unknown action" })
  }

  return true // Keep message channel open
})

// Add a floating button to demonstrate content script capabilities
const createFloatingButton = () => {
  const button = document.createElement("button")
  button.textContent = "🚀"
  button.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    z-index: 10000;
    width: 50px;
    height: 50px;
    border-radius: 25px;
    border: none;
    background: #1a73e8;
    color: white;
    font-size: 20px;
    cursor: pointer;
    box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    transition: transform 0.2s;
  `

  button.addEventListener("mouseenter", () => {
    button.style.transform = "scale(1.1)"
  })

  button.addEventListener("mouseleave", () => {
    button.style.transform = "scale(1)"
  })

  button.addEventListener("click", () => {
    // Send message to background script
    chrome.runtime.sendMessage({
      action: "showNotification",
      message: `Hello from ${document.title}!`
    })
  })

  document.body.appendChild(button)
}

// Only add the button on specific sites (to avoid clutter)
if (window.location.hostname.includes("example.com") || 
    window.location.hostname.includes("github.com")) {
  createFloatingButton()
}

// Monitor for dynamic content changes
const observer = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    if (mutation.type === "childList" && mutation.addedNodes.length > 0) {
      console.log("Page content changed")
      // React to dynamic content changes here
    }
  })
})

observer.observe(document.body, {
  childList: true,
  subtree: true
})
