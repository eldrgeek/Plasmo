#!/usr/bin/env python3
"""
Claude Interface Automated Investigator
Systematically investigates web LLM interfaces to learn interaction patterns
"""

import asyncio
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import uuid

class ClaudeInterfaceInvestigator:
    def __init__(self):
        self.session_id = f"investigation_{int(time.time())}"
        self.results = {
            "session_id": self.session_id,
            "timestamp": datetime.now().isoformat(),
            "phases": {},
            "elements": {},
            "candidates": [],
            "final_results": {}
        }
        self.chrome_tab_id = "5913F1B9C3DA841BBFF3695C9745BDED"  # Claude tab
        
    async def send_status(self, message: str, priority: str = "info", icon: str = "robot"):
        """Send status update through Agent Bridge"""
        try:
            # Use the frontrow-modal tools
            from stdioserver_claude import frontrow_modal
            await frontrow_modal.modal_show_message(
                message=message, 
                duration=4000, 
                priority=priority, 
                icon=icon
            )
        except Exception as e:
            print(f"Status update failed: {e}")
    
    async def execute_js(self, code: str) -> Dict[str, Any]:
        """Execute JavaScript in Claude tab"""
        try:
            from stdioserver_claude import execute_javascript
            result = execute_javascript(code=code, tab_id=self.chrome_tab_id)
            return result
        except Exception as e:
            print(f"JavaScript execution failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def phase_1_reconnaissance(self):
        """Phase 1: Complete DOM reconnaissance and mapping"""
        await self.send_status("🔍 Phase 1: Reconnaissance & Element Mapping", "info", "search")
        
        reconnaissance_js = """
        (function reconnaissance() {
            console.log('🔍 AUTOMATED RECONNAISSANCE PHASE');
            
            const results = {
                timestamp: Date.now(),
                page_info: {
                    url: window.location.href,
                    title: document.title,
                    dimensions: {
                        width: window.innerWidth,
                        height: window.innerHeight
                    }
                },
                elements: {
                    buttons: [],
                    inputs: [],
                    links: [],
                    containers: []
                },
                spatial_map: {},
                observer_status: null
            };
            
            // 1. Map all buttons
            const buttons = document.querySelectorAll('button');
            Array.from(buttons).forEach((btn, i) => {
                const rect = btn.getBoundingClientRect();
                const hasIcon = btn.querySelector('svg') !== null;
                const text = btn.textContent?.trim() || '';
                const ariaLabel = btn.getAttribute('aria-label') || '';
                
                results.elements.buttons.push({
                    index: i,
                    text: text,
                    ariaLabel: ariaLabel,
                    hasIcon: hasIcon,
                    disabled: btn.disabled,
                    visible: rect.width > 0 && rect.height > 0,
                    position: {
                        x: Math.round(rect.left),
                        y: Math.round(rect.top),
                        width: Math.round(rect.width),
                        height: Math.round(rect.height)
                    },
                    className: btn.className,
                    id: btn.id || null,
                    type: btn.type || 'button'
                });
            });
            
            // 2. Map all inputs
            const inputs = document.querySelectorAll('input, textarea, [contenteditable], select');
            Array.from(inputs).forEach((input, i) => {
                const rect = input.getBoundingClientRect();
                
                results.elements.inputs.push({
                    index: i,
                    tagName: input.tagName,
                    type: input.type || 'none',
                    placeholder: input.placeholder || '',
                    name: input.name || '',
                    id: input.id || null,
                    contentEditable: input.contentEditable || 'false',
                    position: {
                        x: Math.round(rect.left),
                        y: Math.round(rect.top),
                        width: Math.round(rect.width),
                        height: Math.round(rect.height)
                    },
                    className: input.className,
                    isMainInput: input.contentEditable === 'true'
                });
            });
            
            // 3. Map key links (first 20)
            const links = document.querySelectorAll('a[href]');
            Array.from(links).slice(0, 20).forEach((link, i) => {
                const rect = link.getBoundingClientRect();
                
                results.elements.links.push({
                    index: i,
                    text: link.textContent?.trim().substring(0, 50) || '',
                    href: link.href,
                    className: link.className,
                    visible: rect.width > 0 && rect.height > 0,
                    position: {
                        x: Math.round(rect.left),
                        y: Math.round(rect.top),
                        width: Math.round(rect.width),
                        height: Math.round(rect.height)
                    }
                });
            });
            
            // 4. Find main containers
            const mainInput = document.querySelector('div[contenteditable="true"]');
            if (mainInput) {
                const inputParent = mainInput.closest('div');
                const inputGrandParent = inputParent?.closest('div');
                
                results.spatial_map.main_input = {
                    element: mainInput.className,
                    parent: inputParent?.className || null,
                    grandparent: inputGrandParent?.className || null,
                    position: mainInput.getBoundingClientRect()
                };
                
                // Find buttons in input hierarchy
                const nearbyButtons = [];
                [inputParent, inputGrandParent].forEach(container => {
                    if (container) {
                        const containerButtons = container.querySelectorAll('button');
                        Array.from(containerButtons).forEach(btn => {
                            const btnIndex = Array.from(buttons).indexOf(btn);
                            if (btnIndex >= 0) {
                                nearbyButtons.push(btnIndex);
                            }
                        });
                    }
                });
                
                results.spatial_map.input_area_buttons = nearbyButtons;
            }
            
            // 5. Check DOM observer status
            if (window.claudeObserver) {
                results.observer_status = {
                    active: true,
                    inputSelector: window.claudeObserver.inputSelector,
                    submitSelector: window.claudeObserver.submitSelector,
                    interactionCount: window.claudeObserver.getInteractions().length
                };
            } else {
                results.observer_status = { active: false };
            }
            
            console.log('📊 Reconnaissance complete:', results);
            return results;
        })();
        """
        
        result = await self.execute_js(reconnaissance_js)
        if result.get("success"):
            self.results["phases"]["reconnaissance"] = result.get("value", {})
            await self.send_status(f"✅ Mapped {len(self.results['phases']['reconnaissance'].get('elements', {}).get('buttons', []))} buttons, {len(self.results['phases']['reconnaissance'].get('elements', {}).get('inputs', []))} inputs", "success")
        else:
            await self.send_status("❌ Reconnaissance failed", "error")
            
        return result.get("success", False)
    
    async def phase_2_hypothesis_generation(self):
        """Phase 2: Generate and score send button candidates"""
        await self.send_status("🎯 Phase 2: Send Button Hypothesis Generation", "info", "target")
        
        hypothesis_js = """
        (function generateHypotheses() {
            console.log('🎯 HYPOTHESIS GENERATION PHASE');
            
            const buttons = Array.from(document.querySelectorAll('button'));
            const mainInput = document.querySelector('div[contenteditable="true"]');
            const inputRect = mainInput ? mainInput.getBoundingClientRect() : null;
            
            const candidates = buttons.map((btn, index) => {
                const rect = btn.getBoundingClientRect();
                const hasIcon = btn.querySelector('svg') !== null;
                const text = btn.textContent?.trim().toLowerCase() || '';
                const ariaLabel = (btn.getAttribute('aria-label') || '').toLowerCase();
                const title = (btn.getAttribute('title') || '').toLowerCase();
                
                // Scoring algorithm
                let score = 0;
                let reasons = [];
                
                // Icon presence (strong indicator)
                if (hasIcon) {
                    score += 3;
                    reasons.push('has_icon');
                }
                
                // Text/label analysis
                if (text.includes('send') || ariaLabel.includes('send') || title.includes('send')) {
                    score += 5;
                    reasons.push('send_keyword');
                }
                
                // Button state
                if (!btn.disabled) {
                    score += 2;
                    reasons.push('enabled');
                }
                
                // Visibility
                if (rect.width > 0 && rect.height > 0) {
                    score += 1;
                    reasons.push('visible');
                }
                
                // Size analysis (send buttons are usually small)
                if (rect.width < 100 && rect.height < 100 && rect.width > 20 && rect.height > 20) {
                    score += 2;
                    reasons.push('appropriate_size');
                }
                
                // Position analysis
                if (inputRect) {
                    const horizontalDist = Math.abs(rect.left - inputRect.right);
                    const verticalDist = Math.abs(rect.top - inputRect.top);
                    
                    // Near input horizontally
                    if (horizontalDist < 100) {
                        score += 3;
                        reasons.push('near_input_horizontal');
                    }
                    
                    // Aligned with input vertically
                    if (verticalDist < 50) {
                        score += 2;
                        reasons.push('aligned_with_input');
                    }
                    
                    // In bottom area of screen
                    if (rect.bottom > window.innerHeight * 0.6) {
                        score += 1;
                        reasons.push('bottom_area');
                    }
                }
                
                // Container analysis
                const inInputContainer = mainInput ? 
                    (mainInput.closest('div')?.contains(btn) || 
                     mainInput.closest('div')?.closest('div')?.contains(btn)) : false;
                
                if (inInputContainer) {
                    score += 4;
                    reasons.push('in_input_container');
                }
                
                // Generate multiple selector strategies
                const selectors = [];
                
                if (ariaLabel) {
                    selectors.push({
                        type: 'aria-label',
                        selector: `button[aria-label="${btn.getAttribute('aria-label')}"]`,
                        reliability: 'high'
                    });
                }
                
                if (btn.id) {
                    selectors.push({
                        type: 'id',
                        selector: `#${btn.id}`,
                        reliability: 'high'
                    });
                }
                
                const classes = btn.className.split(' ').filter(c => c.length > 2);
                if (classes.length > 0) {
                    selectors.push({
                        type: 'class',
                        selector: `button.${classes[0]}`,
                        reliability: 'medium'
                    });
                    
                    if (classes.length > 1) {
                        selectors.push({
                            type: 'multiple-class',
                            selector: `button.${classes[0]}.${classes[1]}`,
                            reliability: 'medium'
                        });
                    }
                }
                
                // Position-based selector as fallback
                if (inInputContainer) {
                    const container = mainInput.closest('div')?.closest('div');
                    if (container) {
                        const containerClass = container.className.split(' ')[0];
                        if (containerClass) {
                            selectors.push({
                                type: 'container-based',
                                selector: `.${containerClass} button:has(svg)`,
                                reliability: 'low'
                            });
                        }
                    }
                }
                
                return {
                    index,
                    button: btn,
                    score,
                    reasons,
                    selectors,
                    metadata: {
                        text,
                        ariaLabel: btn.getAttribute('aria-label'),
                        hasIcon,
                        disabled: btn.disabled,
                        className: btn.className,
                        position: {
                            x: Math.round(rect.left),
                            y: Math.round(rect.top),
                            width: Math.round(rect.width),
                            height: Math.round(rect.height)
                        }
                    }
                };
            }).filter(candidate => candidate.score > 0)
              .sort((a, b) => b.score - a.score);
            
            console.log('🎯 Generated candidates:', candidates);
            
            // Store candidates globally for testing phase
            window.sendButtonCandidates = candidates;
            
            return {
                totalButtons: buttons.length,
                candidates: candidates.slice(0, 10), // Top 10 candidates
                topCandidate: candidates[0] || null
            };
        })();
        """
        
        result = await self.execute_js(hypothesis_js)
        if result.get("success"):
            self.results["phases"]["hypothesis"] = result.get("value", {})
            candidates = self.results["phases"]["hypothesis"].get("candidates", [])
            await self.send_status(f"🎯 Generated {len(candidates)} send button candidates", "success")
        else:
            await self.send_status("❌ Hypothesis generation failed", "error")
            
        return result.get("success", False)
    
    async def phase_3_safe_testing(self):
        """Phase 3: Non-invasive testing of button candidates"""
        await self.send_status("🧪 Phase 3: Safe Button Analysis", "info", "microscope")
        
        safe_testing_js = """
        (function safeTesting() {
            console.log('🧪 SAFE TESTING PHASE');
            
            const candidates = window.sendButtonCandidates || [];
            const results = [];
            
            candidates.slice(0, 5).forEach((candidate, i) => {
                const btn = candidate.button;
                const testResult = {
                    candidateIndex: i,
                    originalScore: candidate.score,
                    tests: {}
                };
                
                try {
                    // Test 1: Hover behavior
                    const originalStyle = btn.style.cssText;
                    btn.dispatchEvent(new Event('mouseenter', { bubbles: true }));
                    
                    // Give it a moment to react
                    setTimeout(() => {
                        const hoverStyle = btn.style.cssText;
                        testResult.tests.hover = {
                            styleChanged: hoverStyle !== originalStyle,
                            newStyle: hoverStyle
                        };
                        
                        // Reset
                        btn.dispatchEvent(new Event('mouseleave', { bubbles: true }));
                    }, 100);
                    
                    // Test 2: Focus behavior
                    btn.focus();
                    testResult.tests.focus = {
                        canFocus: document.activeElement === btn,
                        focusVisible: btn.matches(':focus-visible')
                    };
                    btn.blur();
                    
                    // Test 3: Check for event listeners
                    const events = getEventListeners ? getEventListeners(btn) : {};
                    testResult.tests.eventListeners = {
                        hasClickListener: 'click' in events,
                        hasSubmitListener: 'submit' in events,
                        eventTypes: Object.keys(events)
                    };
                    
                    // Test 4: Analyze button context
                    const form = btn.closest('form');
                    const inputContainer = btn.closest('div[contenteditable="true"]')?.parentElement;
                    
                    testResult.tests.context = {
                        inForm: !!form,
                        nearInput: !!inputContainer,
                        formType: form?.getAttribute('method') || null
                    };
                    
                } catch (error) {
                    testResult.tests.error = error.message;
                }
                
                results.push(testResult);
            });
            
            console.log('🧪 Safe testing complete:', results);
            return {
                candidatesTested: results.length,
                testResults: results
            };
        })();
        """
        
        result = await self.execute_js(safe_testing_js)
        if result.get("success"):
            self.results["phases"]["safe_testing"] = result.get("value", {})
            await self.send_status("✅ Safe testing completed", "success")
        else:
            await self.send_status("❌ Safe testing failed", "error")
            
        return result.get("success", False)
    
    async def phase_4_controlled_testing(self):
        """Phase 4: Systematic button testing with DOM observation"""
        await self.send_status("⚡ Phase 4: Controlled Button Testing", "warning", "lightning")
        
        controlled_testing_js = """
        (function controlledTesting() {
            console.log('⚡ CONTROLLED TESTING PHASE');
            
            const candidates = window.sendButtonCandidates || [];
            const testResults = [];
            let currentTest = 0;
            
            // Ensure DOM observer is ready
            if (!window.claudeObserver) {
                return { error: 'DOM observer not available' };
            }
            
            function runSingleTest(candidate, testIndex) {
                return new Promise((resolve) => {
                    console.log(`Testing candidate ${testIndex}:`, candidate.metadata);
                    
                    const testId = `automated_test_${testIndex}_${Date.now()}`;
                    const btn = candidate.button;
                    
                    // Prepare test environment
                    const testPrompt = `Test ${testIndex}: Automated button test at ${new Date().toISOString()}`;
                    
                    // Inject test prompt
                    const injectionSuccess = window.claudeObserver.injectPrompt(testPrompt);
                    if (!injectionSuccess) {
                        resolve({
                            candidateIndex: testIndex,
                            success: false,
                            error: 'Failed to inject test prompt'
                        });
                        return;
                    }
                    
                    // Record initial state
                    const initialInteractionCount = window.claudeObserver.getInteractions().length;
                    const startTime = Date.now();
                    
                    // Click the button
                    try {
                        btn.click();
                        console.log(`Clicked button ${testIndex}`);
                        
                        // Monitor for response (timeout after 5 seconds for automated testing)
                        let checkCount = 0;
                        const maxChecks = 50; // 5 seconds
                        
                        const monitor = setInterval(() => {
                            checkCount++;
                            const currentInteractionCount = window.claudeObserver.getInteractions().length;
                            const hasNewInteraction = currentInteractionCount > initialInteractionCount;
                            
                            if (hasNewInteraction || checkCount >= maxChecks) {
                                clearInterval(monitor);
                                
                                const result = {
                                    candidateIndex: testIndex,
                                    success: hasNewInteraction,
                                    testDuration: Date.now() - startTime,
                                    interactionDetected: hasNewInteraction,
                                    buttonClicked: true
                                };
                                
                                if (hasNewInteraction) {
                                    const latestInteraction = window.claudeObserver.getInteractions()[currentInteractionCount - 1];
                                    result.interaction = {
                                        id: latestInteraction.id,
                                        duration: latestInteraction.duration,
                                        prompt: latestInteraction.prompt,
                                        responseLength: latestInteraction.response?.length || 0,
                                        eventCount: latestInteraction.events.length
                                    };
                                    console.log(`✅ Button ${testIndex} triggered successful interaction!`);
                                } else {
                                    console.log(`❌ Button ${testIndex} did not trigger interaction`);
                                }
                                
                                resolve(result);
                            }
                        }, 100);
                        
                    } catch (error) {
                        resolve({
                            candidateIndex: testIndex,
                            success: false,
                            error: error.message,
                            buttonClicked: false
                        });
                    }
                });
            }
            
            // Test candidates sequentially to avoid interference
            async function runAllTests() {
                const results = [];
                
                for (let i = 0; i < Math.min(candidates.length, 3); i++) {
                    const result = await runSingleTest(candidates[i], i);
                    results.push(result);
                    
                    // Wait between tests to let interface settle
                    await new Promise(resolve => setTimeout(resolve, 2000));
                }
                
                return results;
            }
            
            // Store the test function globally so we can await it
            window.runAutomatedTests = runAllTests;
            
            return { message: 'Test function prepared', candidateCount: candidates.length };
        })();
        """
        
        # First prepare the testing environment
        setup_result = await self.execute_js(controlled_testing_js)
        
        if setup_result.get("success"):
            await self.send_status("🔄 Running automated button tests...", "warning")
            
            # Now execute the actual tests
            execute_tests_js = """
            (async function executeTests() {
                if (window.runAutomatedTests) {
                    return await window.runAutomatedTests();
                } else {
                    return { error: 'Test function not available' };
                }
            })();
            """
            
            # Give it more time for testing
            await asyncio.sleep(2)
            test_result = await self.execute_js(execute_tests_js)
            
            if test_result.get("success"):
                self.results["phases"]["controlled_testing"] = test_result.get("value", {})
                await self.send_status("✅ Controlled testing completed", "success")
            else:
                await self.send_status("❌ Test execution failed", "error")
        else:
            await self.send_status("❌ Test setup failed", "error")
            
        return setup_result.get("success", False)
    
    async def phase_5_workflow_validation(self):
        """Phase 5: Validate complete workflow with identified send button"""
        await self.send_status("🎉 Phase 5: Workflow Validation", "success", "trophy")
        
        validation_js = """
        (function workflowValidation() {
            console.log('🎉 WORKFLOW VALIDATION PHASE');
            
            // Analyze test results to identify the best send button
            const testResults = window.claudeObserver ? window.claudeObserver.getInteractions() : [];
            const candidates = window.sendButtonCandidates || [];
            
            // Find the successful button from our tests
            let bestButton = null;
            let bestSelector = null;
            
            // Look for the most recent successful interaction
            if (testResults.length > 0) {
                const recentInteraction = testResults[testResults.length - 1];
                console.log('Most recent interaction:', recentInteraction);
                
                // Find which candidate likely succeeded
                candidates.forEach((candidate, i) => {
                    if (recentInteraction.prompt && recentInteraction.prompt.includes(`Test ${i}:`)) {
                        bestButton = candidate;
                        bestSelector = candidate.selectors[0]; // Use best selector
                        console.log(`✅ Identified working send button: candidate ${i}`);
                    }
                });
            }
            
            const finalResults = {
                investigationComplete: true,
                bestButton: bestButton ? {
                    selector: bestSelector?.selector,
                    selectorType: bestSelector?.type,
                    score: bestButton.score,
                    reasons: bestButton.reasons,
                    metadata: bestButton.metadata
                } : null,
                totalInteractions: testResults.length,
                procedureGenerated: !!bestButton,
                recommendedUsage: bestButton ? {
                    inputSelector: 'div[contenteditable="true"]',
                    submitSelector: bestSelector?.selector,
                    workflow: [
                        'Inject prompt using inputSelector',
                        'Submit using submitSelector', 
                        'Monitor DOM observer for completion',
                        'Extract response from latest interaction'
                    ]
                } : null
            };
            
            console.log('🎉 Investigation complete:', finalResults);
            return finalResults;
        })();
        """
        
        result = await self.execute_js(validation_js)
        if result.get("success"):
            self.results["phases"]["validation"] = result.get("value", {})
            final_results = self.results["phases"]["validation"]
            
            if final_results.get("bestButton"):
                selector = final_results["bestButton"]["selector"]
                await self.send_status(f"🎉 SUCCESS! Send button: {selector}", "success", "trophy")
            else:
                await self.send_status("⚠️ No definitive send button identified", "warning")
        else:
            await self.send_status("❌ Validation failed", "error")
            
        return result.get("success", False)
    
    async def save_results(self):
        """Save complete investigation results"""
        self.results["completion_time"] = datetime.now().isoformat()
        self.results["duration_seconds"] = time.time() - int(self.session_id.split("_")[1])
        
        filename = f"claude_investigation_{self.session_id}.json"
        
        try:
            from stdioserver_claude import smart_write_file
            write_result = smart_write_file(
                file_path=filename,
                content=json.dumps(self.results, indent=2, default=str)
            )
            
            if write_result.get("success"):
                await self.send_status(f"📁 Results saved to {filename}", "success", "floppy_disk")
            else:
                await self.send_status("❌ Failed to save results", "error")
                
        except Exception as e:
            await self.send_status(f"❌ Save error: {str(e)}", "error")
    
    async def run_complete_investigation(self):
        """Run all investigation phases"""
        await self.send_status("🚀 Starting Complete Automated Investigation", "info", "rocket")
        
        phases = [
            ("reconnaissance", self.phase_1_reconnaissance),
            ("hypothesis", self.phase_2_hypothesis_generation), 
            ("safe_testing", self.phase_3_safe_testing),
            ("controlled_testing", self.phase_4_controlled_testing),
            ("validation", self.phase_5_workflow_validation)
        ]
        
        for phase_name, phase_func in phases:
            await self.send_status(f"▶️ Starting {phase_name.replace('_', ' ').title()}", "info")
            
            try:
                success = await phase_func()
                if not success:
                    await self.send_status(f"❌ {phase_name} failed, continuing anyway", "warning")
                    
                # Brief pause between phases
                await asyncio.sleep(1)
                
            except Exception as e:
                await self.send_status(f"💥 {phase_name} crashed: {str(e)}", "error")
                
        await self.save_results()
        await self.send_status("🎉 Investigation Complete! Check results file.", "success", "celebration")
        
        return self.results

# Main execution
async def main():
    investigator = ClaudeInterfaceInvestigator()
    results = await investigator.run_complete_investigation()
    return results

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
