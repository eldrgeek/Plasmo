// Streamlined Bolt.new automation - No UI, MCP server controlled
import type { PlasmoCSConfig } from "plasmo"

export const config: PlasmoCSConfig = {
    matches: ["https://bolt.new/*"],
    all_frames: false
}

// Native input value setter to bypass React
const nativeInputValueSetter = Object.getOwnPropertyDescriptor(
    window.HTMLInputElement.prototype,
    'value'
)?.set

const nativeTextAreaValueSetter = Object.getOwnPropertyDescriptor(
    window.HTMLTextAreaElement.prototype,
    'value'
)?.set

function simulateEvent(element: HTMLElement, eventType: string, eventData: any) {
    let event: Event

    if (eventType === 'input') {
        event = new InputEvent(eventType, eventData)
    } else if (eventType.startsWith('key')) {
        event = new KeyboardEvent(eventType, eventData)
    } else {
        event = new Event(eventType, eventData)
    }

    element.dispatchEvent(event)
}

function reactJsEvent(element: HTMLInputElement | HTMLTextAreaElement, value: string) {
    if (!(element as any)._valueTracker) return

    const previousValue = element.value

    if (element instanceof HTMLInputElement && nativeInputValueSetter) {
        nativeInputValueSetter.call(element, value)
    } else if (element instanceof HTMLTextAreaElement && nativeTextAreaValueSetter) {
        nativeTextAreaValueSetter.call(element, value)
    }

    if ((element as any)._valueTracker) {
        (element as any)._valueTracker.setValue(previousValue)
    }
}

// Optimized input function - no delays between keystrokes
async function fastInputText(element: HTMLInputElement | HTMLTextAreaElement, text: string) {
    element?.focus()
    element?.click()

    // Clear existing value
    element?.select()
    reactJsEvent(element, '')
    element.value = ''

    // Set the complete value at once
    reactJsEvent(element, element.value)
    element.value = text

    // Trigger events to ensure React notices the change
    simulateEvent(element, 'input', {
        inputType: 'insertText',
        data: text,
        bubbles: true,
        cancelable: true,
    })

    element.dispatchEvent(
        new Event('change', { bubbles: true, cancelable: true })
    )

    element?.blur()
}

// Find textarea function
function findTextarea(): HTMLTextAreaElement | null {
    const selectors = [
        'textarea[placeholder*="help" i]',
        'textarea[placeholder*="describe" i]',
        'textarea[placeholder*="build" i]',
        'textarea[class*="prompt" i]',
        'textarea[data-id*="chat" i]',
        'textarea' // fallback
    ]

    for (const selector of selectors) {
        const textarea = document.querySelector(selector) as HTMLTextAreaElement
        if (textarea && textarea.offsetParent !== null) {
            return textarea
        }
    }
    return null
}

// Find submit button function
function findSubmitButton(): HTMLButtonElement | null {
    const selectors = [
        'button.absolute[class*="top-"][class*="right-"][class*="bg-accent-500"]',
        'button[class*="absolute"][class*="top-"][class*="right-"]',
        'button:has(svg)',
        'button[type="submit"]',
        'form button:last-of-type',
        'button[class*="send" i]',
        'button[class*="submit" i]'
    ]

    for (const selector of selectors) {
        try {
            const btn = document.querySelector(selector) as HTMLButtonElement
            if (btn && btn.offsetParent !== null && !btn.disabled) {
                return btn
            }
        } catch (e) {
            continue
        }
    }
    return null
}

// Global automation function for MCP server to call
async function automateBolt(prompt: string): Promise<{ success: boolean, message: string }> {
    try {
        console.log("🤖 MCP automation triggered:", prompt)

        // Find textarea
        const textarea = findTextarea()
        if (!textarea) {
            return { success: false, message: "Textarea not found" }
        }

        // Input the prompt
        await fastInputText(textarea, prompt)
        console.log("✅ Prompt injected successfully")

        // Wait a moment for React to process
        await new Promise(resolve => setTimeout(resolve, 100))

        // Find and click submit button
        const submitBtn = findSubmitButton()
        if (!submitBtn) {
            return { success: false, message: "Submit button not found" }
        }

        submitBtn.click()
        console.log("✅ Form submitted successfully")

        return { success: true, message: "Automation completed successfully" }

    } catch (error) {
        console.error("❌ Automation failed:", error)
        return { success: false, message: `Error: ${error instanceof Error ? error.message : String(error)}` }
    }
}

// Make automation function globally accessible for MCP server
; (window as any).automateBolt = automateBolt

console.log("🤖 Streamlined Bolt automation loaded - Ready for MCP control") 