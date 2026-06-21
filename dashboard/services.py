from django.utils import timezone
from django.db.models import Sum, Avg, Count
from django.http import HttpResponse
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

from calculator.models import CarbonRecord

class SustainabilityService:
    @staticmethod
    def calculate_sustainability_score(record):
        """
        Calculate a dynamic 0-100 sustainability score based on the latest record.
        Start at 100 and apply deductions for high emissions in each category:
        - Transport: max 25 deduction (reaches max at 150 km)
        - Electricity: max 25 deduction (reaches max at 120 units)
        - Meat Meals: max 25 deduction (reaches max at 14 meals)
        - Waste: max 25 deduction (reaches max at 20 kg)
        """
        if not record:
            return 100

        score = 100

        # Transport deductions
        trans_deduction = min(25.0, (record.transport_km / 150.0) * 25.0)
        score -= trans_deduction

        # Electricity deductions
        elec_deduction = min(25.0, (record.electricity_units / 120.0) * 25.0)
        score -= elec_deduction

        # Meat meals deductions
        meat_deduction = min(25.0, (record.meat_meals / 14.0) * 25.0)
        score -= meat_deduction

        # Waste deductions
        waste_deduction = min(25.0, (record.waste_kg / 20.0) * 25.0)
        score -= waste_deduction

        return max(10, round(score))

    @staticmethod
    def get_reduction_insights(record):
        """
        Generate detailed breakdown percentages and category statuses.
        """
        if not record:
            return {}

        total = record.total_carbon
        if total == 0:
            return {}

        c_trans = round(record.transport_km * 0.21, 2)
        c_elec = round(record.electricity_units * 0.82, 2)
        c_food = round(record.meat_meals * 3.3, 2)
        c_waste = round(record.waste_kg * 0.57, 2)

        return {
            'breakdown': {
                'Transport': {'emissions': c_trans, 'percentage': round((c_trans / total) * 100, 1)},
                'Electricity': {'emissions': c_elec, 'percentage': round((c_elec / total) * 100, 1)},
                'Food': {'emissions': c_food, 'percentage': round((c_food / total) * 100, 1)},
                'Waste': {'emissions': c_waste, 'percentage': round((c_waste / total) * 100, 1)},
            },
            'highest_sector': max(
                [('Transport', c_trans), ('Electricity', c_elec), ('Food', c_food), ('Waste', c_waste)],
                key=lambda x: x[1]
            )[0]
        }

    @staticmethod
    def get_personalized_recommendations(record):
        """
        Produce a list of highly specific actionable recommendations based on user emissions.
        """
        if not record:
            return ["Record some carbon calculations to receive personalized AI coach tips!"]

        recommendations = []

        # Threshold triggers
        if record.transport_km > 80:
            recommendations.append("🚗 **Transportation**: Your travel emissions are high. Switch to public transit, carpool, or active commuting (walking/cycling) for trips under 5km.")
        else:
            recommendations.append("🚗 **Transportation**: Good transit levels! Keep using green transit options to maintain low transit carbon.")

        if record.electricity_units > 90:
            recommendations.append("⚡ **Electricity**: Energy use is elevated. Install LED light bulbs, unplug idle chargers/appliances, and adjust your thermostat settings to save electricity.")
        else:
            recommendations.append("⚡ **Electricity**: Nice job managing electricity. Consider choosing renewable energy source providers if available.")

        if record.meat_meals > 6:
            recommendations.append("🥩 **Dietary Habits**: High meat intake. Transitioning to a 'Meatless Monday' or eating plant-based substitutes can cut your food footprint in half.")
        else:
            recommendations.append("🥩 **Dietary Habits**: Great control over meat consumption! Plant-rich diets have a significant positive impact on emissions.")

        if record.waste_kg > 15:
            recommendations.append("🗑️ **Waste Management**: High waste output. Start composting kitchen scraps, buy items with minimal packaging, and follow strict recycling guidelines.")
        else:
            recommendations.append("🗑️ **Waste Management**: Excellent recycling and waste reduction habits.")

        return recommendations

    @staticmethod
    def get_benchmark_comparison(record):
        """
        Compare user's footprint against national baseline of 120.0 kg CO2.
        Returns:
            dict: {baseline, difference, percentage, status}
        """
        if not record:
            return {'baseline': 120.0, 'difference': 0.0, 'percentage': 0.0, 'status': 'no_data'}

        baseline = 120.0
        diff = round(baseline - record.total_carbon, 2)
        pct = round((diff / baseline) * 100, 1)
        
        if diff > 0:
            status = 'below' # Eco friendly
        elif diff < 0:
            status = 'above' # High carbon
            pct = abs(pct)
        else:
            status = 'equal'

        return {
            'baseline': baseline,
            'difference': diff,
            'percentage': pct,
            'status': status
        }

    @staticmethod
    def get_tree_offset_equivalent(record):
        """
        Calculate the number of trees needed to offset the user's latest footprint.
        Assumes 1 mature tree absorbs ~20 kg CO2 per year.
        """
        if not record or record.total_carbon <= 0:
            return 0
        latest_carbon = record.total_carbon
        # Round up to next integer
        trees = int(latest_carbon / 20.0)
        if latest_carbon % 20.0 > 0:
            trees += 1
        return trees

    @staticmethod
    def get_monthly_goal_tracking(user):
        """
        Track monthly carbon emissions against a standard goal of 250.0 kg CO2.
        Returns:
            dict: {goal, current_total, progress_pct, status}
        """
        import datetime
        now = timezone.now()
        start_of_month = timezone.make_aware(datetime.datetime(now.year, now.month, 1))
        if now.month == 12:
            start_of_next_month = timezone.make_aware(datetime.datetime(now.year + 1, 1, 1))
        else:
            start_of_next_month = timezone.make_aware(datetime.datetime(now.year, now.month + 1, 1))

        current_month_records = CarbonRecord.objects.filter(
            user=user,
            created_at__gte=start_of_month,
            created_at__lt=start_of_next_month
        )
        current_total = current_month_records.aggregate(sum_carbon=Sum('total_carbon'))['sum_carbon'] or 0.0
        current_total = round(current_total, 2)
        
        goal = 250.0
        progress_pct = round((current_total / goal) * 100, 1) if goal > 0 else 0.0
        
        if current_total <= goal:
            status = 'on_track'
        else:
            status = 'exceeded'

        return {
            'goal': goal,
            'current_total': current_total,
            'progress_pct': progress_pct,
            'status': status
        }

    @staticmethod
    def get_achievement_badges(user, stats, latest):
        """
        Check achievement thresholds dynamically and return unlocked badges.
        """
        badges = []
        
        # 1. Eco Beginner
        if stats.get('total_records', 0) >= 1:
            badges.append({
                'title': 'Eco Beginner',
                'desc': 'Logged your first carbon calculation!',
                'icon': 'fa-seedling',
                'color': 'success'
            })
            
        # 2. Green Hero
        if latest and latest.total_carbon <= 80.0:
            badges.append({
                'title': 'Green Hero',
                'desc': 'Recorded an emission footprint below 80 kg CO₂.',
                'icon': 'fa-shield-halved',
                'color': 'info'
            })
            
        # 3. Planet Protector
        if latest and latest.total_carbon <= 50.0:
            badges.append({
                'title': 'Planet Protector',
                'desc': 'Achieved a footprint below 50 kg CO₂!',
                'icon': 'fa-earth-americas',
                'color': 'primary'
            })
            
        # 4. Carbon Champion
        if stats.get('total_records', 0) >= 3 and stats.get('avg_carbon', 0.0) <= 70.0:
            badges.append({
                'title': 'Carbon Champion',
                'desc': 'Maintained a clean average below 70 kg CO₂.',
                'icon': 'fa-crown',
                'color': 'warning'
            })
            
        return badges

    @staticmethod
    def get_weekly_improvement(records):
        """
        Compare the latest calculation against the previous calculation.
        Returns:
            dict: {previous_total, latest_total, improvement_pct, status}
        """
        # records is a list or sliced QuerySet sorted by -created_at
        if len(records) < 2:
            return {'previous_total': 0.0, 'latest_total': 0.0, 'improvement_pct': 0.0, 'status': 'no_history'}
            
        latest_total = records[0].total_carbon
        previous_total = records[1].total_carbon
        
        if previous_total <= 0:
            return {'previous_total': 0.0, 'latest_total': latest_total, 'improvement_pct': 0.0, 'status': 'no_history'}

        improvement_pct = round(((previous_total - latest_total) / previous_total) * 100, 1)
        
        if improvement_pct >= 0:
            status = 'improved'
        else:
            status = 'increased'
            improvement_pct = abs(improvement_pct)
            
        return {
            'previous_total': previous_total,
            'latest_total': latest_total,
            'improvement_pct': improvement_pct,
            'status': status
        }

    @staticmethod
    def get_personalized_reduction_targets(latest):
        """
        Generate contextual, micro-reduction goals dynamically.
        """
        targets = []
        if not latest:
            return targets

        if latest.transport_km > 50:
            saved = round(15 * 0.21, 2)
            targets.append({
                'title': 'Cut weekly transit by 15 km',
                'saved': f'Save {saved} kg CO₂',
                'desc': 'Walk, cycle, or work remotely one day per week.'
            })
        if latest.electricity_units > 100:
            saved = round(30 * 0.82, 2)
            targets.append({
                'title': 'Reduce electricity by 30 kWh/month',
                'saved': f'Save {saved} kg CO₂',
                'desc': 'Switch to LED lighting and disconnect standby plugs.'
            })
        if latest.meat_meals > 5:
            saved = round(2 * 3.3, 2)
            targets.append({
                'title': 'Adopt 2 vegetarian dinners/week',
                'saved': f'Save {saved} kg CO₂',
                'desc': 'Replace meat with legumes, tofu, or grains.'
            })
        if latest.waste_kg > 10:
            saved = round(4 * 0.57, 2)
            targets.append({
                'title': 'Reduce weekly waste by 4 kg',
                'saved': f'Save {saved} kg CO₂',
                'desc': 'Compost organic scraps and choose unpackaged foods.'
            })
            
        return targets

    @staticmethod
    def get_impact_summary(user, records, stats):
        """
        Aggregate user lifetime impact statistics.
        """
        # CO2 saved = comparison baseline (120) * calculations count - user total
        total_records = stats.get('total_records', 0)
        total_carbon = stats.get('total_carbon', 0.0)
        
        co2_saved = round((total_records * 120.0) - total_carbon, 2)
        co2_saved = max(0.0, co2_saved)
        
        # Reductions: compare first record (oldest) against latest (newest)
        first_record = CarbonRecord.objects.filter(user=user).order_by('created_at', 'id').first()
        latest_record = records[0] if len(records) > 0 else None
        
        if first_record and latest_record and first_record.id != latest_record.id and first_record.total_carbon > 0:
            reduction_pct = round(((first_record.total_carbon - latest_record.total_carbon) / first_record.total_carbon) * 100, 1)
        else:
            reduction_pct = 0.0
            
        return {
            'co2_saved': co2_saved,
            'reduction_pct': reduction_pct,
        }


