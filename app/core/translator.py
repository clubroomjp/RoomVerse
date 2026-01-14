from deep_translator import GoogleTranslator
from app.core.config import config

class TranslatorService:
    def __init__(self):
        # We will initialize the translator dynamically to support config changes
        pass

    def translate(self, text: str, target_lang: str = "ja") -> str:
        """
        Translates text to the target language.
        Returns original text if translation fails or is disabled.
        """
        if not text:
            return ""
            
        try:
            translator = GoogleTranslator(source='auto', target=target_lang)
            return translator.translate(text)
        except Exception as e:
            print(f"Translation failed: {e}")
            return text

translator = TranslatorService()
