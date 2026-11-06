import phonenumbers
from phonenumbers import NumberParseException

def validate_phone(phone: str) -> tuple[bool, str]:
    """
    Valide et formate un numéro de téléphone en utilisant la bibliothèque phonenumbers.
    
    Args:
        phone (str): Le numéro de téléphone à valider.
        
    Returns:
        tuple[bool, str]: Un tuple contenant un booléen indiquant la validité 
                          et le numéro formaté (ou un message d'erreur).
    """
    if not phone:
        return False, "Le numéro de téléphone est vide."
        
    try:
        # On tente de parser en spécifiant par défaut la région de Côte d'Ivoire (CI) pour l'exemple
        parsed_number = phonenumbers.parse(phone, "CI")
        
        if phonenumbers.is_valid_number(parsed_number):
            # Formater en format international (ex: +225...)
            formatted = phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
            return True, formatted
        else:
            return False, "Le numéro de téléphone n'est pas valide."
            
    except NumberParseException:
        # En cas d'erreur de parsing (ex: format non reconnu)
        return False, "Le format du numéro de téléphone est incorrect."
