#!/usr/bin/env python3
"""
Testing Service
===============
Manages continuous testing with parser-specific test running.
"""

import time
from .service_base import ManagedService


class TestingService(ManagedService):
    """Testing service implementation"""
    
    async def health_check(self) -> bool:
        """Health check for testing service"""
        self.last_health_check = time.time()
        
        # Basic process and port check from parent class
        health_ok = await super().health_check()
        
        if health_ok:
            self.update_metrics({
                "service_type": "testing",
                "auto_test_on_change": True
            })
        
        return health_ok 