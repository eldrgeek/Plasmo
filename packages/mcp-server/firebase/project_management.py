"""
Firebase project management tools.

This module contains Firebase automation tools that were factored out from the main
MCP server to reduce complexity and provide specialized Firebase functionality.

These tools can be accessed through the native tools system by registering them
in tools.yaml or by importing them directly when needed.

Note: These functions are NO LONGER MCP tools - they are plain functions
that can be called by the native tools system.
"""

import subprocess
import json
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# ============================================================================
# FIREBASE AUTOMATION FUNCTIONS (No longer MCP tools)
# ============================================================================
def firebase_setup_new_project(
    project_id: str,
    project_name: str,
    billing_account: str = None,
    region: str = "us-central1",
    web_apps: List[Dict[str, Any]] = None,
    auth_providers: List[Dict[str, Any]] = None,
    services: List[str] = None,
    custom_domains: List[str] = None,
    google_credentials: Dict[str, str] = None
) -> Dict[str, Any]:
    """
    🔥 Create a complete new Firebase project with full automation.
    
    This tool orchestrates the complete Firebase project setup process:
    1. Creates GCP project and enables required APIs
    2. Sets up Firebase Console configuration via web automation
    3. Creates web applications with hosting
    4. Configures authentication providers
    5. Initializes Firebase services (Firestore, Storage, Functions)
    6. Sets up custom domains
    
    Args:
        project_id: Unique project identifier (lowercase, hyphens allowed)
        project_name: Human-readable project name
        billing_account: GCP billing account ID (optional, required for some features)
        region: GCP region for resources (default: us-central1)
        web_apps: List of web applications to create
        auth_providers: Authentication providers to enable
        services: Firebase services to initialize (firestore, storage, functions)
        custom_domains: Custom domains to configure
        google_credentials: Google account credentials for console automation
    
    Returns:
        Dict with project creation results, generated configs, and manual steps
    
    Example:
        firebase_setup_new_project(
            project_id="my-startup-2024",
            project_name="My Startup",
            web_apps=[
                {"name": "Main Website", "setupHosting": True, "hostingSite": "main-site"},
                {"name": "Admin Panel", "setupHosting": True, "hostingSite": "admin"}
            ],
            auth_providers=[
                {"type": "email"},
                {"type": "google"},
                {"type": "github", "clientId": "xxx", "clientSecret": "xxx"}
            ],
            services=["firestore", "storage"],
            google_credentials={"email": "user@gmail.com"}
        )
    """
    try:
        import subprocess
        import json
        import os
        from pathlib import Path
        
        result = {
            "success": False,
            "project_id": project_id,
            "web_apps": [],
            "auth_providers": [],
            "services_configured": [],
            "manual_steps": [],
            "errors": []
        }
        
        # Validate inputs
        if not project_id or not project_name:
            result["errors"].append("project_id and project_name are required")
            return result
        
        # Set defaults
        web_apps = web_apps or []
        auth_providers = auth_providers or []
        services = services or ["firestore", "storage"]
        custom_domains = custom_domains or []
        
        # Step 1: Run GCP infrastructure setup
        try:
            script_path = Path("firebase-setup-automation.sh")
            if not script_path.exists():
                result["errors"].append("firebase-setup-automation.sh not found")
                return result
            
            cmd = [
                "bash", str(script_path),
                project_id, project_name
            ]
            if billing_account:
                cmd.append(billing_account)
                cmd.append(region)
            
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if process.returncode != 0:
                result["errors"].append(f"GCP setup failed: {process.stderr}")
                return result
                
            result["gcp_setup"] = "completed"
            
        except subprocess.TimeoutExpired:
            result["errors"].append("GCP setup timed out after 5 minutes")
            return result
        except Exception as e:
            result["errors"].append(f"GCP setup error: {str(e)}")
            return result
        
        # Step 2: Run Firebase Console automation
        if google_credentials and web_apps:
            try:
                # Create Node.js automation config
                automation_config = {
                    "projectId": project_id,
                    "webApps": web_apps,
                    "authProviders": auth_providers,
                    "services": services,
                    "customDomains": custom_domains,
                    **google_credentials
                }
                
                config_path = Path("firebase-automation-config.json")
                with open(config_path, "w") as f:
                    json.dump(automation_config, f, indent=2)
                
                # Run Playwright automation
                node_cmd = ["node", "-e", f"""
                const FirebaseAutomator = require('./firebase-console-automation');
                const config = require('./{config_path}');
                
                async function run() {{
                    const automator = new FirebaseAutomator(config.projectId, {{
                        headless: true,
                        authStatePath: './firebase-auth-state.json'
                    }});
                    
                    try {{
                        await automator.init();
                        
                        // Login if needed
                        if (config.email && config.password) {{
                            await automator.login(config.email, config.password);
                        }}
                        
                        // Create web apps
                        for (const app of config.webApps) {{
                            const configText = await automator.createWebApp(app.name, app);
                            console.log(`APP_CONFIG:${{app.name}}:${{configText}}`);
                        }}
                        
                        // Configure authentication
                        if (config.authProviders.length > 0) {{
                            await automator.enableAuthentication(config.authProviders);
                        }}
                        
                        // Configure services
                        for (const service of config.services) {{
                            switch (service) {{
                                case 'firestore':
                                    await automator.configureFirestore();
                                    break;
                                case 'storage':
                                    await automator.configureStorage();
                                    break;
                                case 'functions':
                                    await automator.configureFunctions();
                                    break;
                            }}
                        }}
                        
                        console.log('AUTOMATION_SUCCESS');
                    }} catch (error) {{
                        console.error('AUTOMATION_ERROR:', error.message);
                    }} finally {{
                        await automator.close();
                    }}
                }}
                
                run();
                """]
                
                automation_process = subprocess.run(
                    node_cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=600  # 10 minutes
                )
                
                # Parse automation results
                output_lines = automation_process.stdout.split('\n')
                for line in output_lines:
                    if line.startswith('APP_CONFIG:'):
                        parts = line.split(':', 2)
                        if len(parts) == 3:
                            app_name, config_text = parts[1], parts[2]
                            result["web_apps"].append({
                                "name": app_name,
                                "config": config_text,
                                "status": "created"
                            })
                    elif line.startswith('AUTOMATION_SUCCESS'):
                        result["console_automation"] = "completed"
                    elif line.startswith('AUTOMATION_ERROR:'):
                        result["errors"].append(f"Console automation: {line[18:]}")
                
                # Cleanup
                if config_path.exists():
                    config_path.unlink()
                    
            except subprocess.TimeoutExpired:
                result["errors"].append("Console automation timed out after 10 minutes")
            except Exception as e:
                result["errors"].append(f"Console automation error: {str(e)}")
        
        # Step 3: Collect manual steps
        manual_steps = [
            "Review generated Firebase configuration files",
            "Test authentication providers in Firebase Console"
        ]
        
        # Add OAuth-specific manual steps
        for provider in auth_providers:
            if provider.get("type") == "github":
                manual_steps.append(
                    f"Add callback URL to GitHub OAuth app: "
                    f"https://{project_id}.firebaseapp.com/__/auth/handler"
                )
            elif provider.get("type") == "facebook":
                manual_steps.append(
                    f"Add callback URL to Facebook app: "
                    f"https://{project_id}.firebaseapp.com/__/auth/handler"
                )
        
        # Add domain verification steps
        for domain in custom_domains:
            manual_steps.append(f"Configure DNS records for domain: {domain}")
        
        result["manual_steps"] = manual_steps
        result["success"] = len(result["errors"]) == 0
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Firebase project setup failed: {str(e)}",
            "project_id": project_id
        }

