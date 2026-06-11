"""
Brahmakaal Localization Engine
Advanced multi-language support for Indian languages with astronomical terminology
"""

import os
import json
import logging
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from pathlib import Path

from .translation_manager import TranslationManager


class SupportedLanguage(str, Enum):
    """Supported languages for localization."""
    ENGLISH = "en"
    HINDI = "hi"
    SANSKRIT = "sa"
    TAMIL = "ta"
    BENGALI = "bn"
    GUJARATI = "gu"
    MARATHI = "mr"
    TELUGU = "te"
    KANNADA = "kn"
    MALAYALAM = "ml"
    PUNJABI = "pa"
    ODIA = "or"


class LocalizationEngine:
    """
    Advanced localization engine for Indian languages.
    Handles astronomical and astrological terminology translation.
    """
    
    def __init__(self):
        self.translation_manager = TranslationManager()
        self.supported_languages = list(SupportedLanguage)
        self.default_language = SupportedLanguage.ENGLISH
        self.logger = logging.getLogger(__name__)
        
        # Initialize translation data
        self._load_translations()
    
    def _load_translations(self):
        """Load all translation files."""
        try:
            self.translation_manager.load_all_translations()
            self.logger.info(f"✅ Loaded translations for {len(self.supported_languages)} languages")
        except Exception as e:
            self.logger.error(f"❌ Failed to load translations: {e}")
    
    def get_supported_languages(self) -> List[str]:
        """Get list of supported language codes."""
        return [lang.value for lang in self.supported_languages]
    
    def is_language_supported(self, language_code: str) -> bool:
        """Check if a language is supported."""
        return language_code in self.get_supported_languages()
    
    def translate_term(self, term: str, language: str, category: str = "general") -> str:
        """
        Translate a single term to the specified language.
        
        Args:
            term: Term to translate
            language: Target language code
            category: Translation category (nakshatra, tithi, rashi, etc.)
        
        Returns:
            Translated term or original if translation not found
        """
        if not self.is_language_supported(language):
            return term
        
        return self.translation_manager.get_translation(
            term, language, category, fallback=term
        )
    
    def translate_object(self, data: Dict[str, Any], language: str, 
                        translation_map: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Translate an entire object with specified field mappings.
        
        Args:
            data: Data object to translate
            language: Target language code
            translation_map: Map of field names to translation categories
        
        Returns:
            Object with both original and translated fields
        """
        if not self.is_language_supported(language) or language == SupportedLanguage.ENGLISH:
            return data
        
        translated_data = data.copy()
        default_map = {
            "nakshatra_name": "nakshatra",
            "tithi_name": "tithi", 
            "rashi": "rashi",
            "yoga_name": "yoga",
            "karana_name": "karana",
            "month_name": "months",
            "weekday": "weekdays",
            "season": "seasons",
            "ritu": "ritu",
            "ayana": "ayana"
        }
        
        field_map = translation_map or default_map
        
        for field, category in field_map.items():
            if field in data and data[field]:
                original_value = data[field]
                translated_value = self.translate_term(original_value, language, category)
                
                # Add both original and translated fields
                translated_data[f"{field}_native"] = translated_value
                if translated_value != original_value:
                    translated_data[f"{field}_transliteration"] = self._transliterate(original_value, language)
        
        return translated_data
    
    def _transliterate(self, text: str, target_language: str) -> str:
        """
        Provide transliteration for better pronunciation.
        This is a simplified version - in production, use proper transliteration libraries.
        """
        # For now, return the original text
        # In production, implement proper transliteration using libraries like:
        # - indictrans for Indian language transliteration
        # - python-transliterate
        return text
    
    def localize_panchang_response(self, panchang_data: Dict[str, Any], language: str) -> Dict[str, Any]:
        """
        Localize a complete panchang response.
        
        Args:
            panchang_data: Panchang calculation result
            language: Target language code
        
        Returns:
            Localized panchang data
        """
        if not self.is_language_supported(language):
            language = self.default_language.value
        
        localized_data = panchang_data.copy()
        
        # Add language metadata
        localized_data["localization"] = {
            "language": language,
            "language_name": self.get_language_name(language),
            "script": self.get_language_script(language),
            "supported_languages": self.get_supported_languages()
        }
        
        # Translate main fields
        translation_map = {
            "tithi_name": "tithi",
            "nakshatra": "nakshatra", 
            "nakshatra_lord": "planets",
            "yoga_name": "yoga",
            "karana_name": "karana",
            "rashi_of_moon": "rashi",
            "rashi_of_sun": "rashi",
            "season": "seasons"
        }
        
        localized_data = self.translate_object(localized_data, language, translation_map)
        
        # Handle nested objects
        if "graha_positions" in localized_data:
            for planet, position_data in localized_data["graha_positions"].items():
                if "rashi" in position_data:
                    position_data["rashi_native"] = self.translate_term(
                        position_data["rashi"], language, "rashi"
                    )
                if "nakshatra" in position_data:
                    position_data["nakshatra_native"] = self.translate_term(
                        position_data["nakshatra"], language, "nakshatra"
                    )
        
        # Handle ritu_ayana data
        if "ritu_ayana" in localized_data:
            ritu_data = localized_data["ritu_ayana"]
            for field in ["drik_ritu", "vedic_ritu"]:
                if field in ritu_data:
                    ritu_data[f"{field}_native"] = self.translate_term(
                        ritu_data[field], language, "ritu"
                    )
        
        # Handle nakshatra detailed data
        if "nakshatra_detailed" in localized_data:
            nakshatra_data = localized_data["nakshatra_detailed"]
            if "current_nakshatra" in nakshatra_data:
                nakshatra_data["current_nakshatra_native"] = self.translate_term(
                    nakshatra_data["current_nakshatra"], language, "nakshatra"
                )
        
        return localized_data
    
    def get_language_name(self, language_code: str) -> str:
        """Get the native name of a language."""
        language_names = {
            "en": "English",
            "hi": "हिन्दी",
            "sa": "संस्कृत",
            "ta": "தமிழ்",
            "bn": "বাংলা", 
            "gu": "ગુજરાતી",
            "mr": "मराठी",
            "te": "తెలుగు",
            "kn": "ಕನ್ನಡ",
            "ml": "മലയാളം",
            "pa": "ਪੰਜਾਬੀ",
            "or": "ଓଡ଼ିଆ"
        }
        return language_names.get(language_code, language_code)
    
    def get_language_script(self, language_code: str) -> str:
        """Get the script used by a language."""
        language_scripts = {
            "en": "Latin",
            "hi": "Devanagari",
            "sa": "Devanagari", 
            "ta": "Tamil",
            "bn": "Bengali",
            "gu": "Gujarati",
            "mr": "Devanagari",
            "te": "Telugu",
            "kn": "Kannada",
            "ml": "Malayalam",
            "pa": "Gurmukhi",
            "or": "Odia"
        }
        return language_scripts.get(language_code, "Unknown")
    
    def get_localized_response_template(self, language: str) -> Dict[str, Any]:
        """Get a response template with localized field descriptions."""
        template = {
            "success": True,
            "language": language,
            "data": {},
            "localization_info": {
                "language_name": self.get_language_name(language),
                "script": self.get_language_script(language),
                "fields_info": {
                    "_native": "Native language translation",
                    "_transliteration": "Romanized pronunciation guide"
                }
            }
        }
        return template


# Global localization engine instance
_localization_engine = None


def get_localization_engine() -> LocalizationEngine:
    """Get the global localization engine instance."""
    global _localization_engine
    if _localization_engine is None:
        _localization_engine = LocalizationEngine()
    return _localization_engine 