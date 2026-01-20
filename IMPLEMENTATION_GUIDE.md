# PROBABILITY CALCULATION SYSTEM v1.5 - IMPLEMENTATION GUIDE

## Overview

This implementation replaces the simple additive placeholder with a sophisticated categorical weighting system based on Fibonacci-inspired magnitude jumps. The system calculates probability adjustments, velocity, and volatility across four time windows.

---

## File Structure

```
/app/
  probability_algorithms.py    # Core calculation algorithms (NEW)
  models.py                     # Updated MarkedScenario.recalculate_probability()
  routes/scenarios.py           # Updated weight validation
  templates/scenarios/
    link_event.html             # Updated weight input UI

/migrations/
  probability_calc_v1.py        # Database migration for weight column (NEW)
```

---

## Weight System

### Scale
- **Range:** -12.0 to +12.0
- **Increment:** 0.1 (e.g., 3.5, -7.2, 11.0)
- **Excluded:** 0 (zero weight not allowed)
- **Total values:** 240 possible weights

### Categories (Fibonacci-inspired multipliers)
```
Minor:    0.1 ≤ |weight| ≤ 4.0   → 1x  multiplier
Moderate: 5.0 ≤ |weight| ≤ 7.0   → 3x  multiplier
Major:    8.0 ≤ |weight| ≤ 10.0  → 8x  multiplier
Critical: 11.0 ≤ |weight| ≤ 12.0 → 20x multiplier
```

### Example
- Weight 3.5 (Minor) → adjusted weight = 3.5 × 1 = 3.5
- Weight 5.0 (Moderate) → adjusted weight = 5.0 × 3 = 15.0
- Weight 9.0 (Major) → adjusted weight = 9.0 × 8 = 72.0
- Weight 12.0 (Critical) → adjusted weight = 12.0 × 20 = 240.0

---

## Time Windows

### Four calculation windows:

1. **Immediate** (single event, real-time)
   - Triggered on event link
   - Basis point conversion: 4x (60% dampening vs batch)
   - Purpose: Show instant impact with recency bias correction

2. **1-Day** (calendar day, UTC)
   - Window: Midnight to midnight UTC
   - Basis point conversion: 10x
   - Purpose: Daily consensus view

3. **7-Day** (rolling window)
   - Window: Today + previous 6 days
   - Basis point conversion: 10x
   - Purpose: Weekly trend

4. **30-Day** (rolling window)
   - Window: Today + previous 29 days
   - Basis point conversion: 10x
   - Purpose: Strategic outlook

---

## Calculation Flow

### Immediate Calculation (on event link)

```python
from probability_algorithms import ProbabilityCalculator

# 1. Calculate adjustment
result = ProbabilityCalculator.calculate_immediate(weight)

# Returns:
{
    'probability_adjustment': 0.0140,  # 1.4% increase
    'basis_points': 140,
    'adjusted_weight': 35.0,
    'category': 'moderate',
    'multiplier': 3
}

# 2. Apply to current probability
new_probability = current_probability + result['probability_adjustment']
new_probability = max(0.0, min(1.0, new_probability))  # Clamp [0, 1]

# 3. Record in history with full metadata
```

### Batch Calculation (scheduled jobs)

```python
from probability_algorithms import calculate_all_metrics

# Get all events linked to this marked_scenario
events = [
    (event_code, weight, timestamp),
    # ...
]

# Calculate for 7-day window
result = calculate_all_metrics(events, window_type='7day')

# Returns:
{
    'window_type': '7day',
    'probability_adjustment': 0.0523,
    'basis_points': 523,
    'adjusted_weight': 52.3,
    'category_breakdown': {
        'minor': {'sum': 8.5, 'modified': 8.5},
        'moderate': {'sum': 12.0, 'modified': 36.0},
        # ...
    },
    'volatility_score': 95.7,
    'volatility_breakdown': {...},
    'velocity': 9.57,  # 95.7 / 10 events
    'event_count': 10
}
```

---

## Metrics Explained

### 1. Probability Adjustment
**What it is:** The change in scenario probability due to event(s)

**Formula:**
```
Adjusted Weight → Basis Points → Probability
adjusted_weight × conversion_factor → / 10000 → decimal
```

**Example:**
- Adjusted weight: 10.7
- Conversion (1-day): × 10 = 107 basis points
- Probability: 107 / 10000 = 0.0107 (1.07%)

### 2. Volatility
**What it is:** Total absolute analytical activity (intensity regardless of direction)

