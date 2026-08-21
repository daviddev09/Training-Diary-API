from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily  # type: ignore
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.schemes.training import DiaryRead

pdfmetrics.registerFont(TTFont("Calibri", "app/fonts/calibri.ttf"))  # type: ignore
pdfmetrics.registerFont(TTFont("Calibri-Bold", "app/fonts/calibrib.ttf"))  # type: ignore
pdfmetrics.registerFont(TTFont("Calibri-Italic", "app/fonts/calibrii.ttf"))  # type: ignore

registerFontFamily(
    family="Calibri", normal="Calibri", bold="Calibri-Bold", italic="Calibri-Italic"
)

# Styles
style_title = ParagraphStyle(
    "CoverTitle",
    fontName="Calibri-Bold",
    fontSize=42,
    leading=38,
    alignment=1,
    textColor=colors.black,
)

style_day_header = ParagraphStyle(
    "DayHeader",
    fontName="Calibri-Bold",
    fontSize=32,
    leading=22,
    alignment=1,
    textColor=colors.black,
)

style_cell_header = ParagraphStyle(
    "CellHeader",
    fontName="Calibri-Bold",
    fontSize=12,
    leading=13,
    alignment=1,
    textColor=colors.white,
)

style_cell_circuit = ParagraphStyle(
    "CellCircuit",
    fontName="Calibri-Bold",
    fontSize=10,
    leading=12,
    alignment=1,
    textColor=colors.white,
)

style_cell_content = ParagraphStyle(
    "CellContent",
    fontName="Calibri",
    fontSize=8,
    leading=10,
    alignment=1,
    textColor=colors.white,
)

color_dark_yellow = colors.HexColor("#f4a900")
color_soft_blue = colors.HexColor("#93C5FD")
color_soft_red = colors.HexColor("#FCA5A5")
color_ash = colors.HexColor("#B2BEB5")


def create_diary_pdf_util(
    user_uuid: str, diary: DiaryRead, exercises: dict[int, str] | None
) -> str:
    page_width = A4[0] - 72
    pdf_filename = f"diary_pdfs/{user_uuid}_{diary.id}_diary.pdf"
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36,
    )

    elements: list[Any] = []

    # 1st page
    elements.append(Spacer(1, 220))
    elements.append(Paragraph(diary.diary_name, style_title))
    elements.append(PageBreak())

    # Other pages
    for day in diary.training_days:
        raw_date = str(day.date).split(" ")[0]
        y, m, d = raw_date.split("-")
        formatted_date = f"{y}.{m}.{d}"

        elements.append(Paragraph(formatted_date, style_day_header))
        elements.append(Spacer(1, 15))

        circuits = day.circuits
        circuits_count = len(circuits)

        if circuits_count == 0:
            table_data = [
                [Paragraph(f"<b>Дата: {formatted_date}</b>", style_cell_header)]
            ]
            t_style = [
                ("BACKGROUND", (0, 0), (0, 0), color_dark_yellow),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
                ("BOX", (0, 0), (-1, -1), 1, colors.black),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
            table = Table(table_data, colWidths=[page_width])
            table.setStyle(TableStyle(t_style))
            elements.append(table)
            elements.append(PageBreak())
            continue

        col_width = page_width / circuits_count
        col_widths = [col_width] * circuits_count

        column_items: list[Any] = []
        max_items = 0

        for circuit in circuits:
            c_items: list[Any] = []
            for exercise in circuit.exercises:
                if exercises is not None:
                    exercise_name = exercises.get(exercise.exercise_id)
                else:
                    exercise_name = f"Упражнение {exercise.exercise_id}"

                if exercise.reps:
                    ex_text = f"{exercise_name} x {exercise.reps}"
                elif exercise.duration_seconds:
                    ex_text = f"{exercise_name} {exercise.duration_seconds} секунд"
                else:
                    ex_text = f"{exercise_name}"

                c_items.append({"type": "exercise", "text": ex_text})

                if exercise.rest_seconds:
                    c_items.append(
                        {"type": "rest", "text": f"Отдых: {exercise.rest_seconds}s"}
                    )

            column_items.append(c_items)
            max_items = max(max_items, len(c_items))

        table_data: list[Any] = []

        row_0 = [Paragraph(f"<b>Дата: {formatted_date}</b>", style_cell_header)] + [
            ""
        ] * (circuits_count - 1)
        table_data.append(row_0)

        row1 = [
            Paragraph(f"Круг {c.numberation}", style_cell_circuit) for c in circuits
        ]
        table_data.append(row1)

        for row_idx in range(max_items):
            current_row: list[Any] = []
            for col_idx in range(circuits_count):
                items = column_items[col_idx]
                if row_idx < len(items):
                    item = items[row_idx]
                    p = Paragraph(item["text"], style_cell_content)
                    current_row.append(p)
                else:
                    current_row.append("")
            table_data.append(current_row)

        t_style: list[Any] = [
            ("SPAN", (0, 0), (circuits_count - 1, 0)),
            ("BACKGROUND", (0, 0), (circuits_count - 1, 0), color_dark_yellow),
            ("BACKGROUND", (0, 1), (circuits_count - 1, 1), color_soft_blue),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("BOX", (0, 0), (-1, -1), 1, colors.black),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]

        for col_idx in range(circuits_count):
            items = column_items[col_idx]
            for row_idx in range(len(items)):
                actual_row = 2 + row_idx

                current_item_type = items[row_idx]["type"]
                cell_bg_color = (
                    color_ash if current_item_type == "rest" else color_soft_red
                )

                t_style.append(
                    (
                        "BACKGROUND",
                        (col_idx, actual_row),
                        (col_idx, actual_row),
                        cell_bg_color,
                    )
                )

        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle(t_style))

        elements.append(table)

        elements.append(PageBreak())

    if elements and isinstance(elements[-1], PageBreak):
        elements.pop()

    doc.build(elements)
    return pdf_filename
