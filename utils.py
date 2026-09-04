# utils.py
# MSEB Style Professional Bill PDF Generator

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib import colors
import io
import datetime
import os
import qrcode


def generate_bill_pdf_bytes(bill: dict) -> bytes:

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 15 * mm

    # ================= HEADER =================
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width/2, height - 30, "Maharashtra State Electricity Distribution Co. Ltd.")

    c.setFont("Helvetica", 9)
    c.drawCentredString(width/2, height - 45, "(A Government of Maharashtra Undertaking)")
    c.drawCentredString(width/2, height - 58, "Electricity Bill")

    c.line(margin, height - 65, width - margin, height - 65)

    # ================= CONSUMER DETAILS =================
    box_y = height - 80
    c.rect(margin, box_y - 90, width - 2*margin, 90)

    c.setFont("Helvetica", 9)

    c.drawString(margin + 10, box_y - 20, f"Consumer Name: {bill.get('customer_name')}")
    c.drawString(margin + 10, box_y - 35, f"Consumer No: {bill.get('bill_no')}")
    c.drawString(margin + 10, box_y - 50, f"Customer Type: {bill.get('customer_type')}")

    c.drawString(width/2, box_y - 20, f"Bill Date: {bill.get('created_at')}")
    c.drawString(width/2, box_y - 35, f"Units Consumed: {bill.get('units')} kWh")
    c.drawString(width/2, box_y - 50, f"Status: {bill.get('status')}")

    # ================= BILL DETAILS =================
    table_y = box_y - 120

    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, table_y, "Bill Details")

    table_y -= 20

    c.setFont("Helvetica", 10)

    rows = [
        ("Energy Charges", bill.get("energy_charge", 0.0)),
        ("Fixed Charges", bill.get("fixed_charge", 0.0)),
        ("Electricity Duty (GST)", bill.get("gst", 0.0)),
    ]

    for label, value in rows:
        c.drawString(margin + 10, table_y, label)
        c.drawRightString(width - margin - 10, table_y, f"₹ {value:,.2f}")
        table_y -= 18

    # TOTAL BOX
    table_y -= 10
    c.setFillColor(colors.lightgrey)
    c.rect(margin, table_y - 5, width - 2*margin, 22, fill=1, stroke=0)

    c.setFillColor(colors.black)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin + 10, table_y, "Total Amount Payable")
    c.drawRightString(width - margin - 10, table_y, f"₹ {bill.get('total', 0.0):,.2f}")

    # ================= DUE DATE =================
    due_date = datetime.datetime.now() + datetime.timedelta(days=15)

    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(colors.red)
    c.drawString(margin, table_y - 40, f"Due Date: {due_date.strftime('%d-%m-%Y')}")
    c.setFillColor(colors.black)

    # ================= QR CODE =================
    try:
        qr_data = f"Bill No: {bill.get('bill_no')} | Amount: {bill.get('total')}"
        qr = qrcode.make(qr_data)
        qr_path = "temp_qr.png"
        qr.save(qr_path)

        c.drawImage(qr_path, margin, table_y - 140, width=80, height=80)

        os.remove(qr_path)
    except:
        pass

    # ================= SIGNATURE =================
    sig_x = width - margin - 140

    if os.path.exists("signature.png"):
        c.drawImage("signature.png", sig_x, table_y - 120, width=100, height=40, mask='auto')

    c.setFont("Helvetica-Bold", 9)
    c.drawString(sig_x, table_y - 130, "Authorized Signatory")

    c.setFont("Helvetica", 8)
    c.drawString(sig_x, table_y - 145, "MSEDCL")

    # ================= FOOTER =================
    c.setFont("Helvetica-Oblique", 8)
    footer = f"Generated on {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')} | MSEDCL"
    c.drawCentredString(width/2, 15 * mm, footer)

    # ================= PAID STAMP =================
    if str(bill.get("status")).lower() == "paid":
        c.saveState()
        c.setFont("Helvetica-Bold", 80)
        c.setFillColorRGB(0.9, 0.9, 0.9)
        c.translate(width/2, height/2)
        c.rotate(30)
        c.drawCentredString(0, 0, "PAID")
        c.restoreState()

    c.showPage()
    c.save()

    buffer.seek(0)
    pdf = buffer.getvalue()
    buffer.close()

    return pdf