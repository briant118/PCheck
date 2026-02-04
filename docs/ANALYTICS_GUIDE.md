# PCheck Analytics System - Complete Guide

## Overview

The enhanced analytics system in PCheck now provides both **descriptive analytics** (historical data analysis) and **predictive analytics** (forecasting and trend analysis). This addresses the panel feedback requesting more comprehensive reporting capabilities beyond basic statistics.

## Features

### 1. Descriptive Analytics (What Happened)

Provides historical insights into:

#### Booking Statistics
- Total bookings, confirmed, and cancelled bookings
- Average booking duration
- Total PC utilization hours
- Bookings by college and top users

#### PC Utilization Metrics
- Total PCs and their status breakdown
- Available, in-use, in-queue, and in-repair devices
- System utilization percentage

#### Violation Statistics
- Total violations by severity level (minor, moderate, major)
- Resolved vs. unresolved violations
- Repeat offenders identification
- Suspended users count

#### Faculty Booking Analysis
- Total faculty bookings and device requests
- Average devices per booking
- Bookings by college

#### Peripheral Events Summary
- Device attachment/removal frequency
- Most affected PCs
- Most common problematic devices

### 2. Predictive Analytics (What Will Happen)

Advanced forecasting and anomaly detection:

#### Peak Usage Predictions
- **Peak Days of Week**: Identifies which days see highest PC usage
- **Peak Hours**: Determines busiest times of day for resource planning
- Visual representation of hourly and daily patterns

#### Booking Trend Analysis
- **Trend Direction**: Identifies if bookings are increasing, decreasing, or stable
- **Weekly Forecasts**: Predicts next week's booking volume
- **Historical Context**: Shows patterns based on 12+ weeks of data

#### User Behavior Change Detection
- Month-over-month comparison of booking patterns
- Change percentage and trend classification
- Early warning system for significant shifts in usage

#### High-Risk User Identification
- **Risk Scoring**: Quantitative risk assessment based on violation patterns
- **Risk Levels**: Categorizes users as high, medium, or low risk
- **Risk Score Formula**: (Total Violations × 2) + (Major × 3) + (Moderate × 1.5)
- Actionable alerts for staff intervention

#### PC Maintenance Prediction
- **Hardware Health Analysis**: Based on peripheral device event frequency
- **Removal Rate Calculation**: Identifies PCs with excessive device disconnections
- **Priority Levels**: High, medium, or low maintenance priority
- Helps prevent system failures before they occur

#### Resource Demand Forecasting
- **14-Day Forecast**: Predicts device requirements for upcoming faculty bookings
- **Peak Demand Days**: Identifies when maximum resources will be needed
- **Capacity Planning**: Supports resource allocation decisions

#### Anomaly Detection
- **Cancellation Rate Anomalies**: Alerts when cancellations exceed normal patterns
- **Hardware Event Anomalies**: Detects excessive peripheral device issues
- **Violation Spikes**: Identifies users with unusual violation patterns
- **Severity Levels**: High or medium priority alerts

## Access Points

### Web Dashboard
All analytics are accessible through the main interface:

1. **Analytics Dashboard** (`/main_app/analytics/`)
   - Comprehensive overview of all metrics
   - Period selection (7, 14, 30, 60, 90 days)
   - Both descriptive and predictive analytics

2. **Booking Predictions** (`/main_app/booking-predictions/`)
   - Detailed peak hour and day analysis
   - Booking trend visualization
   - User behavior change tracking
   - Recommendations based on trends

3. **Risk Analysis** (`/main_app/risk-analysis/`)
   - High-risk user identification
   - PC maintenance requirements
   - Detected anomalies with severity levels
   - Risk mitigation recommendations

4. **Resource Demand Forecast** (`/main_app/resource-demand/`)
   - 14-day device requirement forecast
   - Peak demand identification
   - Capacity planning guide
   - Operational recommendations

### JSON API
For programmatic access:

```
GET /main_app/analytics-api/
    ?period=30           # 7, 14, 30, 60, 90
    &section=all         # all, descriptive, predictive
```

Response includes all analytics data in JSON format, suitable for:
- Integration with other systems
- Custom reporting tools
- Dashboard creation
- Data warehousing

## Data Analysis Methods

### Booking Pattern Analysis
- Analyzes confirmed bookings over specified period
- Groups by hour of day and day of week
- Identifies statistical outliers as peaks
- Provides 12+ week historical context

### Violation Risk Scoring
- Weighted scoring system for user violations
- Factors: count, severity level, recency
- Three-tier risk classification
- Enables proactive staff intervention

### Hardware Health Monitoring
- Tracks peripheral device events per PC
- Calculates device removal rate
- Identifies problem devices and computers
- Suggests maintenance priority

### Trend Analysis
- Weekly aggregation of booking counts
- Moving average calculations
- Percentage change calculations
- Growth/decline identification

### Anomaly Detection Methods
- Threshold-based alerting (e.g., >30% cancellation rate)
- Event frequency analysis (>20 events in 7 days)
- Pattern recognition (5+ violations in 7 days)
- Multi-level severity assessment

## Technical Implementation

### Core Classes

#### `DescriptiveAnalytics`
Provides historical data analysis methods:
- `get_booking_statistics()` - Booking metrics
- `get_pc_utilization()` - PC status metrics
- `get_violation_statistics()` - Violation data
- `get_faculty_booking_statistics()` - Faculty booking data
- `get_peripheral_events_summary()` - Hardware event data

