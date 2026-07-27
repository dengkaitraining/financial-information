# ==============================================================================
# 英文自動翻譯為繁體中文工具 (backend/core/scraper/translator.py)
# ==============================================================================

from deep_translator import GoogleTranslator
import logging

class TextTranslator:
    def __init__(self, source_lang='auto', target_lang='zh-TW'):
        self.translator = GoogleTranslator(source=source_lang, target=target_lang)

    def translate(self, text: str) -> str:
        if not text or not text.strip():
            return text
        try:
            # 檢查是否包含英文字母
            if any(c.isalpha() and ord(c) < 128 for c in text):
                translated = self.translator.translate(text)
                return translated if translated else text
            return text
        except Exception as e:
            logging.warning(f"Translation failed for '{text[:20]}...': {e}")
            return text
