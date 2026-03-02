"""
LLM-based CCPA violation detection using smaller language models
Uses models under 8B parameters for context understanding
"""
import os
import logging
from typing import List, Tuple
import json
import re

logger = logging.getLogger(__name__)


class LLMEngine:
    """
    LLM-based detection for context understanding
    Uses smaller models (< 8B params) for compliance
    """
    
    def __init__(self):
        """Initialize LLM with optional model loading"""
        self.model = None
        self.tokenizer = None
        self.use_llm = os.getenv("USE_LLM", "false").lower() == "true"
        self.use_openai = os.getenv("OPENAI_API_KEY") is not None
        
        if self.use_openai:
            logger.info("Using OpenAI API for LLM detection")
            self.use_llm = True
        elif self.use_llm:
            try:
                self._load_model()
            except Exception as e:
                logger.warning(f"LLM loading failed: {e}. Using heuristics only.")
                self.use_llm = False
    
    def _load_model(self):
        """
        Load smaller LLM for context understanding
        Using Phi-2 (2.7B params) or similar small model
        """
        try:
            from transformers import AutoTokenizer, AutoModelForCausalLM
            import torch
            
            # Use Phi-2 (2.7B params) - well under 8B limit
            model_name = "microsoft/phi-2"
            
            logger.info(f"Loading LLM: {model_name}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
            self.model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                device_map="auto" if torch.cuda.is_available() else None,
                trust_remote_code=True
            )
            
            if not torch.cuda.is_available():
                self.model = self.model.to("cpu")
            
            logger.info(f"LLM loaded successfully")
            
        except ImportError:
            logger.warning("transformers not installed for LLM. Using heuristics only.")
            raise
        except Exception as e:
            logger.error(f"LLM loading error: {e}")
            raise
    
    def detect(self, prompt: str) -> Tuple[List[str], float]:
        """
        Detect violations using LLM context understanding
        
        Args:
            prompt: Business practice description
            
        Returns:
            Tuple of (violations list, confidence)
        """
        if not self.use_llm or self.model is None:
            return [], 0.0
        
        try:
            violations = self._llm_detection(prompt)
            confidence = 0.85 if violations else 0.0
            return violations, confidence
            
        except Exception as e:
            logger.error(f"LLM detection error: {e}")
            return [], 0.0
    
    def _llm_detection(self, prompt: str) -> List[str]:
        """
        Use LLM to understand context and detect violations
        """
        # Use OpenAI if available (faster)
        if self.use_openai:
            return self._openai_detection(prompt)
        
        # Otherwise use local Phi-2 model
        return self._phi2_detection(prompt)
    
    def _openai_detection(self, prompt: str) -> List[str]:
        """Use OpenAI API for fast LLM detection"""
        try:
            import openai
            openai.api_key = os.getenv("OPENAI_API_KEY")
            
            system_prompt = """You are a CCPA compliance expert. Analyze business practices and identify violations.

CCPA Sections:
- Section 1798.100: Must inform consumers before collecting data
- Section 1798.105: Must honor deletion requests
- Section 1798.106: Must allow correction of inaccurate data
- Section 1798.110: Must disclose what data is collected
- Section 1798.115: Must disclose if data is sold/shared
- Section 1798.120: Must allow opt-out of data sales
- Section 1798.121: Must limit use of sensitive data
- Section 1798.125: Cannot discriminate for exercising rights
- Section 1798.130: Must respond to requests within 45 days
- Section 1798.135: Must have "Do Not Sell" link

Respond with ONLY violated section numbers (e.g., "Section 1798.105, Section 1798.120") or "None"."""

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Business practice: {prompt}"}
                ],
                temperature=0.1,
                max_tokens=100
            )
            
            answer = response.choices[0].message.content
            violations = self._parse_sections(answer)
            return violations
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return []
    
    def _phi2_detection(self, prompt: str) -> List[str]:
        """Use local Phi-2 model for LLM detection"""
        # Create a focused prompt for the LLM
        llm_prompt = f"""Analyze this business practice for CCPA violations:

Business Practice: "{prompt}"

CCPA Sections:
- Section 1798.100: Must inform consumers before collecting data
- Section 1798.105: Must honor deletion requests
- Section 1798.106: Must allow correction of inaccurate data
- Section 1798.110: Must disclose what data is collected
- Section 1798.115: Must disclose if data is sold/shared
- Section 1798.120: Must allow opt-out of data sales
- Section 1798.121: Must limit use of sensitive data
- Section 1798.125: Cannot discriminate for exercising rights
- Section 1798.130: Must respond to requests within 45 days
- Section 1798.135: Must have "Do Not Sell" link

Question: Does this practice violate CCPA? If yes, which sections?

Answer with ONLY section numbers (e.g., "Section 1798.105, Section 1798.120") or "None" if no violations.

Answer:"""
        
        try:
            # Tokenize
            inputs = self.tokenizer(llm_prompt, return_tensors="pt", truncation=True, max_length=1024)
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
            
            # Generate
            import torch
            with torch.no_grad():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=100,
                    temperature=0.1,  # Low temperature for consistency
                    do_sample=False,
                    pad_token_id=self.tokenizer.eos_token_id
                )
            
            # Decode
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Extract answer (after "Answer:")
            if "Answer:" in response:
                answer = response.split("Answer:")[-1].strip()
            else:
                answer = response[len(llm_prompt):].strip()
            
            # Parse sections from response
            violations = self._parse_sections(answer)
            
            logger.info(f"LLM detected: {violations}")
            return violations
            
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return []
    
    def _parse_sections(self, text: str) -> List[str]:
        """
        Parse section numbers from LLM response
        """
        violations = []
        
        # Look for "Section 1798.XXX" patterns
        pattern = r'Section\s+1798\.\d{3}'
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        for match in matches:
            # Normalize format
            section = match.replace('section', 'Section').replace('  ', ' ')
            if section not in violations:
                violations.append(section)
        
        # Check for "None" or "no violations"
        if not violations:
            if any(word in text.lower() for word in ['none', 'no violation', 'compliant', 'no ccpa']):
                return []
        
        return sorted(violations)
