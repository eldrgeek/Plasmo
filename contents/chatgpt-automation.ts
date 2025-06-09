// Advanced ChatGPT automation using the same technique as bolt-automation.ts
import type { PlasmoCSConfig } from "plasmo"

export const config: PlasmoCSConfig = {
    matches: ["https://chat.openai.com/*", "https://chatgpt.com/*"],
    all_frames: false
}

// Native input value setters to bypass React (same as bolt-automation.ts)
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

// Core React _valueTracker manipulation (same as bolt-automation.ts)
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

// Advanced input function with React bypass
async function inputText(options: {
    data: { value: string; delay?: number }
    element: HTMLInputElement | HTMLTextAreaElement | HTMLDivElement
    isEditable: boolean
}) {
    const { data, element, isEditable } = options
    const { value, delay = 50 } = data

    element?.focus()
    element?.click()

    if (isEditable) {
        // Handle contenteditable divs (ChatGPT uses these!)
        console.log("🔧 Using contenteditable div technique for ChatGPT")

            // Clear existing content
            ; (element as any).innerText = ''

            // Set new text
            ; (element as any).innerText = value

        // Trigger events to notify React
        simulateEvent(element, 'input', {
            inputType: 'insertText',
            data: value,
            bubbles: true,
            cancelable: true,
        })

        simulateEvent(element, 'change', {
            bubbles: true,
            cancelable: true,
        })

        // Also trigger focus event
        simulateEvent(element, 'focus', {
            bubbles: true,
        })

    } else {
        // Handle regular input/textarea elements
        const inputElement = element as HTMLInputElement | HTMLTextAreaElement

        // Clear and set new value using React bypass
        reactJsEvent(inputElement, '')
        inputElement.value = ''

        // Set the complete value using React bypass
        reactJsEvent(inputElement, value)
        inputElement.value = value

        // Trigger events to ensure React notices the change
        simulateEvent(inputElement, 'input', {
            inputType: 'insertText',
            data: value,
            bubbles: true,
            cancelable: true,
        })

        inputElement.dispatchEvent(
            new Event('change', { bubbles: true, cancelable: true })
        )
    }

    element?.blur()
}

// Main form element handler (same approach as bolt-automation.ts)
async function handleFormElement(element: HTMLElement, data: {
    type: string
    value: string
    delay?: number
    clearValue?: boolean
}) {
    const textFields = ['INPUT', 'TEXTAREA']
    const isEditable = element.hasAttribute('contenteditable') && (element as any).isContentEditable

    console.log(`🔧 ChatGPT handleFormElement: ${data.type} with value: "${data.value}"`)
    console.log(`Element type: ${element.tagName}, isEditable: ${isEditable}`)

    if (isEditable) {
        console.log("✅ Using contenteditable div approach")
        if (data.clearValue) (element as any).innerText = ''

        await inputText({
            data: { value: data.value, delay: data.delay || 50 },
            element: element as HTMLDivElement,
            isEditable: true
        })
        return true
    }

    if (data.type === 'text-field' && textFields.includes(element.tagName)) {
        console.log("✅ Using textarea/input approach")
        const inputElement = element as HTMLInputElement | HTMLTextAreaElement

        if (data.clearValue) {
            inputElement?.select()
            reactJsEvent(inputElement, '')
            inputElement.value = ''
        }

        await inputText({
            data: { value: data.value, delay: data.delay || 50 },
            element: inputElement,
            isEditable: false
        })
        return true
    }

    // Handle other cases
    element?.focus()
    element?.blur()
    return true
}

// Find ChatGPT textarea/input with multiple selectors (updated for contenteditable)
function findChatGPTInput(): HTMLTextAreaElement | HTMLDivElement | null {
    const selectors = [
        // First try contenteditable divs (ChatGPT's preferred method)
        'div[contenteditable="true"]',
        'div[contenteditable="true"][data-id="root"]',
        // Then try textareas as fallback
        'textarea[placeholder*="Send a message"]',
        'textarea[placeholder*="Message"]',
        'textarea[data-id="root"]',
        'textarea[id*="prompt"]',
        'textarea' // fallback
    ]

    for (const selector of selectors) {
        const elements = document.querySelectorAll(selector)
        for (const element of elements) {
            if (element && (element as HTMLElement).offsetParent !== null) {
                // Check if it's visible and likely the main input
                const rect = element.getBoundingClientRect()
                if (rect.width > 100 && rect.height > 20) {
                    console.log(`✅ Found ChatGPT input with selector: ${selector}`)
                    return element as HTMLTextAreaElement | HTMLDivElement
                }
            }
        }
    }
    return null
}

// Find ChatGPT submit button (updated selectors based on testing)
function findChatGPTSubmitButton(): HTMLButtonElement | null {
    const selectors = [
        'button[data-testid="send-button"]',
        'button[data-testid="fruitjuice-send-button"]',
        'button:has(svg)', // This worked in our testing!
        'button[aria-label*="Send" i]',
        'button[title*="Send" i]',
        'form button:last-of-type',
        'button[class*="send" i]',
        'button[type="submit"]'
    ]

    for (const selector of selectors) {
        try {
            const buttons = document.querySelectorAll(selector)
            for (const btn of buttons) {
                const button = btn as HTMLButtonElement
                if (button && button.offsetParent !== null && !button.disabled) {
                    // Check if it's visible and clickable
                    const rect = button.getBoundingClientRect()
                    if (rect.width > 10 && rect.height > 10) {
                        console.log(`✅ Found ChatGPT submit button with selector: ${selector}`)
                        return button
                    }
                }
            }
        } catch (e) {
            continue
        }
    }
    return null
}

// Global automation function for MCP server to call
async function automateChatGPT(prompt: string): Promise<{ success: boolean, message: string }> {
    try {
        console.log("🤖 ChatGPT automation triggered:", prompt)

        // Find input element (prioritizing contenteditable divs)
        const inputElement = findChatGPTInput()
        if (!inputElement) {
            return { success: false, message: "ChatGPT input element not found" }
        }

        console.log("✅ Found ChatGPT input element:", inputElement.tagName)

        // Inject the prompt using advanced technique
        const success = await handleFormElement(inputElement, {
            type: "text-field",
            value: prompt,
            delay: 80, // Slower for better React compatibility
            clearValue: true
        })

        if (!success) {
            return { success: false, message: "Failed to inject prompt" }
        }

        console.log("✅ Prompt injected successfully")

        // Wait a moment for React to process
        await new Promise(resolve => setTimeout(resolve, 200))

        // Find and click submit button
        const submitBtn = findChatGPTSubmitButton()
        if (!submitBtn) {
            return { success: false, message: "ChatGPT submit button not found" }
        }

        submitBtn.click()
        console.log("✅ ChatGPT form submitted successfully")

        return { success: true, message: "ChatGPT automation completed successfully" }

    } catch (error) {
        console.error("❌ ChatGPT automation failed:", error)
        return { success: false, message: `Error: ${error instanceof Error ? error.message : String(error)}` }
    }
}

// Make automation function globally accessible for MCP server
; (window as any).automateChatGPT = automateChatGPT

    // Also provide a simpler alias
    ; (window as any).tellChatGPTTo = automateChatGPT

console.log("🤖 Advanced ChatGPT automation loaded - Ready for MCP control") 