class PDFService:
    @staticmethod
    def build_sustainability_report(user, records):
        """
        Generate a professional, well-formatted ReportLab PDF report containing user history and progress.
        """
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="EcoTrack_Sustain_Report_{user.username}.pdf"'

        doc = SimpleDocTemplate(
            response,
            pagesize=letter,
            rightMargin=40, leftMargin=40,
            topMargin=40, bottomMargin=40
        )

        styles = getSampleStyleSheet()
        
        # Define clean, professional color palette
        PRIMARY_COLOR = colors.HexColor('#0f766e')  # Teal 700
        SECONDARY_COLOR = colors.HexColor('#1e293b') # Slate 800
        LIGHT_BG = colors.HexColor('#f8fafc')        # Slate 50
        
        # Custom Typography Styles
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=24,
            leading=28,
            textColor=PRIMARY_COLOR,
            spaceAfter=8
        )
        
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=11,
            leading=14,
            textColor=colors.HexColor('#64748b'),
            spaceAfter=25
        )
        
        h2_style = ParagraphStyle(
            'SectionHeader',
            parent=styles['Heading2'],
            fontName='Helvetica-Bold',
            fontSize=14,
            leading=18,
            textColor=SECONDARY_COLOR,
            spaceBefore=15,
            spaceAfter=10
        )

        body_style = ParagraphStyle(
            'ReportBody',
            parent=styles['Normal'],
            fontName='Helvetica',
            fontSize=10,
            leading=14,
            textColor=SECONDARY_COLOR
        )

        table_header_style = ParagraphStyle(
            'TableHeader',
            parent=styles['Normal'],
            fontName='Helvetica-Bold',
            fontSize=10,
            textColor=colors.white
        )

        story = []

        # Title Block (Emojis removed to ensure proper Helvetica font printing compatibility)
        story.append(Paragraph("EcoTrack AI", title_style))
        story.append(Paragraph(f"Official Carbon & Sustainability Report for <b>{user.username}</b> | Generated dynamically", subtitle_style))
        story.append(Spacer(1, 10))

        # Executive Summary Section
        story.append(Paragraph("Executive Summary", h2_style))
        
        # Evaluate QuerySet once to avoid repeated DB calls
        records = list(records)

        if records:
            latest = records[0]
            score = SustainabilityService.calculate_sustainability_score(latest)
            
            # Compute stats directly from the evaluated list to eliminate redundant database query
            count = len(records)
            total = sum(r.total_carbon for r in records)
            avg = total / count if count > 0 else 0.0
            stats = {
                'total': total,
                'avg': avg,
                'count': count
            }
            
            summary_text = (
                f"This report summarizes your personal carbon footprint analytics across {stats['count']} recorded entries. "
                f"Your latest calculated footprint is <b>{latest.total_carbon} kg CO₂</b>, achieving a Sustainability Score of "
                f"<b>{score}/100</b>. To date, you have logged a total of <b>{round(stats['total'] or 0, 2)} kg CO₂</b> emissions "
                f"with an average of <b>{round(stats['avg'] or 0, 2)} kg CO₂</b> per entry."
            )
            story.append(Paragraph(summary_text, body_style))
            story.append(Spacer(1, 15))

            # Breakdown Table
            story.append(Paragraph("Latest Record Details", h2_style))
            
            data = [
                [Paragraph("Emission Source", table_header_style), Paragraph("Quantity / Input Value", table_header_style), Paragraph("Calculated CO₂ Impact", table_header_style)],
                [Paragraph("Transportation", body_style), Paragraph(f"{latest.transport_km} km", body_style), Paragraph(f"{round(latest.transport_km * 0.21, 2)} kg", body_style)],
                [Paragraph("Electricity Usage", body_style), Paragraph(f"{latest.electricity_units} kWh", body_style), Paragraph(f"{round(latest.electricity_units * 0.82, 2)} kg", body_style)],
                [Paragraph("Dietary Meals (Meat)", body_style), Paragraph(f"{latest.meat_meals} meals", body_style), Paragraph(f"{round(latest.meat_meals * 3.3, 2)} kg", body_style)],
                [Paragraph("Waste Output", body_style), Paragraph(f"{latest.waste_kg} kg", body_style), Paragraph(f"{round(latest.waste_kg * 0.57, 2)} kg", body_style)],
                [Paragraph("<b>Total Combined Impact</b>", body_style), Paragraph("", body_style), Paragraph(f"<b>{latest.total_carbon} kg CO₂</b>", body_style)]
            ]
            
            summary_table = Table(data, colWidths=[200, 150, 150])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_COLOR),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                ('TOPPADDING', (0, 0), (-1, 0), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -2), [LIGHT_BG, colors.white]),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e2e8f0')),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, -1), (-1, -1), 10),
                ('BOTTOMPADDING', (0, -1), (-1, -1), 10),
            ]))
            story.append(summary_table)
            story.append(Spacer(1, 20))

            # History Table
            if len(records) > 1:
                story.append(Paragraph("Emissions History (Up to Last 5 Records)", h2_style))
                history_data = [
                    [Paragraph("Date", table_header_style), Paragraph("Transport", table_header_style), Paragraph("Electricity", table_header_style), Paragraph("Meals", table_header_style), Paragraph("Waste", table_header_style), Paragraph("Total CO₂", table_header_style)]
                ]
                
                for r in records[1:6]:
                    history_data.append([
                        Paragraph(r.created_at.strftime('%d %b %Y'), body_style),
                        Paragraph(f"{r.transport_km} km", body_style),
                        Paragraph(f"{r.electricity_units} kWh", body_style),
                        Paragraph(f"{r.meat_meals}", body_style),
                        Paragraph(f"{r.waste_kg} kg", body_style),
                        Paragraph(f"<b>{r.total_carbon} kg</b>", body_style),
                    ])
                
                history_table = Table(history_data, colWidths=[100, 80, 80, 70, 70, 100])
                history_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), SECONDARY_COLOR),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
                    ('TOPPADDING', (0, 0), (-1, 0), 6),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [LIGHT_BG, colors.white]),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                story.append(history_table)
                story.append(Spacer(1, 20))

            # Recommendations
            story.append(Paragraph("Actionable Recommendations", h2_style))
            recs = SustainabilityService.get_personalized_recommendations(latest)
            for rec in recs:
                # Remove markdown syntax bold from recs for report presentation
                clean_rec = rec.replace('**', '')
                story.append(Paragraph(f"• {clean_rec}", body_style))
                story.append(Spacer(1, 4))

        else:
            story.append(Paragraph("No carbon logs recorded yet. Please submit your carbon stats in the calculator to view analytics.", body_style))

        doc.build(story)
        return response
