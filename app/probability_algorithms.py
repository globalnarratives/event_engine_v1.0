"""
Probability Calculation Algorithms for Global Narratives Event Engine
Version 1.0 - Fibonacci-inspired categorical weighting system

This module implements the core transformation algorithms that convert
analyst event weight assignments into probability adjustments, velocity,
and volatility metrics across multiple time windows.
"""

from datetime import datetime, timedelta
from typing import List, Tuple, Dict, Optional
from decimal import Decimal


class WeightCategory:
    """Weight category definitions with Fibonacci-inspired multipliers"""
    MINOR = (0.1, 4.9, 1)      # 0.1 ≤ |weight| ≤ 4.9, multiplier = 1x
    MODERATE = (5.0, 7.9, 3)    # 5.0 ≤ |weight| ≤ 7.9, multiplier = 3x
    MAJOR = (8.0, 10.9, 8)      # 8.0 ≤ |weight| ≤ 10.9, multiplier = 8x
    CRITICAL = (11.0, 12.0, 20) # 11.0 ≤ |weight| ≤ 12.0, multiplier = 20x
    
    @classmethod
    def categorize(cls, abs_weight: float) -> Tuple[str, int]:
        """
        Categorize an absolute weight value and return category name and multiplier.
        
        Args:
            abs_weight: Absolute value of the weight
            
        Returns:
            Tuple of (category_name, multiplier)
        """
        if cls.MINOR[0] <= abs_weight <= cls.MINOR[1]:
            return ('minor', cls.MINOR[2])
        elif cls.MODERATE[0] <= abs_weight <= cls.MODERATE[1]:
            return ('moderate', cls.MODERATE[2])
        elif cls.MAJOR[0] <= abs_weight <= cls.MAJOR[1]:
            return ('major', cls.MAJOR[2])
        elif cls.CRITICAL[0] <= abs_weight <= cls.CRITICAL[1]:
            return ('critical', cls.CRITICAL[2])
        else:
            # Should never happen with valid weights
            raise ValueError(f"Weight {abs_weight} outside valid range [0.1-12.0]")


class ProbabilityCalculator:
    """
    Calculates probability adjustments from event weights using categorical weighting.
    
    Supports four time windows with different basis point conversions:
    - Immediate: Single event, 4x conversion (60% dampening)
    - 1-Day: Calendar day batch, 10x conversion
    - 7-Day: Rolling 7-day batch, 10x conversion
    - 30-Day: Rolling 30-day batch, 10x conversion
    """
    
    # Basis point conversion factors
    CONVERSION_IMMEDIATE = 4
    CONVERSION_BATCH = 10
    
    @staticmethod
    def calculate_immediate(weight: float) -> Dict[str, float]:
        """
        Calculate immediate probability adjustment from a single event.
        
        Args:
            weight: Event weight (-12.0 to +12.0, excluding 0)
            
        Returns:
            Dictionary with:
                - probability_adjustment: Change in probability (decimal, e.g., 0.0107 = 1.07%)
                - basis_points: Basis point value
                - adjusted_weight: Category-modified weight
                - category: Weight category name
        """
        # Step 1: Categorize and apply multiplier
        abs_weight = abs(weight)
        category, multiplier = WeightCategory.categorize(abs_weight)
        
        # Step 2: Apply multiplier (preserve sign)
        sign = 1 if weight > 0 else -1
        adjusted_weight = abs_weight * multiplier * sign
        
        # Step 3: Convert to basis points (immediate = 4x)
        basis_points = adjusted_weight * ProbabilityCalculator.CONVERSION_IMMEDIATE
        
        # Step 4: Convert to probability adjustment
        probability_adjustment = basis_points / 10000
        
        return {
            'probability_adjustment': round(probability_adjustment, 6),
            'basis_points': round(basis_points, 2),
            'adjusted_weight': round(adjusted_weight, 2),
            'category': category,
            'multiplier': multiplier
        }
    
    @staticmethod
    def calculate_batch(events: List[Tuple[str, float, datetime]], 
                       window_type: str = '1day') -> Dict[str, float]:
        """
        Calculate batched probability adjustment from multiple events.
        
        Args:
            events: List of (event_code, weight, timestamp) tuples
            window_type: '1day', '7day', or '30day'
            
        Returns:
            Dictionary with:
                - probability_adjustment: Change in probability
                - basis_points: Basis point value
                - adjusted_weight: Total category-modified weight
                - category_breakdown: Dict of weights by category
                - event_count: Number of events in batch
        """
        if not events:
            return {
                'probability_adjustment': 0.0,
                'basis_points': 0.0,
                'adjusted_weight': 0.0,
                'category_breakdown': {},
                'event_count': 0
            }
        
        # Step 1: Categorize and sum weights by category
        category_sums = {
            'minor': 0.0,
            'moderate': 0.0,
            'major': 0.0,
            'critical': 0.0
        }
        
        for event_code, weight, timestamp in events:
            abs_weight = abs(weight)
            category, _ = WeightCategory.categorize(abs_weight)
            # Preserve sign when summing
            sign = 1 if weight > 0 else -1
            category_sums[category] += abs_weight * sign
        
        # Step 2: Apply category multipliers
        modified_minor = category_sums['minor'] * WeightCategory.MINOR[2]
        modified_moderate = category_sums['moderate'] * WeightCategory.MODERATE[2]
        modified_major = category_sums['major'] * WeightCategory.MAJOR[2]
        modified_critical = category_sums['critical'] * WeightCategory.CRITICAL[2]
        
        # Step 3: Calculate net adjusted weight
        adjusted_weight = modified_minor + modified_moderate + modified_major + modified_critical
        
        # Step 4: Convert to basis points (batch = 10x)
        basis_points = adjusted_weight * ProbabilityCalculator.CONVERSION_BATCH
        
        # Step 5: Convert to probability adjustment
        probability_adjustment = basis_points / 10000
        
        return {
            'probability_adjustment': round(probability_adjustment, 6),
            'basis_points': round(basis_points, 2),
            'adjusted_weight': round(adjusted_weight, 2),
            'category_breakdown': {
                'minor': {'sum': round(category_sums['minor'], 2), 'modified': round(modified_minor, 2)},
                'moderate': {'sum': round(category_sums['moderate'], 2), 'modified': round(modified_moderate, 2)},
                'major': {'sum': round(category_sums['major'], 2), 'modified': round(modified_major, 2)},
                'critical': {'sum': round(category_sums['critical'], 2), 'modified': round(modified_critical, 2)}
            },
            'event_count': len(events),
            'window_type': window_type
        }


