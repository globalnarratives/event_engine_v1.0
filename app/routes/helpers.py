from app.models import ScenarioEvent
from app.probability_algorithms import VolatilityCalculator, VelocityCalculator


def compute_marked_metrics(marked_scenarios):
    """Compute volatility, velocity, and event count for a list of MarkedScenario objects.

    Returns a list of dicts:
        {marked, pi, pc, volatility, velocity, event_count}
    """
    if not marked_scenarios:
        return []

    # Batch-load all ScenarioEvent rows in one query instead of one per scenario
    marked_ids = [m.id for m in marked_scenarios]
    all_links = ScenarioEvent.query.filter(
        ScenarioEvent.marked_scenario_id.in_(marked_ids)
    ).all()

    links_by_id = {}
    for link in all_links:
        links_by_id.setdefault(link.marked_scenario_id, []).append(link)

    results = []
    for marked in marked_scenarios:
        event_links = links_by_id.get(marked.id, [])

        events_data = [
            (link.event_code, float(link.weight), link.linked_at)
            for link in event_links
        ]

        if events_data:
            volatility_result = VolatilityCalculator.calculate(events_data)
            velocity = VelocityCalculator.calculate(
                volatility_result['volatility_score'],
                len(events_data)
            )
            volatility = volatility_result['volatility_score']
        else:
            velocity = 0.0
            volatility = 0.0

        results.append({
            'marked': marked,
            'pi': marked.initial_probability,
            'pc': marked.current_probability,
            'velocity': velocity,
            'volatility': volatility,
            'event_count': len(events_data)
        })
    return results
