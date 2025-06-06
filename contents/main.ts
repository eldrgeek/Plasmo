import type { PlasmoCSConfig } from "plasmo"

export const config: PlasmoCSConfig = {
  matches: ["<all_urls>"],
  all_frames: true
}

// Console log interception setup
const logArray: string[] = [];
const originalConsoleLog = console.log;

console.log = function(...args: any[]) {
  const message = args.map(arg => 
    typeof arg === 'object' ? JSON.stringify(arg) : String(arg)
  ).join(' ');
  
  logArray.push(message);
  const prefixedMessage = `${logArray.length}. ${message}`;
  
  // Call original console.log with prefixed message
  originalConsoleLog.call(console, prefixedMessage);
};

// Global reset function for CDP access
(window as any).resetLogs = function() {
  logArray.length = 0;
  console.log("🔄 Log array reset");
};

// Also add a function to get current log count
(window as any).getLogCount = function() {
  console.log(`📊 Current log count: ${logArray.length}`);
  return logArray.length;
};

// Add keyboard shortcuts for log management (Ctrl+Shift+R for reset, Ctrl+Shift+C for count)
document.addEventListener('keydown', (event) => {
  if (event.ctrlKey && event.shiftKey) {
    if (event.key === 'R') {
      event.preventDefault();
      logArray.length = 0;
      console.log("🔄 Log array reset via keyboard shortcut (Ctrl+Shift+R)");
    } else if (event.key === 'C') {
      event.preventDefault();
      console.log(`📊 Current log count: ${logArray.length} (via Ctrl+Shift+C)`);
    }
  }
});

console.log("🔧 Use Ctrl+Shift+R to reset logs, Ctrl+Shift+C to get count");

console.log("Content script loaded on:", window.location.href)

// Enhanced debugging for textarea behavior
const debugTextareaEvents = () => {
  const textareas = document.querySelectorAll('textarea');
  console.log(`Found ${textareas.length} textarea(s) on page`);
  
  textareas.forEach((textarea, index) => {
    console.log(`Setting up monitoring for textarea ${index}:`, {
      id: textarea.id,
      className: textarea.className,
      placeholder: textarea.placeholder
    });
    
    // Monitor all relevant events
    const events = ['input', 'change', 'keydown', 'keyup', 'keypress', 'focus', 'blur'];
    events.forEach(eventType => {
      textarea.addEventListener(eventType, (event) => {
        console.log(`🎯 ${eventType.toUpperCase()} event:`, {
          type: event.type,
          value: (event.target as HTMLTextAreaElement).value,
          valueLength: (event.target as HTMLTextAreaElement).value.length,
          isTrusted: event.isTrusted,
          inputType: (event as InputEvent).inputType || 'N/A',
          timeStamp: event.timeStamp
        });
      }, true);
    });
    
    // Monitor attribute changes
    const observer = new MutationObserver((mutations) => {
      mutations.forEach((mutation) => {
        if (mutation.type === 'attributes' && mutation.attributeName === 'value') {
          console.log('📝 Textarea value attribute changed:', {
            oldValue: mutation.oldValue,
            newValue: textarea.getAttribute('value'),
            currentValue: textarea.value
          });
        }
      });
    });
    
    observer.observe(textarea, {
      attributes: true,
      attributeOldValue: true,
      attributeFilter: ['value']
    });
  });
};

// Function to highlight text on the page
const highlightText = (text: string, color: string = "#ffff00") => {
  const walker = document.createTreeWalker(
    document.body,
    NodeFilter.SHOW_TEXT,
    null
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

// Utility functions for testing programmatic input
const testProgrammaticInput = (textarea: HTMLTextAreaElement, text: string) => {
  console.log('🧪 Testing programmatic input methods...');
  
  // Method 1: Direct value assignment
  console.log('Method 1: Direct value assignment');
  textarea.value = text;
  console.log('Value after direct assignment:', textarea.value);
  
  // Method 2: Set attribute
  console.log('Method 2: Set attribute');
  textarea.setAttribute('value', text);
  console.log('Value after setAttribute:', textarea.value);
  
  // Method 3: Simulate typing with events
  console.log('Method 3: Simulate typing events');
  textarea.focus();
  
  // Clear first
  textarea.value = '';
  
  // Type each character
  for (let i = 0; i < text.length; i++) {
    const char = text[i];
    
    // Dispatch keydown
    textarea.dispatchEvent(new KeyboardEvent('keydown', {
      key: char,
      bubbles: true,
      cancelable: true
    }));
    
    // Update value
    textarea.value = textarea.value + char;
    
    // Dispatch input event
    textarea.dispatchEvent(new InputEvent('input', {
      data: char,
      inputType: 'insertText',
      bubbles: true,
      cancelable: true
    }));
    
    // Dispatch keyup
    textarea.dispatchEvent(new KeyboardEvent('keyup', {
      key: char,
      bubbles: true,
      cancelable: true
    }));
  }
  
  console.log('Final value after simulated typing:', textarea.value);
};

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
      
    case "debugTextarea":
      debugTextareaEvents()
      sendResponse({ success: true, message: "Textarea debugging enabled" })
      break
      
    case "testInput":
      const textarea = document.querySelector('textarea') as HTMLTextAreaElement;
      if (textarea) {
        testProgrammaticInput(textarea, request.text || "This is a test prompt");
        sendResponse({ success: true, message: "Input test completed" });
      } else {
        sendResponse({ error: "No textarea found" });
      }
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

// Enhanced DOM monitoring
const observer = new MutationObserver((mutations) => {
  mutations.forEach((mutation) => {
    if (mutation.type === "childList" && mutation.addedNodes.length > 0) {
      console.log("📄 Page content changed")
      
      // Check if any textareas were added
      mutation.addedNodes.forEach((node) => {
        if (node.nodeType === Node.ELEMENT_NODE) {
          const element = node as Element;
          const newTextareas = element.querySelectorAll('textarea');
          if (newTextareas.length > 0) {
            console.log(`🆕 ${newTextareas.length} new textarea(s) added to DOM`);
            setTimeout(debugTextareaEvents, 100); // Setup monitoring after a brief delay
          }
        }
      });
    }
    
    // Monitor attribute changes on textareas
    if (mutation.type === "attributes" && 
        mutation.target.nodeType === Node.ELEMENT_NODE &&
        (mutation.target as Element).tagName === 'TEXTAREA') {
      console.log("🔄 Textarea attribute changed:", {
        attribute: mutation.attributeName,
        oldValue: mutation.oldValue,
        newValue: (mutation.target as Element).getAttribute(mutation.attributeName || '')
      });
    }
  })
})

observer.observe(document.body, {
  childList: true,
  subtree: true,
  attributes: true,
  attributeOldValue: true
})

// Initialize textarea monitoring when page loads
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', debugTextareaEvents);
} else {
  debugTextareaEvents();
}

// Only add the button on specific sites (to avoid clutter)
if (window.location.hostname.includes("example.com") || 
    window.location.hostname.includes("github.com") ||
    window.location.hostname.includes("chatgpt.com") ||
    window.location.hostname.includes("bolt.new")) {
  createFloatingButton()
}
