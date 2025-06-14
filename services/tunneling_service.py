#!/usr/bin/env python3
"""
Tunneling Service
=================
Manages tunneling for external access to services.
"""

import time
from .service_base import ManagedService


class TunnelingService(ManagedService):
    """Tunneling service implementation"""
    
    async def health_check(self) -> bool:
        """Health check for tunneling service"""
        self.last_health_check = time.time()
        
        # Basic process check from parent class (no port for tunneling)
        health_ok = await super().health_check()
        
        if health_ok:
            self.update_metrics({
                "service_type": "tunneling",
                "external_access": True
            })
        
        return health_ok 