def firebase_configure_existing_project(
    project_id: str,
    google_credentials: Dict[str, str],
    operations: Dict[str, Any]
) -> Dict[str, Any]:
    """
    🔥 Configure an existing Firebase project with additional apps and services.
    
    This tool extends an existing Firebase project by adding new web applications,
    enabling authentication providers, configuring services, and setting up
    custom domains using web automation.
    
    Args:
        project_id: Existing Firebase project ID
        google_credentials: Google account credentials for console access
        operations: Dictionary of operations to perform:
            - createWebApps: List of web apps to create
            - enableAuthProviders: List of auth providers to enable
            - configureServices: List of services to set up
            - addCustomDomains: List of custom domains to add
    
    Returns:
        Dict with configuration results and manual steps required
    
    Example:
        firebase_configure_existing_project(
            project_id="existing-project",
            google_credentials={"email": "user@gmail.com"},
            operations={
                "createWebApps": [
                    {"name": "New Admin Panel", "setupHosting": True}
                ],
                "enableAuthProviders": [
                    {"type": "github", "clientId": "xxx", "clientSecret": "xxx"}
                ],
                "configureServices": ["storage", "functions"],
                "addCustomDomains": ["api.myapp.com"]
            }
        )
    """
    try:
        import subprocess
        import json
        from pathlib import Path
        
        result = {
            "success": False,
            "project_id": project_id,
            "operations_completed": [],
            "operations_failed": [],
            "manual_steps": [],
            "created_apps": []
        }
        
        # Validate inputs
        if not project_id or not google_credentials:
            result["error"] = "project_id and google_credentials are required"
            return result
        
        # Create automation configuration
        automation_config = {
            "projectId": project_id,
            "operations": operations,
            **google_credentials
        }
        
        config_path = Path("firebase-existing-config.json")
        with open(config_path, "w") as f:
            json.dump(automation_config, f, indent=2)
        
        # Run automation script
        node_cmd = ["node", "-e", f"""
        const FirebaseAutomator = require('./firebase-console-automation');
        const config = require('./{config_path}');
        
        async function run() {{
            const automator = new FirebaseAutomator(config.projectId, {{
                headless: true,
                authStatePath: './firebase-auth-state.json'
            }});
            
            try {{
                await automator.init();
                
                // Login if needed
                if (config.email && config.password) {{
                    await automator.login(config.email, config.password);
                }}
                
                const ops = config.operations;
                
                // Create web apps
                if (ops.createWebApps) {{
                    for (const app of ops.createWebApps) {{
                        try {{
                            const configText = await automator.createWebApp(app.name, app);
                            console.log(`CREATED_APP:${{app.name}}:success`);
                        }} catch (error) {{
                            console.log(`CREATED_APP:${{app.name}}:failed:${{error.message}}`);
                        }}
                    }}
                }}
                
                // Enable auth providers
                if (ops.enableAuthProviders) {{
                    try {{
                        await automator.enableAuthentication(ops.enableAuthProviders);
                        console.log('AUTH_PROVIDERS:success');
                    }} catch (error) {{
                        console.log(`AUTH_PROVIDERS:failed:${{error.message}}`);
                    }}
                }}
                
                // Configure services
                if (ops.configureServices) {{
                    for (const service of ops.configureServices) {{
                        try {{
                            switch (service) {{
                                case 'firestore':
                                    await automator.configureFirestore();
                                    break;
                                case 'storage':
                                    await automator.configureStorage();
                                    break;
                                case 'functions':
                                    await automator.configureFunctions();
                                    break;
                            }}
                            console.log(`SERVICE:${{service}}:success`);
                        }} catch (error) {{
                            console.log(`SERVICE:${{service}}:failed:${{error.message}}`);
                        }}
                    }}
                }}
                
                // Add custom domains
                if (ops.addCustomDomains) {{
                    for (const domain of ops.addCustomDomains) {{
                        try {{
                            await automator.configureHosting(domain);
                            console.log(`DOMAIN:${{domain}}:success`);
                        }} catch (error) {{
                            console.log(`DOMAIN:${{domain}}:failed:${{error.message}}`);
                        }}
                    }}
                }}
                
                console.log('AUTOMATION_COMPLETE');
                
            }} catch (error) {{
                console.error('AUTOMATION_ERROR:', error.message);
            }} finally {{
                await automator.close();
            }}
        }}
        
        run();
        """]
        
        automation_process = subprocess.run(
            node_cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minutes
        )
        
        # Parse results
        output_lines = automation_process.stdout.split('\n')
        for line in output_lines:
            if line.startswith('CREATED_APP:'):
                parts = line.split(':', 3)
                if len(parts) >= 3:
                    app_name, status = parts[1], parts[2]
                    if status == "success":
                        result["operations_completed"].append(f"Created app: {app_name}")
                        result["created_apps"].append(app_name)
                    else:
                        error_msg = parts[3] if len(parts) > 3 else "Unknown error"
                        result["operations_failed"].append(f"Failed to create app {app_name}: {error_msg}")
            
            elif line.startswith('AUTH_PROVIDERS:'):
                status = line.split(':', 1)[1]
                if status == "success":
                    result["operations_completed"].append("Configured authentication providers")
                else:
                    result["operations_failed"].append(f"Auth providers failed: {status}")
            
            elif line.startswith('SERVICE:'):
                parts = line.split(':', 2)
                service, status = parts[1], parts[2]
                if status.startswith("success"):
                    result["operations_completed"].append(f"Configured service: {service}")
                else:
                    error_msg = status.replace("failed:", "")
                    result["operations_failed"].append(f"Service {service} failed: {error_msg}")
            
            elif line.startswith('DOMAIN:'):
                parts = line.split(':', 2)
                domain, status = parts[1], parts[2]
                if status.startswith("success"):
                    result["operations_completed"].append(f"Configured domain: {domain}")
                    result["manual_steps"].append(f"Complete DNS verification for: {domain}")
                else:
                    error_msg = status.replace("failed:", "")
                    result["operations_failed"].append(f"Domain {domain} failed: {error_msg}")
        
        # Cleanup
        if config_path.exists():
            config_path.unlink()
        
        result["success"] = len(result["operations_failed"]) == 0
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Firebase configuration failed: {str(e)}",
            "project_id": project_id
        }