#### `PredictiveAnalytics`
Provides forecasting and prediction methods:
- `predict_peak_usage_hours()` - Peak time analysis
- `predict_peak_usage_days()` - Peak day analysis
- `predict_booking_trends()` - Trend forecasting
- `predict_user_violation_risk()` - Risk scoring
- `predict_pc_maintenance_needs()` - Hardware prediction
- `predict_resource_demand()` - Capacity forecasting
- `predict_user_behavior_change()` - Behavior analysis
- `anomaly_detection()` - System anomalies

#### `AnalyticsSummary`
Comprehensive reporting:
- `get_comprehensive_report(days)` - Full analytics report

### Views

1. `analytics_dashboard()` - Renders main dashboard HTML
2. `analytics_api()` - Returns JSON data for API consumers
3. `booking_predictions()` - Predictions-focused view
4. `risk_analysis()` - Risk assessment view
5. `resource_demand_forecast()` - Resource planning view

## Usage Examples

### View Analytics Dashboard
Navigate to `/main_app/analytics/` in your browser (requires staff login)

### Get JSON Data
```bash
# All analytics for last 30 days
curl http://localhost:8000/main_app/analytics-api/?period=30

# Only predictive analytics
curl http://localhost:8000/main_app/analytics-api/?section=predictive

# Last 90 days descriptive only
curl http://localhost:8000/main_app/analytics-api/?period=90&section=descriptive
```

### In Django Code
```python
from main_app.analytics import AnalyticsSummary, PredictiveAnalytics

# Get comprehensive report
report = AnalyticsSummary.get_comprehensive_report(days=30)

# Get specific predictions
peak_hours = PredictiveAnalytics.predict_peak_usage_hours()
high_risk_users = PredictiveAnalytics.predict_user_violation_risk()
```

## Key Metrics Explained

### Risk Score
- **Calculation**: (Total Violations × 2) + (Major Violations × 3) + (Moderate Violations × 1.5)
- **High Risk**: Score ≥ 10
- **Medium Risk**: Score 5-9
- **Low Risk**: Score < 5

### Device Removal Rate
- **High Priority**: > 50% removal rate
- **Medium Priority**: 30-50% removal rate
- **Low Priority**: < 30% removal rate

### Cancellation Rate
- **Anomaly Threshold**: > 30% of bookings cancelled
- **Investigation Recommended**: When threshold exceeded
- **Context**: Compare against historical baseline

### Demand Levels
- **High Demand**: > 30 devices needed
- **Medium Demand**: 16-30 devices needed
- **Low Demand**: 1-15 devices needed

## Recommendations for Use

### Staff Actions
1. **Review High-Risk Users Weekly**
   - Check risk analysis report
   - Schedule interventions for high-risk users
   - Document all actions taken

2. **Plan Maintenance Based on Predictions**
   - Schedule maintenance during low-demand days
   - Prioritize high-priority maintenance needs
   - Avoid maintenance on predicted peak days

3. **Prepare for Predicted Peaks**
   - Review next week's resource demand forecast
   - Adjust staffing levels accordingly
   - Ensure all devices are functional

4. **Investigate Anomalies**
   - Unusual cancellation spikes
   - Hardware failure patterns
   - User behavior changes

### System Administrators
1. **Monitor Trends Over Time**
   - Set up periodic dashboard reviews
   - Track consistency of predictions
   - Refine thresholds as needed

2. **Capacity Planning**
   - Use resource demand forecasts for procurement
   - Plan facility upgrades based on trends
   - Allocate budget for maintenance

3. **Performance Optimization**
   - Identify and address hardware bottlenecks
   - Optimize scheduling based on peak predictions
   - Reduce cancellation rates through process improvements

## Data Requirements

For accurate predictions, the system needs:
- **Minimum 4 weeks**: For reliable weekly trends
- **Minimum 8 weeks**: For daily pattern analysis
- **Minimum 12 weeks**: For month-over-month comparisons
- **Historical violations**: For risk scoring accuracy
- **Peripheral events**: For hardware prediction

Initial implementation should allow 2-3 months of data collection before relying on predictive features.

## Future Enhancements

Potential additions to the analytics system:
1. Machine learning models for demand forecasting
2. Time-series analysis for seasonal patterns
3. Automated alert system for anomalies
4. Predictive maintenance using failure history
5. User satisfaction correlation analysis
6. Resource optimization recommendations
7. Scheduled email reports
8. Custom report builder
9. Data export in multiple formats
10. Interactive dashboards with filters

## Troubleshooting

### No Data Available
- Ensure data exists in the specified period
- Check that records have required date fields
- Verify database connections

### Predictions Appear Inaccurate
- Confirm minimum data collection period (4+ weeks)
- Check for incomplete/corrupted data
- Review threshold settings

### Performance Issues
- Analytics queries may be slow with large datasets
- Consider data archival for old records
- Add database indexes on date fields

## Support

For questions or issues with the analytics system, contact:
- Development Team: [contact info]
- System Administrator: [contact info]

## Version History

**v1.0.0** (February 2026)
- Initial analytics system implementation
- Descriptive analytics for all major features
- Predictive analytics for trends and risks
- Web dashboard and JSON API
- Risk scoring and anomaly detection
