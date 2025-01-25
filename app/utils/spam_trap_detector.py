"""Spam trap detection module.

This module provides functionality to:
- Check if an email address is a potential spam trap 
- Load and maintain spam trap patterns
- Monitor detection metrics
"""

import re
import json
import time
from typing import Set, Dict, Optional
from pathlib import Path
from collections import defaultdict
from .logger import logger
from .metrics import record_metric

class SpamTrapDetector:
    def __init__(self, config_path: str = 'config/spam_traps.json'):
        """Initialize the spam trap detector.
        
        Args:
            config_path: Path to spam trap configuration file
        """
        self.config_path = Path(config_path)
        self.patterns: Dict[str, Set[str]] = defaultdict(set)
        self.load_patterns()
        
    def load_patterns(self) -> None:
        """Load spam trap patterns from configuration file.
        
        Loads and compiles regex patterns for spam trap detection by category.
        Patterns are grouped into categories like disposable, role-based, etc.
        """
        if not self.config_path.exists():
            logger.warning(f"Spam trap config not found at {self.config_path}")
            return
            
        try:
            with open(self.config_path) as f:
                config = json.load(f)
                for category, patterns in config.items():
                    self.patterns[category].update(patterns)
            logger.info(f"Loaded spam trap patterns: {len(self.patterns)} categories")
        except Exception as e:
            logger.error(f"Error loading spam trap patterns: {e}")
            
    def is_spam_trap(self, email: str) -> Dict[str, bool]:
        """Check if email matches any spam trap patterns.
        
        Args:
            email: Email address to check
            
        Returns:
            Dict[str, bool]: Results per category showing if email matches any patterns
        """
        email = email.lower()
        results = {}
        
        start_time = time.time()
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                if re.search(pattern, email):
                    results[category] = True
                    record_metric('spam_trap.detected', 1, {'category': category})
                    break
            if category not in results:
                results[category] = False
                
        duration = time.time() - start_time
        record_metric('spam_trap.check_duration', duration)
                
        return results
        
    def add_pattern(self, category: str, pattern: str) -> bool:
        """Add a new spam trap pattern.
        
        Args:
            category: Pattern category
            pattern: Regex pattern to add
            
        Returns:
            bool: True if added successfully
        """
        try:
            # Validate pattern can be compiled
            re.compile(pattern)
            self.patterns[category].add(pattern)
            
            # Update config file
            config = {}
            if self.config_path.exists():
                with open(self.config_path) as f:
                    config = json.load(f)
                    
            if category not in config:
                config[category] = []
            config[category].append(pattern)
            
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
                
            logger.info(f"Added pattern to {category}: {pattern}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add pattern: {e}")
            return False
            
    def remove_pattern(self, category: str, pattern: str) -> bool:
        """Remove a spam trap pattern.
        
        Args:
            category: Pattern category
            pattern: Pattern to remove
            
        Returns:
            bool: True if removed successfully
        """
        try:
            self.patterns[category].discard(pattern)
            
            if self.config_path.exists():
                with open(self.config_path) as f:
                    config = json.load(f)
                
                if category in config and pattern in config[category]:
                    config[category].remove(pattern)
                    
                    with open(self.config_path, 'w') as f:
                        json.dump(config, f, indent=2)
                        
            logger.info(f"Removed pattern from {category}: {pattern}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove pattern: {e}")
            return False