class VolatilityCalculator:
    """
    Calculates volatility metric: total absolute analytical activity in a time window.
    
    Volatility measures the intensity of analytical work regardless of direction,
    using category-weighted absolute values.
    """
    
    @staticmethod
    def calculate(events: List[Tuple[str, float, datetime]]) -> Dict[str, float]:
        """
        Calculate volatility from a batch of events.
        
        Args:
            events: List of (event_code, weight, timestamp) tuples
            
        Returns:
            Dictionary with:
                - volatility_score: Raw volatility value
                - category_breakdown: Absolute sums by category
                - event_count: Number of events
        """
        if not events:
            return {
                'volatility_score': 0.0,
                'category_breakdown': {},
                'event_count': 0
            }
        
        # Step 1: Categorize and sum absolute weights by category
        category_abs_sums = {
            'minor': 0.0,
            'moderate': 0.0,
            'major': 0.0,
            'critical': 0.0
        }
        
        for event_code, weight, timestamp in events:
            abs_weight = abs(weight)
            category, _ = WeightCategory.categorize(abs_weight)
            category_abs_sums[category] += abs_weight
        
        # Step 2: Apply category multipliers
        modified_minor = category_abs_sums['minor'] * WeightCategory.MINOR[2]
        modified_moderate = category_abs_sums['moderate'] * WeightCategory.MODERATE[2]
        modified_major = category_abs_sums['major'] * WeightCategory.MAJOR[2]
        modified_critical = category_abs_sums['critical'] * WeightCategory.CRITICAL[2]
        
        # Step 3: Sum to raw volatility (no transformation for now)
        volatility_score = modified_minor + modified_moderate + modified_major + modified_critical
        
        return {
            'volatility_score': round(volatility_score, 2),
            'category_breakdown': {
                'minor': {'sum': round(category_abs_sums['minor'], 2), 'modified': round(modified_minor, 2)},
                'moderate': {'sum': round(category_abs_sums['moderate'], 2), 'modified': round(modified_moderate, 2)},
                'major': {'sum': round(category_abs_sums['major'], 2), 'modified': round(modified_major, 2)},
                'critical': {'sum': round(category_abs_sums['critical'], 2), 'modified': round(modified_critical, 2)}
            },
            'event_count': len(events)
        }


class VelocityCalculator:
    """
    Calculates velocity metric: average analytical intensity per event.
    
    Velocity = Volatility / Event Count, measuring concentration of weight.
    """
    
    @staticmethod
    def calculate(volatility_score: float, event_count: int) -> float:
        """
        Calculate velocity from volatility and event count.
        
        Args:
            volatility_score: Raw volatility value
            event_count: Number of events in window
            
        Returns:
            Velocity score (0.0 if event_count is 0)
        """
        if event_count == 0:
            return 0.0
        
        return round(volatility_score / event_count, 2)


