"""
Analytics module for PCheck system with descriptive and predictive analytics.
Provides insights into PC usage, violations, bookings, and system performance.
"""

from django.db.models import Count, Q, Avg, Sum, F
from django.utils import timezone
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import statistics
from .models import Booking, Violation, PeripheralEvent, PC, User, FacultyBooking


class DescriptiveAnalytics:
    """Descriptive analytics - what happened and is currently happening"""
    
    @staticmethod
    def get_booking_statistics(start_date=None, end_date=None):
        """Get booking statistics for a given period"""
        if not start_date:
            start_date = timezone.now() - timedelta(days=30)
        if not end_date:
            end_date = timezone.now()
        
        bookings = Booking.objects.filter(created_at__gte=start_date, created_at__lte=end_date)
        
        stats = {
            'total_bookings': bookings.count(),
            'confirmed_bookings': bookings.filter(status='confirmed').count(),
            'cancelled_bookings': bookings.filter(status='cancelled').count(),
            'avg_duration_minutes': None,
            'total_pc_hours': 0,
            'bookings_by_college': {},
            'bookings_by_user': bookings.values('user__username').annotate(count=Count('id')).order_by('-count')[:10],
        }
        
        # Calculate average duration
        durations = bookings.filter(duration__isnull=False).values_list('duration', flat=True)
        if durations:
            avg_seconds = sum(d.total_seconds() for d in durations) / len(durations)
            stats['avg_duration_minutes'] = round(avg_seconds / 60, 2)
            stats['total_pc_hours'] = sum(d.total_seconds() for d in durations) / 3600
        
        # Bookings by college
        college_bookings = bookings.filter(user__profile__college__isnull=False).values(
            'user__profile__college__name'
        ).annotate(count=Count('id')).order_by('-count')
        stats['bookings_by_college'] = {b['user__profile__college__name']: b['count'] for b in college_bookings}
        
        return stats
    
    @staticmethod
    def get_pc_utilization():
        """Get PC utilization metrics"""
        pcs = PC.objects.all()
        bookings = Booking.objects.filter(status='confirmed', end_time__gte=timezone.now() - timedelta(days=30))
        
        utilization = {
            'total_pcs': pcs.count(),
            'active_pcs': pcs.filter(system_condition='active', status='connected').count(),
            'in_repair': pcs.filter(system_condition='repair').count(),
            'disconnected': pcs.filter(status='disconnected').count(),
            'available': pcs.filter(booking_status='available', system_condition='active', status='connected').count(),
            'in_use': pcs.filter(booking_status='in_use').count(),
            'in_queue': pcs.filter(booking_status='in_queue').count(),
        }
        
        # Calculate average utilization percentage
        if bookings.exists():
            utilization['avg_utilization_percent'] = round(
                (utilization['active_pcs'] / max(utilization['total_pcs'], 1)) * 100, 2
            )
        else:
            utilization['avg_utilization_percent'] = 0
        
        return utilization
    
    @staticmethod
    def get_violation_statistics(start_date=None, end_date=None):
        """Get violation statistics"""
        if not start_date:
            start_date = timezone.now() - timedelta(days=30)
        if not end_date:
            end_date = timezone.now()
        
        violations = Violation.objects.filter(timestamp__gte=start_date, timestamp__lte=end_date)
        
        stats = {
            'total_violations': violations.count(),
            'resolved_violations': violations.filter(resolved=True).count(),
            'unresolved_violations': violations.filter(resolved=False).count(),
            'violations_by_level': {
                'minor': violations.filter(level='minor').count(),
                'moderate': violations.filter(level='moderate').count(),
                'major': violations.filter(level='major').count(),
            },
            'violations_by_reason': {},
            'repeat_offenders': violations.values('user__username').annotate(
                count=Count('id')
            ).filter(count__gt=1).order_by('-count')[:10],
            'suspended_users': violations.filter(status='suspended').values('user__username').distinct().count(),
        }
        
        # Violations by reason
        reason_violations = violations.values('reason').annotate(count=Count('id')).order_by('-count')[:10]
        stats['violations_by_reason'] = {v['reason']: v['count'] for v in reason_violations}
        
        return stats
    
    @staticmethod
    def get_faculty_booking_statistics(start_date=None, end_date=None):
        """Get faculty booking statistics"""
        if not start_date:
            start_date = timezone.now() - timedelta(days=30)
        if not end_date:
            end_date = timezone.now()
        
        faculty_bookings = FacultyBooking.objects.filter(created_at__gte=start_date, created_at__lte=end_date)
        
        stats = {
            'total_faculty_bookings': faculty_bookings.count(),
            'confirmed': faculty_bookings.filter(status='confirmed').count(),
            'pending': faculty_bookings.filter(status='pending').count(),
            'cancelled': faculty_bookings.filter(status='cancelled').count(),
            'total_devices_requested': faculty_bookings.aggregate(Sum('num_of_devices'))['num_of_devices__sum'] or 0,
            'avg_devices_per_booking': None,
            'bookings_by_college': {},
        }
        
        # Average devices per booking
        if faculty_bookings.exists():
            stats['avg_devices_per_booking'] = round(
                statistics.mean(faculty_bookings.values_list('num_of_devices', flat=True)), 2
            )
        
        # Bookings by college
        college_bookings = faculty_bookings.values('college__name').annotate(
            count=Count('id')
        ).order_by('-count')
        stats['bookings_by_college'] = {b['college__name']: b['count'] for b in college_bookings if b['college__name']}
        
        return stats
    
    @staticmethod
    def get_peripheral_events_summary(start_date=None, end_date=None):
        """Get summary of peripheral device events"""
        if not start_date:
            start_date = timezone.now() - timedelta(days=30)
        if not end_date:
            end_date = timezone.now()
        
        events = PeripheralEvent.objects.filter(created_at__gte=start_date, created_at__lte=end_date)
        
        stats = {
            'total_events': events.count(),
            'devices_attached': events.filter(action='attached').count(),
            'devices_removed': events.filter(action='removed').count(),
            'most_affected_pcs': events.values('pc__name').annotate(
                count=Count('id')
            ).order_by('-count')[:10],
            'most_common_devices': events.values('device_name').annotate(
                count=Count('id')
            ).order_by('-count')[:10],
        }
        
        return stats


