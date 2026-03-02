"""
Multi-Label NLP model engine for CCPA violation detection
Winner Tier: Direct section prediction without keyword mapping
"""
import os
import logging
from typing import List, Dict, Tuple
import torch

logger = logging.getLogger(__name__)

# CCPA Section mapping (must match training order)
SECTION_LABELS = [
    "Section 1798.100",  # Notice
    "Section 1798.105",  # Deletion
    "Section 1798.106",  # Correction
    "Section 1798.110",  # Disclosure of collection
    "Section 1798.115",  # Disclosure of sale/sharing
    "Section 1798.120",  # Opt-out
    "Section 1798.121",  # Sensitive data
    "Section 1798.125",  # Non-discrimination
    "Section 1798.130",  # Response time
    "Section 1798.135",  # Do Not Sell link
]


class ModelEngine:
    """
    Multi-label model-based detection for CCPA violations
    Directly predicts which sections are violated (no keyword mapping)
    """
    
    def __init__(self):
        """Initialize multi-label model"""
        self.model = None
        self.tokenizer = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.is_multilabel = False
        
        try:
            self._load_model()
        except Exception as e:
            logger.warning(f"Model loading failed: {e}. Using rule-based only.")
    
    def _load_model(self):
        """
        Load multi-label model (preferred) or fall back to binary model
        """
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            
            # Try enhanced model first, then multi-label, then binary, then base
            # Priority: enhanced (6600 examples) > multilabel (3600) > binary (66) > base
            if os.path.exists("./ccpa_model_multilabel_enhanced"):
                model_name = "./ccpa_model_multilabel_enhanced"
                self.is_multilabel = True
                logger.info("Loading ENHANCED MULTI-LABEL model (6600+ examples - best accuracy)")
            elif os.path.exists("./ccpa_model_multilabel"):
                model_name = "./ccpa_model_multilabel"
                self.is_multilabel = True
                logger.info("Loading MULTI-LABEL model (3600 examples - winner tier)")
            elif os.path.exists("./ccpa_model"):
                model_name = "./ccpa_model"
                self.is_multilabel = False
                logger.info("Loading binary model (66 examples - fallback)")
            else:
                model_name = "distilbert-base-uncased"
                self.is_multilabel = False
                logger.info("Loading base model (no fine-tuning - fallback)")
            
            # Get HF token if needed
            hf_token = os.getenv("HF_TOKEN")
            
            self.tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                token=hf_token if hf_token else None
            )
            
            num_labels = 10 if self.is_multilabel else 2
            self.model = AutoModelForSequenceClassification.from_pretrained(
                model_name,
                num_labels=num_labels,
                token=hf_token if hf_token else None
            )
            
            self.model.to(self.device)
            self.model.eval()
            
            logger.info(f"Model loaded on {self.device} (multi-label: {self.is_multilabel})")
            
        except ImportError:
            logger.warning("transformers not installed. Using rule-based only.")
        except Exception as e:
            logger.error(f"Model loading error: {e}")
            raise
    
    def detect(self, prompt: str) -> Tuple[List[str], Dict[str, float]]:
        """
        Detect violations using multi-label model
        
        Args:
            prompt: Business practice description
            
        Returns:
            Tuple of (violations list, confidence dict)
        """
        if self.model is None or self.tokenizer is None:
            return [], {}
        
        try:
            if self.is_multilabel:
                # Use multi-label prediction (direct section detection)
                return self._multilabel_detection(prompt)
            else:
                # Fall back to binary + keyword mapping
                return self._binary_detection(prompt)
            
        except Exception as e:
            logger.error(f"Model detection error: {e}")
            return [], {}
    
    def _multilabel_detection(self, prompt: str) -> Tuple[List[str], Dict[str, float]]:
        """
        Multi-label detection: Direct section prediction
        Winner tier approach - no keyword mapping needed
        """
        violations = []
        confidences = {}
        
        try:
            # FILTER: Skip model if sentence contains positive compliance indicators
            positive_indicators = [
                # Compliance actions
                'allows users', 'allow users', 'respects', 'honors', 'complies', 'provides',
                'verified', 'permanently erased', 'anonymized', 'does not sell', 'do not sell',
                'easy to', 'can easily', 'promptly', 'immediately', 'within',
                
                # Positive deletion/correction
                'users can delete', 'users can correct', 'users can access', 'users can opt out',
                'able to delete', 'able to correct', 'able to access', 'able to opt out',
                'right to delete', 'right to correct', 'right to access', 'right to opt out',
                
                # Positive response/timing
                'respond within', 'reply within', 'process within', 'complete within',
                'within 45 days', 'within 10 days', 'within 30 days', 'timely response',
                
                # Positive disclosure/transparency
                'clearly disclose', 'fully disclose', 'transparently', 'openly',
                'inform users', 'notify users', 'tell users', 'explain to users',
                'privacy policy states', 'privacy policy explains', 'as disclosed',
                
                # Positive opt-out
                'can opt out', 'may opt out', 'option to opt out', 'choice to opt out',
                'opt-out available', 'opt-out option', 'opt-out mechanism',
                
                # Positive data handling
                'secure', 'protected', 'encrypted', 'safeguarded',
                'in accordance with', 'compliant with', 'follows', 'adheres to',
                
                # Positive user control
                'user control', 'user choice', 'user consent', 'with consent',
                'with permission', 'with authorization', 'after consent',
                
                # Positive service quality
                'all users receive', 'same service', 'equal service', 'no discrimination',
                'treat all users', 'same price', 'same quality',
                
                # Positive link/access
                'prominent link', 'clear link', 'visible link', 'accessible',
                'homepage link', 'easy to find',
                
                # Positive internal use
                'internal use only', 'internal analytics', 'internal purposes',
                'not shared', 'not sold', 'not disclosed to third parties',
                
                # Positive verification
                'after verification', 'verified request', 'confirmed request',
                'authenticated', 'validated',
                
                # General positive compliance
                'in compliance', 'meets requirements', 'satisfies', 'fulfills',
                'according to law', 'as required', 'proper', 'appropriate'
            ]
            
            prompt_lower = prompt.lower()
            has_positive = any(indicator in prompt_lower for indicator in positive_indicators)
            
            if has_positive:
                logger.info("Positive compliance indicators detected - skipping model prediction")
                return [], {}
            
            # Tokenize input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get model predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probs = torch.sigmoid(logits[0])  # Sigmoid for multi-label
                
                # Check each section independently
                for i, prob in enumerate(probs):
                    section = SECTION_LABELS[i]
                    confidence = prob.item()
                    confidences[section] = confidence
                    
                    # Threshold: 0.75 (higher threshold to reduce false positives)
                    if confidence > 0.75:
                        violations.append(section)
                        logger.info(f"Detected {section} with confidence {confidence:.3f}")
            
        except Exception as e:
            logger.error(f"Multi-label detection error: {e}")
        
        return violations, confidences
    
    def _binary_detection(self, prompt: str) -> Tuple[List[str], Dict[str, float]]:
        """
        Binary detection with keyword mapping (fallback)
        """
        violations = []
        confidences = {}
        
        try:
            # Tokenize input
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Get model predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probs = torch.softmax(logits, dim=1)
                
                # Get confidence for "harmful" class
                harmful_confidence = probs[0][1].item()
                confidences['overall'] = harmful_confidence
                
                # If model detects potential violation
                if harmful_confidence > 0.6:
                    # Use keyword mapping to determine sections
                    violations.extend(self._map_to_sections(prompt, harmful_confidence))
            
        except Exception as e:
            logger.error(f"Binary detection error: {e}")
        
        return violations, confidences
    
    def _map_to_sections(self, prompt: str, confidence: float) -> List[str]:
        """
        Map binary predictions to sections using keywords (fallback only)
        """
        sections = []
        prompt_lower = prompt.lower()
        
        # Enhanced concept mapping
        concept_map = {
            'Section 1798.100': ['collect', 'gather', 'obtain', 'acquire', 'notice', 'inform', 'disclose', 'tell'],
            'Section 1798.105': ['delete', 'remove', 'erase', 'purge', 'deletion', 'forever', 'permanent'],
            'Section 1798.106': ['correct', 'fix', 'update', 'amend', 'accurate', 'inaccurate'],
            'Section 1798.110': ['disclose', 'access', 'see', 'view', 'know', 'find out'],
            'Section 1798.115': ['sell', 'sale', 'share', 'sharing', 'third party', 'monetize'],
            'Section 1798.120': ['opt out', 'opt-out', 'stop', 'unsubscribe'],
            'Section 1798.121': ['minor', 'child', 'children', 'under 16', 'sensitive', 'geolocation', 'biometric'],
            'Section 1798.125': ['discriminate', 'penalty', 'charge', 'price', 'service', 'deny', 'penalize'],
            'Section 1798.130': ['respond', 'reply', 'answer', 'request', 'delay', 'late', 'months', 'weeks'],
            'Section 1798.135': ['do not sell', 'link', 'button', 'homepage', 'website'],
        }
        
        # Check which concepts are present
        for section, keywords in concept_map.items():
            if any(kw in prompt_lower for kw in keywords):
                # Check for negative context
                negative_indicators = [
                    'no', 'not', 'never', 'refuse', 'deny', 'ignore', 
                    'reject', 'without', 'fail', 'won\'t', 'cannot', 'don\'t'
                ]
                if any(neg in prompt_lower for neg in negative_indicators):
                    sections.append(section)
        
        return sections
