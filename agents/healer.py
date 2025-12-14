import logging
import random

logger = logging.getLogger(__name__)

class DisasterRecoveryAgent:
    """
    Intelligent agent that handles workflow failures by prescribing 
    alternative paths or revised inputs.
    """
    
    def heal(self, error: str, state: dict) -> dict:
        """
        Analyzes the error and returns a patch to the state + a routing decision.
        """
        logger.warning(f"⚠️ DISASTER RECOVERY: Analyzing failure -> {error}")
        
        mode = state.get('mode')
        patch = {"error": None} # Generic clear error
        
        # Scenario 1: Navigation Failure (e.g. timeout, blocker)
        if mode == 'techcrunch' and ("Timeout" in error or "Navigation" in error or "element" in error):
            logger.info("🚑 DECISION: TechCrunch blocked. Rerouting to general AI Research mode.")
            patch['mode'] = 'research'
            patch['topic'] = "Latest Artificial Intelligence and TechCrunch News"
            patch['decision'] = "reroute_research"
            return patch

        # Scenario 2: Research Failure (e.g. API limit)
        if mode == 'research' and ("429" in error or "quota" in error):
             logger.info("🚑 DECISION: Research API limit. Using internal knowledge generation.")
             # We skip research and go straight to generation with a prompt override
             patch['research_context'] = "The user requested research, but external tools failed. Please write a general think-piece about: " + str(state.get('topic'))
             patch['decision'] = "reroute_generation"
             return patch

        # Scenario 3: YouTube Failure
        if mode == 'youtube':
            logger.info("🚑 DECISION: Video playback failed. Trying alternative search query.")
            # Simple heuristic: simplify the query
            original = state.get('topic', '')
            patch['topic'] = original + " official video" # Try slightly different query
            patch['decision'] = "retry"
            return patch
            
        # Default: Abort if no smart fix
        logger.error("☠️ FATAL: No cure found for this error.")
        return None
