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

// NEW: Correct completion detection using button transformation monitoring
async function waitForChatGPTCompletion(originalSubmitHTML: string, originalSubmitClasses: string, timeout: number = 120000): Promise<boolean> {
    const startTime = Date.now()
    console.log("🕐 Waiting for ChatGPT to complete response using button transformation...")

    while (Date.now() - startTime < timeout) {
        const submitBtn = findChatGPTSubmitButton()

        if (submitBtn) {
            const currentHTML = submitBtn.innerHTML
            const currentClasses = submitBtn.className

            // Check if button has returned to original submit state
            // This indicates generation is complete
            if (currentHTML === originalSubmitHTML ||
                (currentHTML.includes('Send') && !currentHTML.includes('Stop'))) {
                console.log("✅ ChatGPT response complete - button returned to submit state")
                await new Promise(resolve => setTimeout(resolve, 500)) // Safety wait
                return true
            }

            // Log state changes for debugging
            if (currentHTML !== originalSubmitHTML) {
                // Still in stop/generating state
                console.log("🔄 ChatGPT still generating (button in stop state)")
            }
        } else {
            console.log("⚠️ Submit button not found during completion check")
        }

        await new Promise(resolve => setTimeout(resolve, 500)) // Check every 500ms
    }

    console.log("⚠️ ChatGPT completion detection timed out")
    return false
}

// NEW: Enhanced automation with completion detection
async function automateChatGPTWithCompletion(prompt: string): Promise<{
    success: boolean,
    message: string,
    responseComplete: boolean
}> {
    try {
        console.log("🤖 ChatGPT automation with completion detection:", prompt)

        // Find input element
        const inputElement = findChatGPTInput()
        if (!inputElement) {
            return { success: false, message: "ChatGPT input element not found", responseComplete: false }
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
        const submitBtn = findChatGPTSubmitButton()
        if (!submitBtn) {
            return { success: false, message: "ChatGPT submit button not found", responseComplete: false }
        }

        submitBtn.click()
        console.log("✅ ChatGPT form submitted, waiting for completion...")

        // Inject "Processing..." to indicate we're waiting
        await new Promise(resolve => setTimeout(resolve, 1000)) // Let response start

        await handleFormElement(inputElement, {
            type: "text-field",
            value: "Processing...",
            delay: 50,
            clearValue: true
        })

        // Store original button state before submission
        const originalSubmitHTML = submitBtn.innerHTML
        const originalSubmitClasses = submitBtn.className

        // Wait for completion using button transformation detection
        const responseComplete = await waitForChatGPTCompletion(originalSubmitHTML, originalSubmitClasses)

        // Clear the "Processing..." text
        await handleFormElement(inputElement, {
            type: "text-field",
            value: "",
            delay: 50,
            clearValue: true
        })

        return {
            success: true,
            message: "ChatGPT automation completed",
            responseComplete
        }

    } catch (error) {
        console.error("❌ ChatGPT automation failed:", error)
        return {
            success: false,
            message: `Error: ${error instanceof Error ? error.message : String(error)}`,
            responseComplete: false
        }
    }
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

// NEW: Stop generation function using discovered stop button pattern
async function stopChatGPTGeneration(): Promise<{ success: boolean, message: string }> {
    try {
        console.log("🛑 Attempting to stop ChatGPT generation...")

        // Find the submit button (which should be in stop state if generating)
        const submitBtn = findChatGPTSubmitButton()
        if (!submitBtn) {
            return { success: false, message: "Submit button not found - cannot stop generation" }
        }

        const currentHTML = submitBtn.innerHTML
        console.log("Current button HTML:", currentHTML.substring(0, 100))

        // Check if button is in stop state (different from original submit state)
        if (currentHTML.includes('Stop') || currentHTML.includes('stop') ||
            submitBtn.getAttribute('aria-label')?.includes('Stop')) {
            console.log("🎯 Stop button detected - clicking to stop generation")
            submitBtn.click()

            // Wait a moment and verify it worked
            await new Promise(resolve => setTimeout(resolve, 1000))

            const newHTML = submitBtn.innerHTML
            if (newHTML !== currentHTML) {
                return { success: true, message: "Successfully stopped ChatGPT generation" }
            } else {
                return { success: false, message: "Stop button clicked but no state change detected" }
            }
        } else {
            return { success: false, message: "ChatGPT does not appear to be generating (button not in stop state)" }
        }

    } catch (error) {
        console.error("❌ Failed to stop ChatGPT generation:", error)
        return { success: false, message: `Error: ${error instanceof Error ? error.message : String(error)}` }
    }
}

// Make automation functions globally accessible for MCP server
; (window as any).automateChatGPT = automateChatGPT
    ; (window as any).automateChatGPTWithCompletion = automateChatGPTWithCompletion
    ; (window as any).stopChatGPTGeneration = stopChatGPTGeneration

    // Also provide simpler aliases
    ; (window as any).tellChatGPTTo = automateChatGPT
    ; (window as any).tellChatGPTToAndWait = automateChatGPTWithCompletion
    ; (window as any).stopChatGPT = stopChatGPTGeneration

console.log("🤖 Advanced ChatGPT automation loaded - Ready for MCP control") 