from io import BytesIO

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Paragraph


def generate_resume_pdf(user, resume):

    buffer = BytesIO()

    doc = SimpleDocTemplate(buffer)

    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph(f"<b>{user.full_name}</b>", styles["Title"]))

    story.append(Paragraph(user.email, styles["Normal"]))

    story.append(Paragraph(resume.phone or "", styles["Normal"]))

    story.append(Paragraph("<br/><b>Career Objective</b>", styles["Heading2"]))
    story.append(Paragraph(resume.objective or "", styles["BodyText"]))

    story.append(Paragraph("<br/><b>Education</b>", styles["Heading2"]))
    story.append(Paragraph(resume.education or "", styles["BodyText"]))

    story.append(Paragraph("<br/><b>Experience</b>", styles["Heading2"]))
    story.append(Paragraph(resume.experience or "", styles["BodyText"]))

    story.append(Paragraph("<br/><b>Projects</b>", styles["Heading2"]))
    story.append(Paragraph(resume.projects or "", styles["BodyText"]))

    story.append(Paragraph("<br/><b>Skills</b>", styles["Heading2"]))
    story.append(Paragraph(resume.skills or "", styles["BodyText"]))

    story.append(Paragraph("<br/><b>Certifications</b>", styles["Heading2"]))
    story.append(Paragraph(resume.certifications or "", styles["BodyText"]))

    story.append(Paragraph("<br/><b>Achievements</b>", styles["Heading2"]))
    story.append(Paragraph(resume.achievements or "", styles["BodyText"]))

    doc.build(story)

    pdf = buffer.getvalue()

    buffer.close()

    return pdf