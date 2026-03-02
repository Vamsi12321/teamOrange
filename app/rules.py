"""
Rule-based CCPA violation detection engine
Handles keyword matching, pattern detection, and synonym resolution
"""
import re
from typing import List, Set


class RuleEngine:
    """
    Fast rule-based detection for common CCPA violations
    """
    
    def __init__(self):
        """Initialize rule patterns and keyword mappings"""
        
        # Section 1798.100 - Notice before collecting data
        self.notice_keywords = {
            'no notice', 'without notice', 'without informing', 'without telling',
            'without disclosure', 'secretly collect', 'hidden collection',
            'undisclosed collection', 'collect without', 'gather without',
            'no disclosure', 'fail to notify', 'failed to inform'
        }
        
        # Section 1798.105 - Right to delete
        self.delete_keywords = {
            'refuse to delete', 'deny deletion', 'ignore deletion', 
            'reject deletion', 'not delete', 'won\'t delete', 'cannot delete',
            'refuse deletion request', 'deny delete request', 'ignore delete',
            'deletion denied', 'keep forever', 'never delete'
        }
        
        # Section 1798.106 - Right to correct
        self.correct_keywords = {
            'refuse to correct', 'deny correction', 'ignore correction',
            'reject correction', 'not correct', 'won\'t correct', 'cannot correct',
            'refuse correction request', 'deny correct request', 'no correction',
            'deny request to correct', 'deny requests to correct', 'refuse request to correct',
            'ignore request to correct', 'reject request to correct'
        }
        
        # Section 1798.110 - Right to know collected data
        self.know_collected_keywords = {
            'refuse to disclose', 'deny access', 'not disclose', 'won\'t disclose',
            'hide what data', 'refuse information', 'deny information',
            'not tell what', 'refuse to tell', 'no access to data'
        }
        
        # Section 1798.115 - Right to know sold/shared data
        self.know_sold_keywords = {
            'not disclose sale', 'hide sale', 'secret sale', 'undisclosed sale',
            'not tell about sale', 'refuse to disclose sale', 'no disclosure of sale',
            'hide sharing', 'secret sharing', 'undisclosed sharing'
        }
        
        # Section 1798.120 - Right to opt out of sale
        self.opt_out_keywords = {
            'no opt out', 'no opt-out', 'cannot opt out', 'can\'t opt out',
            'refuse opt out', 'deny opt out', 'ignore opt out',
            'no way to opt out', 'impossible to opt out', 'difficult to opt out'
        }
        
        # Section 1798.121 - Limit use of sensitive info
        self.sensitive_keywords = {
            'sensitive', 'geolocation', 'precise location', 'genetic',
            'biometric', 'health', 'sexual orientation', 'race', 'ethnicity',
            'religion', 'union membership', 'minor', 'child', 'under 16'
        }
        
        # Section 1798.125 - No discrimination after opt-out
        self.discrimination_keywords = {
            'charge more', 'higher price', 'different price', 'discriminate',
            'penalize', 'penalty', 'worse service', 'lower quality',
            'deny service', 'refuse service', 'after opt out', 'after opting out'
        }
        
        # Section 1798.130 - Notice & response requirements
        self.response_keywords = {
            'no response', 'not respond', 'ignore request', 'no reply',
            'fail to respond', 'failed to respond', 'never responded',
            'never respond', 'do not respond', 'don\'t respond',
            'refuse to respond', 'deny request', 'reject request'
        }
        
        # Section 1798.135 - Do Not Sell link requirements
        self.dns_link_keywords = {
            'no link', 'no do not sell', 'no "do not sell"', 'missing link',
            'no opt out link', 'no opt-out link', 'hidden link'
        }
        
        # Sale/share synonyms
        self.sale_synonyms = {
            'sell', 'sale', 'sold', 'selling', 'share', 'shared', 'sharing',
            'disclose', 'disclosed', 'disclosing', 'transfer', 'transferred',
            'provide to third party', 'give to third party'
        }
    
    def detect(self, prompt: str) -> List[str]:
        """
        Detect CCPA violations using rule-based patterns
        STRICT MODE: Only trigger on explicit violations with negative context
        
        Args:
            prompt: Business practice description
            
        Returns:
            List of violated section numbers
        """
        violations: Set[str] = set()
        prompt_lower = prompt.lower()
        
        # STRICT: Only trigger if NEGATIVE context is present
        # Positive/neutral statements should NOT trigger rules
        
        # Check 1798.100 - Notice violations (must have "without" or "no")
        if any(kw in prompt_lower for kw in self.notice_keywords):
            violations.add("Section 1798.100")
        
        # Check 1798.105 - Deletion violations (must have "refuse"/"deny"/"ignore")
        if any(kw in prompt_lower for kw in self.delete_keywords):
            violations.add("Section 1798.105")
        
        # Check 1798.106 - Correction violations (must have "refuse"/"deny"/"ignore")
        if any(kw in prompt_lower for kw in self.correct_keywords):
            violations.add("Section 1798.106")
        
        # Check 1798.110 - Right to know collected data (must have "refuse"/"deny"/"hide")
        if any(kw in prompt_lower for kw in self.know_collected_keywords):
            violations.add("Section 1798.110")
        
        # Check 1798.115 - Right to know sold/shared data (must have "hide"/"secret"/"not disclose")
        if any(kw in prompt_lower for kw in self.know_sold_keywords):
            violations.add("Section 1798.115")
        
        # Check 1798.120 - Opt-out violations (must have "no"/"cannot"/"refuse")
        if any(kw in prompt_lower for kw in self.opt_out_keywords):
            violations.add("Section 1798.120")
        
        # Check 1798.121 - Sensitive data + sale/share (BOTH required)
        has_sensitive = any(kw in prompt_lower for kw in self.sensitive_keywords)
        has_sale = any(syn in prompt_lower for syn in self.sale_synonyms)
        # STRICT: Also check for negative context (without consent, no permission)
        has_negative = any(word in prompt_lower for word in ['without', 'no consent', 'no permission', 'no authorization'])
        if has_sensitive and has_sale and has_negative:
            violations.add("Section 1798.121")
        
        # Check 1798.125 - Discrimination violations (must have "charge more"/"penalize"/"discriminate")
        if any(kw in prompt_lower for kw in self.discrimination_keywords):
            violations.add("Section 1798.125")
        
        # Check 1798.130 - Response violations (must have "no"/"not"/"ignore"/"fail")
        if any(kw in prompt_lower for kw in self.response_keywords):
            violations.add("Section 1798.130")
        
        # Check 1798.135 - Do Not Sell link violations (must have "no"/"missing"/"hidden")
        if any(kw in prompt_lower for kw in self.dns_link_keywords):
            violations.add("Section 1798.135")
        
        # Additional pattern-based checks (STRICT)
        violations.update(self._pattern_checks(prompt_lower))
        
        return sorted(list(violations))
    
    def _pattern_checks(self, prompt_lower: str) -> Set[str]:
        """Additional regex-based pattern matching"""
        violations = set()
        
        # Pattern: "sell data to X without Y"
        if re.search(r'(sell|share|disclose).*(without|no).*(notice|consent|permission)', prompt_lower):
            violations.add("Section 1798.100")
            violations.add("Section 1798.120")
        
        # Pattern: Minor-related violations
        if re.search(r'(minor|child|under 16|kid|teenager)', prompt_lower):
            if any(word in prompt_lower for word in ['sell', 'share', 'disclose']):
                violations.add("Section 1798.120")
                violations.add("Section 1798.121")
        
        # Pattern: Deletion + refuse/deny/ignore (MUST have negative word)
        if re.search(r'(delete|deletion|remove).*(refuse|deny|ignore|reject|won\'t|cannot|not)', prompt_lower):
            violations.add("Section 1798.105")
        
        # Pattern: Keep/retain data DESPITE/EVEN AFTER request (violation)
        if re.search(r'(keep|retain|store).*(despite|even after|even though).*(request|deletion)', prompt_lower):
            violations.add("Section 1798.105")
        
        # Pattern: Price discrimination after opt-out
        if re.search(r'(opt.?out|opted.?out).*(charge|price|cost|fee|pay)', prompt_lower):
            violations.add("Section 1798.125")
        
        return violations
