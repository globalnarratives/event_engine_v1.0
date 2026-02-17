from app.models import ScenarioEvent
from app.probability_algorithms import VolatilityCalculator, VelocityCalculator


def compute_marked_metrics(marked_scenarios):
    """Compute volatility, velocity, and event count for a list of MarkedScenario objects.

    Returns a list of dicts:
        {marked, pi, pc, volatility, velocity, event_count}
    """
    results = []
    for marked in marked_scenarios:
        event_links = ScenarioEvent.query.filter_by(
            marked_scenario_id=marked.id
        ).all()

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