class PredictiveAnalytics:
    """Predictive analytics - forecasting future trends and anomalies"""
    
    @staticmethod
    def predict_peak_usage_hours():
        """Predict peak PC usage hours based on historical data"""
        bookings = Booking.objects.filter(
            start_time__isnull=False,
            status='confirmed',
            created_at__gte=timezone.now() - timedelta(days=60)
        )
        
        hour_usage = defaultdict(int)
        for booking in bookings:
            hour = booking.start_time.hour
            hour_usage[hour] += 1
        
        if not hour_usage:
            return {'peak_hours': [], 'hourly_distribution': {}}
        
        # Find peak hours (top 5)
        peak_hours = sorted(hour_usage.items(), key=lambda x: x[1], reverse=True)[:5]
        peak_hours = [{'hour': h[0], 'usage_count': h[1]} for h in peak_hours]
        
        return {
            'peak_hours': peak_hours,
            'hourly_distribution': dict(sorted(hour_usage.items())),
        }
    
    @staticmethod
    def predict_peak_usage_days():
        """Predict peak PC usage days of the week"""
        bookings = Booking.objects.filter(
            start_time__isnull=False,
            status='confirmed',
            created_at__gte=timezone.now() - timedelta(days=90)
        )
        
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        day_usage = defaultdict(int)
        
        for booking in bookings:
            day = booking.start_time.weekday()
            day_usage[day] += 1
        
        if not day_usage:
            return {'peak_days': [], 'daily_distribution': {}}
        
        daily_dist = {day_names[i]: day_usage.get(i, 0) for i in range(7)}
        peak_days = sorted(day_usage.items(), key=lambda x: x[1], reverse=True)[:3]
        peak_days = [{'day': day_names[d[0]], 'usage_count': d[1]} for d in peak_days]
        
        return {
            'peak_days': peak_days,
            'daily_distribution': daily_dist,
        }
    
    @staticmethod
    def predict_user_violation_risk():
        """Identify users at high risk of violations based on patterns"""
        violations = Violation.objects.filter(
            timestamp__gte=timezone.now() - timedelta(days=90)
        )
        
        user_violations = violations.values('user__id', 'user__username', 'user__first_name', 'user__last_name').annotate(
            violation_count=Count('id'),
            major_count=Count('id', filter=Q(level='major')),
            moderate_count=Count('id', filter=Q(level='moderate')),
        ).order_by('-violation_count')[:20]
        
        risk_users = []
        for user in user_violations:
            # Calculate risk score (higher is more risk)
            risk_score = (user['violation_count'] * 2) + (user['major_count'] * 3) + (user['moderate_count'] * 1.5)
            risk_level = 'low'
            
            if risk_score >= 10:
                risk_level = 'high'
            elif risk_score >= 5:
                risk_level = 'medium'
            
            risk_users.append({
                'user_id': user['user__id'],
                'username': user['user__username'],
                'full_name': f"{user['user__first_name']} {user['user__last_name']}",
                'violation_count': user['violation_count'],
                'major_violations': user['major_count'],
                'moderate_violations': user['moderate_count'],
                'risk_score': round(risk_score, 2),
                'risk_level': risk_level,
            })
        
        return {'high_risk_users': risk_users}
    
    @staticmethod
    def predict_pc_maintenance_needs():
        """Predict which PCs likely need maintenance based on event frequency"""
        events = PeripheralEvent.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=60)
        )
        
        pc_events = events.values('pc__id', 'pc__name').annotate(
            event_count=Count('id'),
            removed_count=Count('id', filter=Q(action='removed')),
        ).order_by('-removed_count')
        
        maintenance_needs = []
        for pc in pc_events:
            # High removal rate suggests hardware issues
            if pc['removed_count'] > pc['event_count'] * 0.5:
                priority = 'high'
            elif pc['removed_count'] > pc['event_count'] * 0.3:
                priority = 'medium'
            else:
                priority = 'low'
            
            maintenance_needs.append({
                'pc_id': pc['pc__id'],
                'pc_name': pc['pc__name'],
                'event_count': pc['event_count'],
                'device_removal_count': pc['removed_count'],
                'removal_rate': round(pc['removed_count'] / pc['event_count'] * 100, 2),
                'maintenance_priority': priority,
            })
        
        return {'pcs_needing_maintenance': maintenance_needs}
    
    @staticmethod
    def predict_booking_trends():
        """Predict future booking trends based on historical patterns"""
        bookings = Booking.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=90)
        )
        
        # Group by week
        weekly_bookings = defaultdict(int)
        for booking in bookings:
            week = booking.created_at.isocalendar()[1]
            weekly_bookings[week] += 1
        
        if len(weekly_bookings) < 2:
            return {'trend': 'insufficient_data', 'prediction': None}
        
        weeks = sorted(weekly_bookings.keys())
        values = [weekly_bookings[w] for w in weeks]
        
        # Simple trend analysis
        recent_avg = statistics.mean(values[-4:]) if len(values) >= 4 else statistics.mean(values)
        older_avg = statistics.mean(values[:len(values)//2]) if len(values) >= 4 else recent_avg
        
        trend = 'stable'
        if recent_avg > older_avg * 1.1:
            trend = 'increasing'
        elif recent_avg < older_avg * 0.9:
            trend = 'decreasing'
        
        # Forecast next week
        if len(values) >= 2:
            predicted_next_week = int(statistics.mean(values[-4:]))
        else:
            predicted_next_week = int(recent_avg)
        
        return {
            'trend': trend,
            'current_weekly_average': int(recent_avg),
            'predicted_next_week_bookings': predicted_next_week,
            'historical_data_points': len(weeks),
        }
    
    @staticmethod
    def predict_resource_demand():
        """Predict future resource demand (devices needed for faculty bookings)"""
        faculty_bookings = FacultyBooking.objects.filter(
            start_datetime__gte=timezone.now(),
            status__in=['pending', 'confirmed']
        )
        
        # Group by day
        daily_demand = defaultdict(int)
        for booking in faculty_bookings:
            day = booking.start_datetime.date()
            daily_demand[day] += booking.num_of_devices
        
        upcoming_demand = []
        for day in sorted(daily_demand.keys())[:14]:  # Next 14 days
            upcoming_demand.append({
                'date': day.isoformat(),
                'devices_needed': daily_demand[day],
                'day_of_week': day.strftime('%A'),
            })
        
        total_needed = sum(d['devices_needed'] for d in upcoming_demand)
        
        return {
            'upcoming_resource_demand': upcoming_demand,
            'total_devices_needed_next_2weeks': total_needed,
            'peak_demand_day': max(upcoming_demand, key=lambda x: x['devices_needed']) if upcoming_demand else None,
        }
    
    @staticmethod
    def predict_user_behavior_change():
        """Predict changes in user booking behavior"""
        # Get current month bookings
        current_month_start = timezone.now().replace(day=1)
        current_month_bookings = Booking.objects.filter(
            created_at__gte=current_month_start,
            status='confirmed'
        ).count()
        
        # Get last month bookings
        last_month_end = current_month_start - timedelta(days=1)
        last_month_start = last_month_end.replace(day=1)
        last_month_bookings = Booking.objects.filter(
            created_at__gte=last_month_start,
            created_at__lte=last_month_end,
            status='confirmed'
        ).count()
        
        change_percent = 0
        if last_month_bookings > 0:
            change_percent = round(((current_month_bookings - last_month_bookings) / last_month_bookings) * 100, 2)
        
        trend = 'stable'
        if change_percent > 10:
            trend = 'increasing'
        elif change_percent < -10:
            trend = 'decreasing'
        
        return {
            'current_month_bookings': current_month_bookings,
            'last_month_bookings': last_month_bookings,
            'change_percent': change_percent,
            'behavior_trend': trend,
        }
    
    @staticmethod
    def anomaly_detection():
        """Detect anomalies in system usage"""
        anomalies = []
        
        # Check for unusual booking cancellation rate
        recent_bookings = Booking.objects.filter(created_at__gte=timezone.now() - timedelta(days=7))
        if recent_bookings.exists():
            cancellation_rate = recent_bookings.filter(status='cancelled').count() / recent_bookings.count()
            if cancellation_rate > 0.3:
                anomalies.append({
                    'type': 'high_cancellation_rate',
                    'severity': 'medium',
                    'description': f'Unusually high booking cancellation rate: {cancellation_rate*100:.1f}%',
                    'value': round(cancellation_rate * 100, 2),
                })
        
        # Check for PC with excessive events
        excessive_events = PeripheralEvent.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).values('pc__name').annotate(count=Count('id')).filter(count__gt=20)
        
        for event in excessive_events:
            anomalies.append({
                'type': 'excessive_peripheral_events',
                'severity': 'high',
                'pc_name': event['pc__name'],
                'description': f"PC '{event['pc__name']}' has {event['count']} peripheral events in 7 days",
                'event_count': event['count'],
            })
        
        # Check for user with sudden violation spike
        recent_violations = Violation.objects.filter(timestamp__gte=timezone.now() - timedelta(days=7))
        user_violation_spike = recent_violations.values('user__username').annotate(
            count=Count('id')
        ).filter(count__gte=5)
        
        for user in user_violation_spike:
            anomalies.append({
                'type': 'violation_spike',
                'severity': 'high',
                'username': user['user__username'],
                'description': f"User '{user['user__username']}' has {user['count']} violations in 7 days",
                'violation_count': user['count'],
            })
        
        return {'detected_anomalies': anomalies}


class AnalyticsSummary:
    """Comprehensive analytics summary combining descriptive and predictive insights"""
    
    @staticmethod
    def get_comprehensive_report(days=30):
        """Get a comprehensive analytics report"""
        start_date = timezone.now() - timedelta(days=days)
        end_date = timezone.now()
        
        report = {
            'report_date': timezone.now().isoformat(),
            'period_days': days,
            
            # Descriptive Analytics
            'descriptive': {
                'bookings': DescriptiveAnalytics.get_booking_statistics(start_date, end_date),
                'pc_utilization': DescriptiveAnalytics.get_pc_utilization(),
                'violations': DescriptiveAnalytics.get_violation_statistics(start_date, end_date),
                'faculty_bookings': DescriptiveAnalytics.get_faculty_booking_statistics(start_date, end_date),
                'peripheral_events': DescriptiveAnalytics.get_peripheral_events_summary(start_date, end_date),
            },
            
            # Predictive Analytics
            'predictive': {
                'peak_usage_hours': PredictiveAnalytics.predict_peak_usage_hours(),
                'peak_usage_days': PredictiveAnalytics.predict_peak_usage_days(),
                'user_violation_risks': PredictiveAnalytics.predict_user_violation_risk(),
                'pc_maintenance_needs': PredictiveAnalytics.predict_pc_maintenance_needs(),
                'booking_trends': PredictiveAnalytics.predict_booking_trends(),
                'resource_demand': PredictiveAnalytics.predict_resource_demand(),
                'user_behavior_changes': PredictiveAnalytics.predict_user_behavior_change(),
                'anomalies': PredictiveAnalytics.anomaly_detection(),
            },
        }
        
        return report