class TimeWindowFilter:
    """
    Filters events by time window for batch calculations.
    
    Supports:
    - 1-day: Calendar day (UTC midnight to midnight)
    - 7-day: Rolling 7 days (today + previous 6 days)
    - 30-day: Rolling 30 days (today + previous 29 days)
    """
    
    @staticmethod
    def filter_1day(events: List[Tuple[str, float, datetime]], 
                   reference_date: Optional[datetime] = None) -> List[Tuple[str, float, datetime]]:
        """
        Filter events to current calendar day (UTC).
        
        Args:
            events: List of (event_code, weight, timestamp) tuples
            reference_date: Date to use (defaults to now)
            
        Returns:
            Filtered list of events
        """
        if reference_date is None:
            reference_date = datetime.utcnow()
        
        # UTC midnight of reference date
        day_start = reference_date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        return [(code, weight, ts) for code, weight, ts in events 
                if day_start <= ts < day_end]
    
    @staticmethod
    def filter_7day(events: List[Tuple[str, float, datetime]], 
                   reference_date: Optional[datetime] = None) -> List[Tuple[str, float, datetime]]:
        """
        Filter events to rolling 7-day window.
        
        Args:
            events: List of (event_code, weight, timestamp) tuples
            reference_date: End date of window (defaults to now)
            
        Returns:
            Filtered list of events
        """
        if reference_date is None:
            reference_date = datetime.utcnow()
        
        cutoff = reference_date - timedelta(days=7)
        
        return [(code, weight, ts) for code, weight, ts in events 
                if ts >= cutoff]
    
    @staticmethod
    def filter_30day(events: List[Tuple[str, float, datetime]], 
                    reference_date: Optional[datetime] = None) -> List[Tuple[str, float, datetime]]:
        """
        Filter events to rolling 30-day window.
        
        Args:
            events: List of (event_code, weight, timestamp) tuples
            reference_date: End date of window (defaults to now)
            
        Returns:
            Filtered list of events
        """
        if reference_date is None:
            reference_date = datetime.utcnow()
        
        cutoff = reference_date - timedelta(days=30)
        
        return [(code, weight, ts) for code, weight, ts in events 
                if ts >= cutoff]


# Convenience function for complete calculation
def calculate_all_metrics(events: List[Tuple[str, float, datetime]], 
                         window_type: str = 'immediate',
                         reference_date: Optional[datetime] = None) -> Dict:
    """
    Calculate all metrics (probability, volatility, velocity) for a given window.
    
    Args:
        events: List of (event_code, weight, timestamp) tuples
        window_type: 'immediate', '1day', '7day', or '30day'
        reference_date: Reference time for calculations (defaults to now)
        
    Returns:
        Dictionary with all calculated metrics
    """
    if window_type == 'immediate':
        # For immediate, events should contain exactly one event
        if len(events) != 1:
            raise ValueError("Immediate calculation requires exactly one event")
        
        event_code, weight, timestamp = events[0]
        prob_result = ProbabilityCalculator.calculate_immediate(weight)
        
        # Volatility = absolute modified weight for single event
        abs_weight = abs(weight)
        category, multiplier = WeightCategory.categorize(abs_weight)
        volatility_score = abs_weight * multiplier
        
        return {
            'window_type': 'immediate',
            'probability_adjustment': prob_result['probability_adjustment'],
            'basis_points': prob_result['basis_points'],
            'adjusted_weight': prob_result['adjusted_weight'],
            'category': prob_result['category'],
            'volatility_score': round(volatility_score, 2),
            'velocity': round(volatility_score, 2),  # Same as volatility for single event
            'event_count': 1
        }
    
    else:
        # Batch calculation
        # Filter events by window
        if window_type == '1day':
            filtered_events = TimeWindowFilter.filter_1day(events, reference_date)
        elif window_type == '7day':
            filtered_events = TimeWindowFilter.filter_7day(events, reference_date)
        elif window_type == '30day':
            filtered_events = TimeWindowFilter.filter_30day(events, reference_date)
        else:
            raise ValueError(f"Unknown window_type: {window_type}")
        
        # Calculate metrics
        prob_result = ProbabilityCalculator.calculate_batch(filtered_events, window_type)
        vol_result = VolatilityCalculator.calculate(filtered_events)
        velocity = VelocityCalculator.calculate(vol_result['volatility_score'], 
                                               vol_result['event_count'])
        
        return {
            'window_type': window_type,
            'probability_adjustment': prob_result['probability_adjustment'],
            'basis_points': prob_result['basis_points'],
            'adjusted_weight': prob_result['adjusted_weight'],
            'category_breakdown': prob_result['category_breakdown'],
            'volatility_score': vol_result['volatility_score'],
            'volatility_breakdown': vol_result['category_breakdown'],
            'velocity': velocity,
            'event_count': prob_result['event_count']
        }