def firebase_project_status(project_id: str) -> Dict[str, Any]:
    """
    🔥 Get the current configuration status of a Firebase project.
    
    This tool queries the Firebase project to determine the current state
    of web applications, authentication providers, services, and domains.
    Uses Firebase CLI and web automation to gather comprehensive status.
    
    Args:
        project_id: Firebase project ID to check
    
    Returns:
        Dict with detailed project status information
    
    Example:
        firebase_project_status("my-project-2024")
    """
    try:
        import subprocess
        import json
        from pathlib import Path
        
        result = {
            "success": False,
            "project_id": project_id,
            "web_apps": [],
            "auth_providers": [],
            "services": {},
            "custom_domains": [],
            "billing_status": "unknown"
        }
        
        # Check if Firebase CLI is available and project exists
        try:
            # Get project info using Firebase CLI
            cli_result = subprocess.run(
                ["firebase", "projects:list", "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if cli_result.returncode == 0:
                projects = json.loads(cli_result.stdout)
                project_found = any(p.get("projectId") == project_id for p in projects)
                
                if not project_found:
                    result["error"] = f"Project {project_id} not found or not accessible"
                    return result
                
                result["project_exists"] = True
            else:
                result["error"] = "Firebase CLI not available or not authenticated"
                return result
                
        except subprocess.TimeoutExpired:
            result["error"] = "Firebase CLI command timed out"
            return result
        except json.JSONDecodeError:
            result["error"] = "Failed to parse Firebase CLI output"
            return result
        
        # Get web apps list
        try:
            apps_result = subprocess.run(
                ["firebase", "apps:list", "--project", project_id, "--json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if apps_result.returncode == 0:
                apps_data = json.loads(apps_result.stdout)
                for app in apps_data:
                    if app.get("platform") == "WEB":
                        result["web_apps"].append({
                            "name": app.get("displayName", "Unknown"),
                            "app_id": app.get("appId"),
                            "status": "active"
                        })
                        
        except Exception as e:
            result["web_apps_error"] = str(e)
        
        # Check Firebase services using GCP CLI
        try:
            services_result = subprocess.run(
                ["gcloud", "services", "list", "--enabled", "--project", project_id, "--format=json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if services_result.returncode == 0:
                services = json.loads(services_result.stdout)
                service_names = [s.get("config", {}).get("name", "") for s in services]
                
                result["services"] = {
                    "firestore": "firestore.googleapis.com" in service_names,
                    "storage": "firebasestorage.googleapis.com" in service_names,
                    "functions": "cloudfunctions.googleapis.com" in service_names,
                    "hosting": "firebasehosting.googleapis.com" in service_names,
                    "auth": "firebase.googleapis.com" in service_names
                }
                
        except Exception as e:
            result["services_error"] = str(e)
        
        # Check billing status
        try:
            billing_result = subprocess.run(
                ["gcloud", "billing", "projects", "describe", project_id, "--format=json"],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if billing_result.returncode == 0:
                billing_data = json.loads(billing_result.stdout)
                result["billing_status"] = "enabled" if billing_data.get("billingEnabled") else "disabled"
                result["billing_account"] = billing_data.get("billingAccountName", "")
            else:
                result["billing_status"] = "unknown"
                
        except Exception as e:
            result["billing_error"] = str(e)
        
        result["success"] = True
        result["last_checked"] = datetime.now().isoformat()
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Firebase project status check failed: {str(e)}",
            "project_id": project_id
        }
