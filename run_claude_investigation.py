#!/usr/bin/env python3
"""
Simple Automated Claude Interface Investigation
Executable version for immediate testing
"""

import json
import time
from datetime import datetime

def run_investigation():
    """Run the automated investigation using available MCP tools"""
    
    session_id = f"investigation_{int(time.time())}"
    results = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "phases": {}
    }
    
    print("🚀 Starting Automated Claude Interface Investigation")
    
    # Phase 1: Reconnaissance
    print("🔍 Phase 1: Reconnaissance & Element Mapping")
    
    reconnaissance_js = """
    (function reconnaissance() {
        console.log('🔍 AUTOMATED RECONNAISSANCE PHASE');
        
        const results = {
            timestamp: Date.now(),
            page_info: {
                url: window.location.href,
                title: document.title,
                dimensions: { width: window.innerWidth, height: window.innerHeight }
            },
            elements: { buttons: [], inputs: [], spatial_map: {} },
            observer_status: null
        };
        
        // Map all buttons with detailed analysis
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
                    x: Math.round(rect.left), y: Math.round(rect.top),
                    width: Math.round(rect.width), height: Math.round(rect.height)
                },
                className: btn.className,
                id: btn.id || null
            });
        });
        
        // Map inputs
        const inputs = document.querySelectorAll('input, textarea, [contenteditable]');
        Array.from(inputs).forEach((input, i) => {
            const rect = input.getBoundingClientRect();
            results.elements.inputs.push({
                index: i,
                tagName: input.tagName,
                type: input.type || 'none',
                contentEditable: input.contentEditable || 'false',
                position: { x: Math.round(rect.left), y: Math.round(rect.top) },
                className: input.className,
                isMainInput: input.contentEditable === 'true'
            });
        });
        
        // Spatial analysis
        const mainInput = document.querySelector('div[contenteditable="true"]');
        if (mainInput) {
            const inputRect = mainInput.getBoundingClientRect();
            const nearbyButtons = [];
            
            // Find buttons near the input
            Array.from(buttons).forEach((btn, i) => {
                const btnRect = btn.getBoundingClientRect();
                const horizontalDist = Math.abs(btnRect.left - inputRect.right);
                const verticalDist = Math.abs(btnRect.top - inputRect.top);
                
                if (horizontalDist < 200 && verticalDist < 100) {
                    nearbyButtons.push({
                        buttonIndex: i,
                        distance: { horizontal: horizontalDist, vertical: verticalDist }
                    });
                }
            });
            
            results.elements.spatial_map.input_area_buttons = nearbyButtons;
        }
        
        // Check DOM observer
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
        
        return results;
    })();
    """
    
    try:
        from stdioserver_claude import execute_javascript
        recon_result = execute_javascript(code=reconnaissance_js, tab_id="5913F1B9C3DA841BBFF3695C9745BDED")
        
        if recon_result.get("success"):
            results["phases"]["reconnaissance"] = recon_result.get("value", {})
            button_count = len(results["phases"]["reconnaissance"].get("elements", {}).get("buttons", []))
            print(f"✅ Reconnaissance complete: {button_count} buttons mapped")
        else:
            print("❌ Reconnaissance failed")
            return None
            
    except Exception as e:
        print(f"❌ Reconnaissance error: {e}")
        return None
    
    # Phase 2: Generate Send Button Candidates
    print("🎯 Phase 2: Send Button Hypothesis Generation")
    
    hypothesis_js = """
    (function generateHypotheses() {
        const buttons = Array.from(document.querySelectorAll('button'));
        const mainInput = document.querySelector('div[contenteditable="true"]');
        const inputRect = mainInput ? mainInput.getBoundingClientRect() : null;
        
        const candidates = buttons.map((btn, index) => {
            const rect = btn.getBoundingClientRect();
            const hasIcon = btn.querySelector('svg') !== null;
            const text = btn.textContent?.trim().toLowerCase() || '';
            const ariaLabel = (btn.getAttribute('aria-label') || '').toLowerCase();
            
            // Smart scoring algorithm
            let score = 0;
            let reasons = [];
            
            if (hasIcon) { score += 3; reasons.push('has_icon'); }
            if (text.includes('send') || ariaLabel.includes('send')) { score += 5; reasons.push('send_keyword'); }
            if (!btn.disabled) { score += 2; reasons.push('enabled'); }
            if (rect.width > 0 && rect.height > 0) { score += 1; reasons.push('visible'); }
            if (rect.width < 100 && rect.height < 100) { score += 2; reasons.push('appropriate_size'); }
            
            // Position scoring
            if (inputRect) {
                const horizontalDist = Math.abs(rect.left - inputRect.right);
                const verticalDist = Math.abs(rect.top - inputRect.top);
                
                if (horizontalDist < 100) { score += 3; reasons.push('near_input'); }
                if (verticalDist < 50) { score += 2; reasons.push('aligned_with_input'); }
                
                // Container analysis
                if (mainInput.closest('div')?.contains(btn)) { 
                    score += 4; reasons.push('in_input_container'); 
                }
            }
            
            // Generate selectors
            const selectors = [];
            if (ariaLabel && btn.getAttribute('aria-label')) {
                selectors.push(`button[aria-label="${btn.getAttribute('aria-label')}"]`);
            }
            if (btn.id) selectors.push(`#${btn.id}`);
            
            const classes = btn.className.split(' ').filter(c => c.length > 2);
            if (classes.length > 0) {
                selectors.push(`button.${classes[0]}`);
            }
            
            return {
                index, score, reasons, selectors,
                metadata: {
                    text, ariaLabel: btn.getAttribute('aria-label'), hasIcon,
                    disabled: btn.disabled, className: btn.className,
                    position: { x: Math.round(rect.left), y: Math.round(rect.top) }
                }
            };
        }).filter(c => c.score > 0).sort((a, b) => b.score - a.score);
        
        // Store for testing phase
        window.sendButtonCandidates = candidates;
        
        return {
            totalButtons: buttons.length,
            candidates: candidates.slice(0, 5),
            topCandidate: candidates[0] || null
        };
    })();
    """
    
    try:
        hypothesis_result = execute_javascript(code=hypothesis_js, tab_id="5913F1B9C3DA841BBFF3695C9745BDED")
        
        if hypothesis_result.get("success"):
            results["phases"]["hypothesis"] = hypothesis_result.get("value", {})
            candidate_count = len(results["phases"]["hypothesis"].get("candidates", []))
            print(f"🎯 Generated {candidate_count} send button candidates")
        else:
            print("❌ Hypothesis generation failed")
            
    except Exception as e:
        print(f"❌ Hypothesis error: {e}")
    
    # Phase 3: Test the top candidate
    print("⚡ Phase 3: Testing Top Candidate")
    
    testing_js = """
    (function testTopCandidate() {
        const candidates = window.sendButtonCandidates || [];
        if (candidates.length === 0) {
            return { error: 'No candidates available' };
        }
        
        const topCandidate = candidates[0];
        const btn = document.querySelectorAll('button')[topCandidate.index];
        
        if (!btn) {
            return { error: 'Button not found' };
        }
        
        // Test with DOM observer if available
        if (window.claudeObserver) {
            const testPrompt = `Automated test at ${new Date().toISOString()}`;
            const injectionSuccess = window.claudeObserver.injectPrompt(testPrompt);
            
            if (injectionSuccess) {
                const initialCount = window.claudeObserver.getInteractions().length;
                
                // Click the button
                btn.click();
                
                // Quick check for response (simplified for demo)
                setTimeout(() => {
                    const newCount = window.claudeObserver.getInteractions().length;
                    const success = newCount > initialCount;
                    
                    window.testResult = {
                        candidateIndex: 0,
                        buttonClicked: true,
                        interactionDetected: success,
                        selector: topCandidate.selectors[0] || `button.${btn.className.split(' ')[0]}`,
                        metadata: topCandidate.metadata
                    };
                }, 2000);
                
                return { message: 'Test initiated', candidate: topCandidate };
            }
        }
        
        return { 
            error: 'DOM observer not available',
            candidate: topCandidate,
            suggestedSelector: topCandidate.selectors[0]
        };
    })();
    """
    
    try:
        test_result = execute_javascript(code=testing_js, tab_id="5913F1B9C3DA841BBFF3695C9745BDED")
        
        if test_result.get("success"):
            results["phases"]["testing"] = test_result.get("value", {})
            print("⚡ Testing initiated")
            
            # Wait for test to complete
            time.sleep(3)
            
            # Check results
            check_js = "window.testResult || { message: 'Test still running' };"
            check_result = execute_javascript(code=check_js, tab_id="5913F1B9C3DA841BBFF3695C9745BDED")
            
            if check_result.get("success"):
                test_data = check_result.get("value", {})
                results["phases"]["test_results"] = test_data
                
                if test_data.get("interactionDetected"):
                    print(f"🎉 SUCCESS! Send button found: {test_data.get('selector')}")
                else:
                    print("⚠️ Test completed but no interaction detected")
            
        else:
            print("❌ Testing failed")
            
    except Exception as e:
        print(f"❌ Testing error: {e}")
    
    # Save results
    filename = f"claude_investigation_simple_{session_id}.json"
    try:
        from stdioserver_claude import smart_write_file
        write_result = smart_write_file(
            file_path=filename,
            content=json.dumps(results, indent=2, default=str)
        )
        
        if write_result.get("success"):
            print(f"📁 Results saved to {filename}")
        else:
            print("❌ Failed to save results")
            
    except Exception as e:
        print(f"❌ Save error: {e}")
    
    print("🎉 Investigation Complete!")
    return results

if __name__ == "__main__":
    results = run_investigation()
    print("\n📊 FINAL RESULTS:")
    print(json.dumps(results, indent=2, default=str))
