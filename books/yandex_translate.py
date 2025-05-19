import requests
from django.conf import settings

class YandexTranslateClient:
    """Client for Yandex Translate API."""
    
    BASE_URL = 'https://translate.api.cloud.yandex.net/translate/v2/translate'
    
    def __init__(self):
        """Initialize the client with settings from Django settings."""
        self.folder_id = settings.YANDEX_TRANSLATE_FOLDER_ID
        self.api_key = settings.YANDEX_TRANSLATE_API_KEY
        self.target_language = settings.YANDEX_TRANSLATE_TARGET_LANGUAGE
        
        if not self.folder_id or not self.api_key:
            raise ValueError('YANDEX_TRANSLATE_FOLDER_ID and YANDEX_TRANSLATE_API_KEY must be set in environment variables')
    
    def translate(self, text: str, target_language: str = None, source_language: str = None) -> str:
        """
        Translate text using Yandex Translate API.
        
        Args:
            text: Text to translate
            target_language: Target language code (defaults to YANDEX_TRANSLATE_TARGET_LANGUAGE from settings)
            source_language: Source language code (default: 'en')
            
        Returns:
            Translated text
        """
        if target_language is None:
            target_language = self.target_language
            
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Api-Key {self.api_key}'
        }
        
        data = {
            'folderId': self.folder_id,
            'texts': [text],
            'targetLanguageCode': target_language,
            'sourceLanguageCode': source_language
        }
        
        try:
            response = requests.post(self.BASE_URL, headers=headers, json=data)
            response.raise_for_status()
            
            result = response.json()
            if 'translations' in result and result['translations']:
                return result['translations'][0]['text']
            else:
                raise ValueError('No translation found in response')
                
        except requests.exceptions.RequestException as e:
            raise Exception(f'Translation request failed: {str(e)}')
        except (KeyError, IndexError) as e:
            raise Exception(f'Failed to parse translation response: {str(e)}') 