**Formula:**
```
Sum of |weights| by category → Apply multipliers → Total
```

**Example:**
- Events: [-1.2, -3.1, 5.0]
- Minor absolute: 1.2 + 3.1 = 4.3 × 1 = 4.3
- Moderate absolute: 5.0 × 3 = 15.0
- Volatility = 4.3 + 15.0 = 19.3

**Purpose:** Shows how much analytical effort is being applied. High volatility = intense scrutiny.

### 3. Velocity
**What it is:** Average analytical intensity per event

**Formula:**
```
Velocity = Volatility / Event Count
```

**Example:**
- Volatility: 19.3
- Event count: 3
- Velocity: 19.3 / 3 = 6.43

**Purpose:** Distinguishes between "many small signals" vs "few major signals"

---

## Database Schema

### Current (Postgres)
Stores immutable analytical inputs:

```sql
-- scenario_events table
id                  INTEGER
marked_scenario_id  INTEGER (FK)
event_code          VARCHAR(50) (FK)
weight              NUMERIC(4,1)  -- UPDATED: was NUMERIC(5,3)
notes               TEXT
linked_at           TIMESTAMP
linked_by_id        INTEGER (FK)
```

### Probability History (JSONB in marked_scenarios)
```json
{
  "probability": 0.47,
  "timestamp": "2026-01-19T14:23:00Z",
  "reason": "Event 20260118.usa.001 linked",
  "event_code": "20260118.usa.001",
  "user_id": 1,
  "weight": 5.5,
  "category": "moderate",
  "multiplier": 3,
  "adjusted_weight": 16.5,
  "basis_points": 66,
  "probability_adjustment": 0.0066
}
```

### Future: Time-Series Storage (Separate DB)
For computed batch metrics:

```
Structure TBD - will store:
- marked_scenario_id
- window_type (1day/7day/30day)
- timestamp
- probability
- volatility
- velocity
- category_breakdown
```

---

## Installation Steps

### 1. Add algorithm module to Flask app
```bash
cp probability_algorithms.py /path/to/app/
```

### 2. Update models.py
Replace file with updated version that includes new `recalculate_probability()` method.

### 3. Update routes/scenarios.py
Replace file with updated version that includes weight validation.

### 4. Update templates
Replace `templates/scenarios/link_event.html` with updated version.

### 5. Run database migration
```bash
# Set down_revision to your latest migration ID
# Edit migration_probability_calc_v1.py

flask db upgrade
```

### 6. Test the system
```python
# In Flask shell
from app import db
from app.models import MarkedScenario, ScenarioEvent

# Test immediate calculation
marked = MarkedScenario.query.first()
marked.add_event('test.event.001', 5.5, user_id=1)
db.session.commit()

# Check probability_history
print(marked.probability_history[-1])
```

---

## Future Work

### Phase 2.1: Batch Calculation Scheduler
- Implement scheduled jobs (every 6 hours or daily)
- Calculate 1-day, 7-day, 30-day metrics for all active marked scenarios
- Store in time-series database

### Phase 2.2: Time-Series Storage
- Choose storage solution (InfluxDB, TimescaleDB, or simple SQLite)
- Design schema for computed metrics
- Implement read/write interfaces

### Phase 2.3: Visualization Updates
- Update charts to show all four time windows
- Display velocity and volatility metrics
- Add category breakdown visualization

### Phase 2.4: Algorithm Extensibility
- Create algorithm registry system
- Allow multiple transformation algorithms
- Enable algorithm comparison view

### Phase 2.5: Advanced Features
- Volatility premium (optional modifier)
- Decay functions for older events
- Cross-window relationships
- Extreme probability dampening (logistic)

---

## Testing Checklist

- [ ] Weight validation works (rejects 0, out-of-range, wrong increments)
- [ ] Immediate calculation produces correct results
- [ ] Categories correctly assigned (minor/moderate/major/critical)
- [ ] Multipliers applied correctly (1x/3x/8x/20x)
- [ ] Basis points conversion correct (4x immediate, 10x batch)
- [ ] Probability clamped to [0, 1]
- [ ] History records full metadata
- [ ] Unlinking events works correctly
- [ ] Database migration runs without errors
- [ ] UI displays new weight system information

---

## Contact / Questions

For implementation questions or algorithm refinements, refer to:
- Algorithm specification document
- Original 2017 spreadsheet screenshots
- Fibonacci justification rationale

**Version:** 1.0  
**Date:** January 19, 2026  
**Status:** Ready for alpha testing deployment
