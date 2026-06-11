"""
Translation Manager for Brahmakaal Localization
Handles loading and managing translation dictionaries for Indian languages
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class TranslationManager:
    """Manages translation dictionaries for multiple Indian languages."""
    
    def __init__(self):
        self.translations = {}
        self.base_path = Path(__file__).parent / "translations"
        
    def load_all_translations(self):
        """Load all available translation files."""
        if not self.base_path.exists():
            # Create translations with in-memory data if files don't exist
            self._create_default_translations()
            return
            
        for lang_file in self.base_path.glob("*.json"):
            lang_code = lang_file.stem
            try:
                with open(lang_file, 'r', encoding='utf-8') as f:
                    self.translations[lang_code] = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load translations for {lang_code}: {e}")
        
        # Ensure we have at least basic translations
        if not self.translations:
            self._create_default_translations()
    
    def _create_default_translations(self):
        """Create default in-memory translations."""
        self.translations = {
            "hi": self._get_hindi_translations(),
            "sa": self._get_sanskrit_translations(),
            "ta": self._get_tamil_translations(),
            "bn": self._get_bengali_translations(),
            "gu": self._get_gujarati_translations(),
            "mr": self._get_marathi_translations(),
            "te": self._get_telugu_translations(),
            "kn": self._get_kannada_translations(),
            "ml": self._get_malayalam_translations(),
            "pa": self._get_punjabi_translations(),
            "or": self._get_odia_translations()
        }
    
    def get_translation(self, term: str, language: str, category: str = "general", fallback: str = None) -> str:
        """Get translation for a term in specified language and category."""
        if language not in self.translations:
            return fallback or term
            
        lang_data = self.translations[language]
        
        # Try to find in specific category first
        if category in lang_data and term in lang_data[category]:
            return lang_data[category][term]
        
        # Try general category
        if "general" in lang_data and term in lang_data["general"]:
            return lang_data["general"][term]
            
        # Try direct lookup
        if term in lang_data:
            return lang_data[term]
            
        return fallback or term
    
    def _get_hindi_translations(self) -> Dict[str, Any]:
        """Hindi translations."""
        return {
            "nakshatra": {
                "Ashwini": "अश्विनी",
                "Bharani": "भरणी", 
                "Krittika": "कृत्तिका",
                "Rohini": "रोहिणी",
                "Mrigashira": "मृगशिरा",
                "Ardra": "आर्द्रा",
                "Punarvasu": "पुनर्वसु",
                "Pushya": "पुष्य",
                "Ashlesha": "आश्लेषा",
                "Magha": "मघा",
                "Purva Phalguni": "पूर्व फाल्गुनी",
                "Uttara Phalguni": "उत्तर फाल्गुनी",
                "Hasta": "हस्त",
                "Chitra": "चित्रा",
                "Swati": "स्वाति",
                "Vishakha": "विशाखा",
                "Anuradha": "अनुराधा",
                "Jyeshtha": "ज्येष्ठा",
                "Mula": "मूल",
                "Purva Ashadha": "पूर्व आषाढ़ा",
                "Uttara Ashadha": "उत्तर आषाढ़ा",
                "Shravana": "श्रवण",
                "Dhanishtha": "धनिष्ठा",
                "Shatabhisha": "शतभिषा",
                "Purva Bhadrapada": "पूर्व भाद्रपदा",
                "Uttara Bhadrapada": "उत्तर भाद्रपदा",
                "Revati": "रेवती"
            },
            "tithi": {
                "Pratipada": "प्रतिपदा",
                "Dwitiya": "द्वितीया",
                "Tritiya": "तृतीया", 
                "Chaturthi": "चतुर्थी",
                "Panchami": "पंचमी",
                "Shashthi": "षष्ठी",
                "Saptami": "सप्तमी",
                "Ashtami": "अष्टमी",
                "Navami": "नवमी",
                "Dashami": "दशमी",
                "Ekadashi": "एकादशी",
                "Dwadashi": "द्वादशी",
                "Trayodashi": "त्रयोदशी",
                "Chaturdashi": "चतुर्दशी",
                "Purnima": "पूर्णिमा",
                "Amavasya": "अमावस्या",
                "Shukla": "शुक्ल",
                "Krishna": "कृष्ण",
                # Full tithi names
                "Shukla Pratipada": "शुक्ल प्रतिपदा",
                "Shukla Dwitiya": "शुक्ल द्वितीया",
                "Shukla Tritiya": "शुक्ल तृतीया",
                "Shukla Chaturthi": "शुक्ल चतुर्थी",
                "Shukla Panchami": "शुक्ल पंचमी",
                "Shukla Shashthi": "शुक्ल षष्ठी",
                "Shukla Saptami": "शुक्ल सप्तमी",
                "Shukla Ashtami": "शुक्ल अष्टमी",
                "Shukla Navami": "शुक्ल नवमी",
                "Shukla Dashami": "शुक्ल दशमी",
                "Shukla Ekadashi": "शुक्ल एकादशी",
                "Shukla Dwadashi": "शुक्ल द्वादशी",
                "Shukla Trayodashi": "शुक्ल त्रयोदशी",
                "Shukla Chaturdashi": "शुक्ल चतुर्दशी",
                "Krishna Pratipada": "कृष्ण प्रतिपदा",
                "Krishna Dwitiya": "कृष्ण द्वितीया",
                "Krishna Tritiya": "कृष्ण तृतीया",
                "Krishna Chaturthi": "कृष्ण चतुर्थी",
                "Krishna Panchami": "कृष्ण पंचमी",
                "Krishna Shashthi": "कृष्ण षष्ठी",
                "Krishna Saptami": "कृष्ण सप्तमी",
                "Krishna Ashtami": "कृष्ण अष्टमी",
                "Krishna Navami": "कृष्ण नवमी",
                "Krishna Dashami": "कृष्ण दशमी",
                "Krishna Ekadashi": "कृष्ण एकादशी",
                "Krishna Dwadashi": "कृष्ण द्वादशी",
                "Krishna Trayodashi": "कृष्ण त्रयोदशी",
                "Krishna Chaturdashi": "कृष्ण चतुर्दशी"
            },
            "rashi": {
                "Mesha": "मेष",
                "Vrishabha": "वृषभ",
                "Mithuna": "मिथुन",
                "Karka": "कर्क", 
                "Simha": "सिंह",
                "Kanya": "कन्या",
                "Tula": "तुला",
                "Vrishchika": "वृश्चिक",
                "Dhanu": "धनु",
                "Makara": "मकर",
                "Kumbha": "कुम्भ",
                "Meena": "मीन"
            },
            "yoga": {
                "Vishkambha": "विष्कम्भ",
                "Priti": "प्रीति",
                "Ayushman": "आयुष्मान",
                "Saubhagya": "सौभाग्य",
                "Shobhana": "शोभना",
                "Atiganda": "अतिगण्ड",
                "Sukarman": "सुकर्मन्",
                "Dhriti": "धृति",
                "Shula": "शूल",
                "Ganda": "गण्ड",
                "Vriddhi": "वृद्धि",
                "Dhruva": "ध्रुव",
                "Vyaghata": "व्याघात",
                "Harshana": "हर्षण",
                "Vajra": "वज्र",
                "Siddhi": "सिद्धि",
                "Vyatipata": "व्यतीपात",
                "Variyana": "वरीयान्",
                "Parigha": "परिघ",
                "Shiva": "शिव",
                "Siddha": "सिद्ध",
                "Sadhya": "साध्य",
                "Shubha": "शुभ",
                "Shukla": "शुक्ल",
                "Brahma": "ब्रह्म",
                "Indra": "इन्द्र",
                "Vaidhriti": "वैधृति"
            },
            "karana": {
                "Bava": "बव",
                "Balava": "बालव",
                "Kaulava": "कौलव",
                "Taitila": "तैतिल",
                "Gara": "गर",
                "Vanija": "वणिज्",
                "Vishti": "विष्टि",
                "Shakuni": "शकुनि",
                "Chatushpada": "चतुष्पाद",
                "Naga": "नाग",
                "Kinstughna": "किंस्तुघ्न"
            },
            "planets": {
                "Sun": "सूर्य",
                "Moon": "चन्द्र",
                "Mars": "मंगल",
                "Mercury": "बुध",
                "Jupiter": "गुरु",
                "Venus": "शुक्र",
                "Saturn": "शनि",
                "Rahu": "राहु",
                "Ketu": "केतु"
            },
            "ritu": {
                "Vasant": "वसंत",
                "Grishma": "ग्रीष्म", 
                "Varsha": "वर्षा",
                "Sharad": "शरद्",
                "Shishir": "शिशिर",
                "Hemant": "हेमंत"
            },
            "ayana": {
                "Uttarayana": "उत्तरायण",
                "Dakshinayana": "दक्षिणायन"
            },
            "weekdays": {
                "Sunday": "रविवार",
                "Monday": "सोमवार", 
                "Tuesday": "मंगलवार",
                "Wednesday": "बुधवार",
                "Thursday": "गुरुवार",
                "Friday": "शुक्रवार",
                "Saturday": "शनिवार"
            }
        }
    
    def _get_sanskrit_translations(self) -> Dict[str, Any]:
        """Sanskrit translations."""
        return {
            "nakshatra": {
                "Ashwini": "अश्विनी",
                "Bharani": "भरणी",
                "Krittika": "कृत्तिका",
                "Rohini": "रोहिणी",
                "Mrigashira": "मृगशिरा",
                "Ardra": "आर्द्रा",
                "Punarvasu": "पुनर्वसु",
                "Pushya": "पुष्य",
                "Ashlesha": "आश्लेषा",
                "Magha": "मघा",
                "Purva Phalguni": "पूर्वफल्गुनी",
                "Uttara Phalguni": "उत्तरफल्गुनी",
                "Hasta": "हस्त",
                "Chitra": "चित्रा",
                "Swati": "स्वाति",
                "Vishakha": "विशाखा",
                "Anuradha": "अनुराधा",
                "Jyeshtha": "ज्येष्ठा",
                "Mula": "मूल",
                "Purva Ashadha": "पूर्वाषाढा",
                "Uttara Ashadha": "उत्तराषाढा",
                "Shravana": "श्रवण",
                "Dhanishtha": "धनिष्ठा",
                "Shatabhisha": "शतभिषा",
                "Purva Bhadrapada": "पूर्वभाद्रपदा",
                "Uttara Bhadrapada": "उत्तरभाद्रपदा",
                "Revati": "रेवती"
            },
            "planets": {
                "Sun": "सूर्य",
                "Moon": "चन्द्र",
                "Mars": "मङ्गल",
                "Mercury": "बुध",
                "Jupiter": "गुरु",
                "Venus": "शुक्र",
                "Saturn": "शनि",
                "Rahu": "राहु",
                "Ketu": "केतु"
            }
        }
    
    def _get_tamil_translations(self) -> Dict[str, Any]:
        """Tamil translations."""
        return {
            "nakshatra": {
                "Ashwini": "அசுவினி",
                "Bharani": "பரணி",
                "Krittika": "கார்த்திகை",
                "Rohini": "ரோகிணி",
                "Mrigashira": "மிருகசீரிடம்",
                "Ardra": "திருவாதிரை",
                "Punarvasu": "புனர்பூசம்",
                "Pushya": "பூசம்",
                "Ashlesha": "ஆயில்யம்",
                "Magha": "மகம்",
                "Purva Phalguni": "பூரம்",
                "Uttara Phalguni": "உத்திரம்",
                "Hasta": "ஹஸ்தம்",
                "Chitra": "சித்திரை",
                "Swati": "சுவாதி",
                "Vishakha": "விசாகம்",
                "Anuradha": "அனுஷம்",
                "Jyeshtha": "கேட்டை",
                "Mula": "மூலம்",
                "Purva Ashadha": "பூராடம்",
                "Uttara Ashadha": "உத்திராடம்",
                "Shravana": "திருவோணம்",
                "Dhanishtha": "அவிட்டம்",
                "Shatabhisha": "சதயம்",
                "Purva Bhadrapada": "பூரட்டாதி",
                "Uttara Bhadrapada": "உத்திரட்டாதி",
                "Revati": "ரேவதி"
            },
            "rashi": {
                "Mesha": "மேஷம்",
                "Vrishabha": "ரிஷபம்",
                "Mithuna": "மிதுனம்",
                "Karka": "கடகம்",
                "Simha": "சிம்மம்",
                "Kanya": "கன்னி",
                "Tula": "துலாம்",
                "Vrishchika": "விருச்சிகம்",
                "Dhanu": "தனுசு",
                "Makara": "மகரம்",
                "Kumbha": "கும்பம்",
                "Meena": "மீனம்"
            }
        }
    
    def _get_bengali_translations(self) -> Dict[str, Any]:
        """Bengali translations."""
        return {
            "nakshatra": {
                "Ashwini": "অশ্বিনী",
                "Bharani": "ভরণী",
                "Krittika": "কৃত্তিকা",
                "Rohini": "রোহিণী",
                "Mrigashira": "মৃগশিরা",
                "Ardra": "আর্দ্রা",
                "Punarvasu": "পুনর্বসু",
                "Pushya": "পুষ্য",
                "Ashlesha": "আশ্লেষা",
                "Magha": "মঘা",
                "Purva Phalguni": "পূর্ব ফাল্গুনী",
                "Uttara Phalguni": "উত্তর ফাল্গুনী",
                "Hasta": "হস্ত",
                "Chitra": "চিত্রা",
                "Swati": "স্বাতী",
                "Vishakha": "বিশাখা",
                "Anuradha": "অনুরাধা",
                "Jyeshtha": "জ্যেষ্ঠা",
                "Mula": "মূল",
                "Purva Ashadha": "পূর্ব আষাঢ়া",
                "Uttara Ashadha": "উত্তর আষাঢ়া",
                "Shravana": "শ্রবণ",
                "Dhanishtha": "ধনিষ্ঠা",
                "Shatabhisha": "শতভিষা",
                "Purva Bhadrapada": "পূর্ব ভাদ্রপদা",
                "Uttara Bhadrapada": "উত্তর ভাদ্রপদা",
                "Revati": "রেবতী"
            }
        }
    
    def _get_gujarati_translations(self) -> Dict[str, Any]:
        """Gujarati translations."""
        return {
            "nakshatra": {
                "Ashwini": "અશ્વિની",
                "Bharani": "ભરણી",
                "Krittika": "કૃત્તિકા",
                "Rohini": "રોહિણી",
                "Mrigashira": "મૃગશિરા",
                "Ardra": "આર્દ્રા",
                "Punarvasu": "પુનર્વસુ",
                "Pushya": "પુષ્ય",
                "Ashlesha": "આશ્લેષા",
                "Magha": "મઘા",
                "Purva Phalguni": "પૂર્વ ફાલ્ગુની",
                "Uttara Phalguni": "ઉત્તર ફાલ્ગુની",
                "Hasta": "હસ્ત",
                "Chitra": "ચિત્રા",
                "Swati": "સ્વાતિ",
                "Vishakha": "વિશાખા",
                "Anuradha": "અનુરાધા",
                "Jyeshtha": "જ્યેષ્ઠા",
                "Mula": "મૂળ",
                "Purva Ashadha": "પૂર્વ આષાઢા",
                "Uttara Ashadha": "ઉત્તર આષાઢા",
                "Shravana": "શ્રવણ",
                "Dhanishtha": "ધનિષ્ઠા",
                "Shatabhisha": "શતભિષા",
                "Purva Bhadrapada": "પૂર્વ ભાદ્રપદા",
                "Uttara Bhadrapada": "ઉત્તર ભાદ્રપદા",
                "Revati": "રેવતી"
            }
        }
    
    # Simplified versions for other languages
    def _get_marathi_translations(self) -> Dict[str, Any]:
        """Marathi translations (simplified)."""
        return {"nakshatra": {"Pushya": "पुष्य", "Ashwini": "अश्विनी"}}
    
    def _get_telugu_translations(self) -> Dict[str, Any]:
        """Telugu translations (simplified)."""
        return {"nakshatra": {"Pushya": "పుష్య", "Ashwini": "అశ్వినీ"}}
    
    def _get_kannada_translations(self) -> Dict[str, Any]:
        """Kannada translations (simplified)."""
        return {"nakshatra": {"Pushya": "ಪುಷ್ಯ", "Ashwini": "ಅಶ್ವಿನೀ"}}
    
    def _get_malayalam_translations(self) -> Dict[str, Any]:
        """Malayalam translations (simplified)."""
        return {"nakshatra": {"Pushya": "പുഷ്യം", "Ashwini": "അശ്വിനി"}}
    
    def _get_punjabi_translations(self) -> Dict[str, Any]:
        """Punjabi translations (simplified)."""
        return {"nakshatra": {"Pushya": "ਪੁਸ਼ਯ", "Ashwini": "ਅਸ਼ਵਿਨੀ"}}
    
    def _get_odia_translations(self) -> Dict[str, Any]:
        """Odia translations (simplified)."""
        return {"nakshatra": {"Pushya": "ପୁଷ୍ୟ", "Ashwini": "ଅଶ୍ଵିନୀ"}} 