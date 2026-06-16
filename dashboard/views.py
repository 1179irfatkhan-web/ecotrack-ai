import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from calculator.services import CarbonService
from .services import SustainabilityService

@login_required
def dashboard_view(request):
    # Retrieve user records, limited to the latest 15 entries for maximum database efficiency
    records = CarbonService.get_user_records(request.user)[:15]
    
    # Retrieve complete aggregate stats (calculated at DB-level)
    stats = CarbonService.get_user_stats(request.user)
    
    # Extract latest record from the sliced records list
    latest = records[0] if len(records) > 0 else None
    
    # Generate problem alignment metrics and widgets contexts
    score = SustainabilityService.calculate_sustainability_score(latest)
    insights = SustainabilityService.get_reduction_insights(latest)
    recommendations = SustainabilityService.get_personalized_recommendations(latest)
    
    benchmark = SustainabilityService.get_benchmark_comparison(latest)
    trees = SustainabilityService.get_tree_offset_equivalent(latest)
    monthly_goal = SustainabilityService.get_monthly_goal_tracking(request.user)
    badges = SustainabilityService.get_achievement_badges(request.user, stats, latest)
    weekly_improvement = SustainabilityService.get_weekly_improvement(records)
    reduction_targets = SustainabilityService.get_personalized_reduction_targets(latest)
    impact = SustainabilityService.get_impact_summary(request.user, records, stats)

    # Format chart data safely as JSON to prevent template-parsing script validation errors
    chart_list = [
        {
            'date': r.created_at.strftime('%d %b') if r.created_at else '',
            'total_carbon': r.total_carbon
        }
        for r in reversed(records)
    ]
    chart_data_json = json.dumps(chart_list)

    # Compile template context variables
    context = {
        'records': records,
        'stats': stats,
        'latest': latest,
        'sustainability_score': score,
        'breakdown': insights.get('breakdown', {}),
        'highest_sector': insights.get('highest_sector', 'None'),
        'recommendations': recommendations,
        
        'benchmark': benchmark,
        'trees': trees,
        'monthly_goal': monthly_goal,
        'badges': badges,
        'weekly_improvement': weekly_improvement,
        'reduction_targets': reduction_targets,
        'impact': impact,
        'chart_data_json': chart_data_json,
    }

    return render(request, 'dashboard.html', context)