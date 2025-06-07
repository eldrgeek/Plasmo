# Cursor Fix Instructions - Event Loop Issue

## Problem
The `execute_javascript_fixed()` function fails with "Cannot run the event loop while another loop is running" error because it tries to create a new event loop when one already exists in the MCP server environment.

## Fix Required
In `/Users/MikeWolf/Projects/Plasmo/mcp_server.py`, replace the event loop handling in `execute_javascript_fixed()` function (around lines 590-600).

### Current Code (BROKEN):
```python
# Run the async function
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
try:
    result = loop.run_until_complete(execute())
    return result
finally:
    loop.close()
```

### Replace With (FIXED):
```python
# Run the async function using thread executor to avoid event loop conflicts
def run_async_in_thread(coro):
    def run_in_thread():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            return loop.run_until_complete(coro)
        finally:
            loop.close()
    
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(run_in_thread)
        return future.result()

# Use the thread executor
result = run_async_in_thread(execute())
return result
```

## Apply Same Fix To
Also apply the same pattern to `set_breakpoint_fixed()` function which has identical event loop issue.

## Test After Fix
1. Restart the MCP server
2. Connect to Chrome: `connect_to_chrome()`
3. Test JavaScript execution: `execute_javascript_fixed('console.log("test")', tab_id)`
4. Should work without event loop errors

## Expected Result
- ✅ JavaScript execution works
- ✅ Console monitoring continues working  
- ✅ No event loop conflicts
