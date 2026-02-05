# PCheck Analytics - Quick Reference Guide for Staff

## Accessing Analytics

**URL**: `/main_app/analytics/`  
**Requirements**: Staff login  
**Access**: Use the navigation menu once logged in

---

## Dashboard Sections

### 📊 Descriptive Analytics (Historical Data)

#### Bookings Overview
- **Total Bookings**: All confirmed bookings in selected period
- **Confirmed**: Completed bookings
- **Cancelled**: User cancellations
- **Avg Duration**: Average time per booking
- **PC Hours**: Total machine utilization time

#### PC Status
- **Total PCs**: All machines in system
- **Active**: Connected and operational
- **Available**: Ready for booking
- **In Use**: Currently occupied
- **In Queue**: Pending reservation
- **In Repair**: Under maintenance

#### Violations
- **Total**: All violations recorded
- **Resolved**: Issues addressed
- **Unresolved**: Pending action
- **By Level**: Minor/Moderate/Major breakdown
- **Suspended Users**: Users currently blocked

#### Faculty Bookings & Devices
- Total faculty block bookings
- Device requests and averages
- Peripheral device events

---

## 🔮 Predictive Analytics (Future Insights)

### Peak Usage Patterns
- **Best Days**: Days with highest bookings (for staffing)
- **Busy Hours**: Times with most demand (for planning)
- **Daily Distribution**: Usage by day of week
- **Hourly Distribution**: Usage by hour of day

### Booking Trends
- **Trend**: Increasing ↗️ | Decreasing ↘️ | Stable →
- **Current Average**: Weekly bookings
- **Next Week Forecast**: Predicted demand
- **Interpretation**: What the trend means for your planning

### User Behavior Changes
- **Last Month**: Previous month's bookings
- **This Month**: Current month's bookings
- **Change**: Percentage increase/decrease
- **Trend**: Overall pattern classification

### 👥 High-Risk Users
**What it means**: Users likely to violate policies again

| Risk Level | Score | Action |
|-----------|-------|--------|
| 🔴 HIGH   | ≥ 10  | Interview & monitor closely |
| 🟡 MEDIUM | 5-9   | Monitor; document incidents |
| 🟢 LOW    | < 5   | Standard monitoring |

**Risk Score** = (Total Violations × 2) + (Major × 3) + (Moderate × 1.5)

### 🔧 PC Maintenance Needs
**What it means**: Computers likely to fail based on device events

| Priority | Removal Rate | Action |
|----------|-------------|--------|
| 🔴 HIGH  | > 50%       | Schedule maintenance ASAP |
| 🟡 MEDIUM| 30-50%      | Plan maintenance soon |
| 🟢 LOW   | < 30%       | Monitor; routine maintenance |

### 🚨 Anomalies Detected
**What it means**: Unusual patterns that need investigation

- **High Cancellation Rate**: Too many bookings cancelled
- **Hardware Events**: PC having device problems
- **Violation Spikes**: User suddenly has many violations

---

## 📈 Detailed Reports

### Booking Predictions Report
Navigate to: `/main_app/booking-predictions/`

Shows detailed analysis of:
- Peak days with expected usage
- Peak hours with load visualization
- 14-day trend forecast
- User behavior patterns
- Recommendations for staffing

**Use for**: Scheduling staff, planning maintenance windows

### Risk Analysis Report  
Navigate to: `/main_app/risk-analysis/`

Shows:
- High-risk users list with violation counts
- PCs needing maintenance with device removal rates
- Detected system anomalies with severity
- Risk mitigation recommendations

**Use for**: Disciplinary decisions, maintenance planning, troubleshooting

### Resource Demand Forecast
Navigate to: `/main_app/resource-demand/`

Shows:
- 14-day equipment needs
- Peak demand days
- Daily demand visualization
- Capacity planning guidelines

**Use for**: Equipment procurement, lab preparation, staffing

---

## 💡 Common Use Cases

### "How should I schedule this week's staff?"
1. Go to Booking Predictions
2. Look at "Peak Usage Days" and "Peak Usage Hours"
3. Schedule more staff during peak days/hours
4. Reduce staff during low-demand periods

### "Which users need disciplinary action?"
1. Go to Risk Analysis
2. Review "High Risk Users" list
3. Check their violation counts and types
4. Schedule one-on-one discussions
5. Document all actions

### "Which computers need maintenance?"
1. Go to Risk Analysis
2. Look at "PCs Requiring Maintenance"
3. Prioritize by maintenance priority level
4. Schedule during low-demand hours (see Booking Predictions)
5. Track maintenance history

### "Do we have enough devices for next week?"
1. Go to Resource Demand Forecast
2. Check "Total Devices Needed"
3. Compare to available inventory
4. Request additional resources if needed
5. Alert faculty of any limitations

### "Why are cancellations increasing?"
1. Go to Risk Analysis
2. Look for "high cancellation rate" anomaly
3. Check Booking Predictions for trends
4. Investigate possible causes:
   - System issues?
   - User satisfaction?
   - Scheduling problems?
5. Take corrective action

---

## 📊 Dashboard Controls

### Period Selection
Default: 30 days  
Options: 7, 14, 30, 60, 90 days

**Choose based on your needs:**
- 7 days: Recent trends only
- 30 days: Monthly overview (default)
- 60+ days: Longer-term patterns

### Mobile View
All dashboards are mobile-responsive. Access from:
- Desktop browser
- Tablet
- Smartphone

---

## 🔍 Interpreting the Data

### Trend Arrows
- 📈 **Increasing**: Demand/issues going up - prepare for more
- 📉 **Decreasing**: Demand/issues going down - watch for continued decline
- ➡️ **Stable**: Consistent demand - maintain current resources

### Color Coding
- 🟢 **Green**: Good/Low risk - normal operations
- 🟡 **Yellow**: Medium - monitor situation
- 🔴 **Red**: High risk/High demand - immediate action needed

### Severity Levels
- **HIGH (🔴)**: Urgent, requires immediate attention
- **MEDIUM (🟡)**: Important, should be addressed soon
- **LOW (🟢)**: Monitor, routine action needed

---

## 📋 Weekly Staff Checklist

Every Monday:
- [ ] Review Booking Predictions for the week
- [ ] Check Resource Demand for upcoming events
- [ ] Review Risk Analysis for high-risk users
- [ ] Check for any anomalies detected
- [ ] Plan staff schedule based on peak hours
- [ ] Identify maintenance tasks needed
- [ ] Update any pending disciplinary actions

---

## 🆘 Troubleshooting

### "No data appears"
- Ensure at least 4 weeks of data has been collected
- Check that records are being created in the system
- Verify your staff permissions

### "Predictions seem wrong"
- Need 8-12 weeks of data for accuracy
- Check if this is the first month (limited history)
- Look for unusual events that might skew data

### "Slow loading"
- Large datasets can take time to analyze
- Try shorter time period (7 vs 90 days)
- Check your internet connection
- Try refreshing the page

---

## 📞 Need Help?

For questions about:
- **Analytics interpretation**: Contact System Administrator
- **Technical issues**: Contact IT Support
- **Data accuracy**: Contact Development Team

---

## Key Takeaways

✅ Use analytics to **make data-driven decisions**  
✅ Review **peak predictions** for scheduling  
✅ Monitor **high-risk users** proactively  
✅ Plan **maintenance** during low-demand periods  
✅ **Forecast resources** for faculty bookings  
✅ **Investigate anomalies** when detected  
✅ Check reports **weekly** for best results  

---

*Last Updated: February 2026*  
*Version: 1.0*
