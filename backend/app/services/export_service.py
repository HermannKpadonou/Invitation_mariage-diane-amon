import io
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def export_guests_excel(guests) -> io.BytesIO:
    """Exporte la liste des invités au format Excel."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Invités"

    # En-têtes
    headers = [
        "Nom", "Prénom", "Téléphone", "Statut", 
        "Accompagnateurs", "Régime", "Transport", "Date d'inscription"
    ]
    ws.append(headers)

    # Données
    for guest in guests:
        date_str = guest.created_at.strftime("%Y-%m-%d %H:%M:%S") if guest.created_at else ""
        row = [
            guest.last_name,
            guest.first_name,
            guest.phone or "",
            guest.status,
            guest.companions_count,
            guest.dietary_options or "",
            "Oui" if guest.transport_needs else "Non",
            date_str
        ]
        ws.append(row)

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)
    return output

def export_guests_pdf(guests) -> io.BytesIO:
    """Exporte la liste des invités au format PDF."""
    output = io.BytesIO()
    
    # Utilisation du mode paysage pour avoir plus de place
    doc = SimpleDocTemplate(output, pagesize=landscape(letter))
    elements = []
    
    styles = getSampleStyleSheet()
    title = Paragraph("Liste des Invités - Mariage Adodo & Amon", styles['Title'])
    elements.append(title)
    
    # Données du tableau
    data = [[
        "Nom", "Prénom", "Téléphone", "Statut", 
        "Accompagnateurs", "Régime", "Transport"
    ]]
    
    for guest in guests:
        data.append([
            guest.last_name,
            guest.first_name,
            guest.phone or "",
            guest.status,
            str(guest.companions_count),
            guest.dietary_options or "",
            "Oui" if guest.transport_needs else "Non"
        ])
        
    table = Table(data)
    
    # Style du tableau
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    table.setStyle(style)
    
    elements.append(table)
    doc.build(elements)
    
    output.seek(0)
    return output
