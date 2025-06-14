// Advanced Claude.ai automation with completion detection
import type { PlasmoCSConfig } from "plasmo"

export const config: PlasmoCSConfig = {
    matches: ["https://claude.ai/*"],
    all_frames: false
}

// Native input value setters to bypass React
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

// Core React _valueTracker manipulation
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
        // Handle contenteditable divs (Claude uses these!)
        console.log("🔧 Using contenteditable div technique for Claude")

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

// Main form element handler
async function handleFormElement(element: HTMLElement, data: {
    type: string
    value: string
    delay?: number
    clearValue?: boolean
}) {
    const textFields = ['INPUT', 'TEXTAREA']
    const isEditable = element.hasAttribute('contenteditable') && (element as any).isContentEditable

    console.log(`🔧 Claude handleFormElement: ${data.type} with value: "${data.value}"`)
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

// Find Claude input with multiple selectors
function findClaudeInput(): HTMLTextAreaElement | HTMLDivElement | null {
    const selectors = [
        // First try contenteditable divs (Claude's preferred method)
        'div[contenteditable="true"]',
        'div[contenteditable="true"][data-testid*="chat"]',
        'div[contenteditable="true"][placeholder*="Talk to Claude"]',
        // Then try textareas as fallback
        'textarea[placeholder*="Talk to Claude"]',
        'textarea[placeholder*="Message Claude"]',
        'textarea[data-testid*="chat"]',
        'textarea' // fallback
    ]

    for (const selector of selectors) {
        const elements = document.querySelectorAll(selector)
        for (const element of elements) {
            if (element && (element as HTMLElement).offsetParent !== null) {
                // Check if it's visible and likely the main input
                const rect = element.getBoundingClientRect()
                if (rect.width > 100 && rect.height > 20) {
                    console.log(`✅ Found Claude input with selector: ${selector}`)
                    return element as HTMLTextAreaElement | HTMLDivElement
                }
            }
        }
    }
    return null
}

// Find Claude submit button
function findClaudeSubmitButton(): HTMLButtonElement | null {
    const selectors = [
        'button[data-testid="send-button"]',
        'button[aria-label*="Send" i]',
        'button[title*="Send" i]',
        'button:has(svg)', // Common pattern for icon buttons
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
                        console.log(`✅ Found Claude submit button with selector: ${selector}`)
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

// NEW: Robust completion detection using submit button monitoring
async function waitForClaudeCompletion(timeout: number = 120000): Promise<boolean> {
    const startTime = Date.now()
    let lastButtonState = false
    let stableCount = 0

    console.log("🕐 Waiting for Claude to complete response...")

    while (Date.now() - startTime < timeout) {
        const submitBtn = findClaudeSubmitButton()
        const isButtonEnabled = !!(submitBtn && !submitBtn.disabled && submitBtn.offsetParent !== null)

        // Also check for streaming indicators (Claude-specific)
        const streamingIndicators = document.querySelectorAll('[data-is-streaming="true"], .thinking, [aria-label*="thinking"]')
        const isStreaming = streamingIndicators.length > 0

        // Track button state changes
        if (isButtonEnabled !== lastButtonState) {
            console.log(`🔄 Submit button state changed: ${isButtonEnabled ? 'enabled' : 'disabled'}`)
            lastButtonState = isButtonEnabled
            stableCount = 0
        } else {
            stableCount++
        }

        // If button has been enabled, stable, and no streaming indicators, response is complete
        if (isButtonEnabled && !isStreaming && stableCount >= 3) {
            console.log("✅ Claude response appears complete (submit button enabled, no streaming)")
            await new Promise(resolve => setTimeout(resolve, 1000)) // Extra safety wait
            return true
        }

        await new Promise(resolve => setTimeout(resolve, 500)) // Check every 500ms
    }

    console.log("⚠️ Claude completion detection timed out")
    return false
}

// NEW: Enhanced automation with completion detection
async function automateClaudeWithCompletion(prompt: string): Promise<{
    success: boolean,
    message: string,
    responseComplete: boolean
}> {
    try {
        console.log("🤖 Claude automation with completion detection:", prompt)

        // Find input element
        const inputElement = findClaudeInput()
        if (!inputElement) {
            return { success: false, message: "Claude input element not found", responseComplete: false }
        }

        // Submit the prompt
        const success = await handleFormElement(inputElement, {
            type: "text-field",
            value: prompt,
            delay: 80,
            clearValue: true
        })

        if (!success) {
            return { success: false, message: "Failed to inject prompt", responseComplete: false }
        }

        // Wait for React to process
        await new Promise(resolve => setTimeout(resolve, 200))

        // Find and click submit button
        const submitBtn = findClaudeSubmitButton()
        if (!submitBtn) {
            return { success: false, message: "Claude submit button not found", responseComplete: false }
        }

        submitBtn.click()
        console.log("✅ Claude form submitted, waiting for completion...")

        // Inject "Processing..." to indicate we're waiting
        await new Promise(resolve => setTimeout(resolve, 1000)) // Let response start

        await handleFormElement(inputElement, {
            type: "text-field",
            value: "Processing...",
            delay: 50,
            clearValue: true
        })

        // Wait for completion
        const responseComplete = await waitForClaudeCompletion()

        // Clear the "Processing..." text
        await handleFormElement(inputElement, {
            type: "text-field",
            value: "",
            delay: 50,
            clearValue: true
        })

        return {
            success: true,
            message: "Claude automation completed",
            responseComplete
        }

    } catch (error) {
        console.error("❌ Claude automation failed:", error)
        return {
            success: false,
            message: `Error: ${error instanceof Error ? error.message : String(error)}`,
            responseComplete: false
        }
    }
}

// Global automation function for MCP server to call
async function automateClaude(prompt: string): Promise<{ success: boolean, message: string }> {
    try {
        console.log("🤖 Claude automation triggered:", prompt)

        // Find input element
        const inputElement = findClaudeInput()
        if (!inputElement) {
            return { success: false, message: "Claude input element not found" }
        }

        console.log("✅ Found Claude input element:", inputElement.tagName)

        // Inject the prompt using advanced technique
        const success = await handleFormElement(inputElement, {
            type: "text-field",
            value: prompt,
            delay: 80,
            clearValue: true
        })

        if (!success) {
            return { success: false, message: "Failed to inject prompt" }
        }

        console.log("✅ Prompt injected successfully")

        // Wait a moment for React to process
        await new Promise(resolve => setTimeout(resolve, 200))

        // Find and click submit button
        const submitBtn = findClaudeSubmitButton()
        if (!submitBtn) {
            return { success: false, message: "Claude submit button not found" }
        }

        submitBtn.click()
        console.log("✅ Claude form submitted successfully")

        return { success: true, message: "Claude automation completed successfully" }

    } catch (error) {
        console.error("❌ Claude automation failed:", error)
        return { success: false, message: `Error: ${error instanceof Error ? error.message : String(error)}` }
    }
}

// Make automation functions globally accessible for MCP server
; (window as any).automateClaude = automateClaude
    ; (window as any).automateClaudeWithCompletion = automateClaudeWithCompletion

    // Also provide simpler aliases
    ; (window as any).tellClaudeTo = automateClaude
    ; (window as any).tellClaudeToAndWait = automateClaudeWithCompletion

console.log("🤖 Advanced Claude automation loaded - Ready for MCP control") 