import logging

logger = logging.getLogger(__name__)

class WhatsAppService:
    """
    Service de gestion des envois de messages WhatsApp.
    Ceci est un placeholder pour la future intégration avec l'API WhatsApp Business.
    """
    
    def __init__(self):
        # Configuration potentielle avec app.config.settings
        self.is_configured = False

    def send_message(self, phone_number: str, message_text: str) -> dict:
        """
        Simule l'envoi d'un message WhatsApp.
        """
        log_msg = f"WhatsApp simulation - To: {phone_number} | Message: {message_text}"
        logger.info(log_msg)
        print(log_msg) # Pour visibilité dans la console pendant le dev
        
        return {
            "status": "success",
            "message": "Message simulé avec succès (WhatsApp non configuré)",
            "details": {
                "phone": phone_number,
                "text_preview": message_text[:20] + "..."
            }
        }
