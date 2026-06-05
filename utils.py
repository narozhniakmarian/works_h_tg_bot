import holidays
from datetime import datetime, timedelta

def get_polish_holidays(year):
    return holidays.PL(years=year)

def is_work_day(date_obj):
    pl_holidays = get_polish_holidays(date_obj.year)
    if date_obj.weekday() >= 5:  # Saturday or Sunday
        return False
    if date_obj in pl_holidays:
        return False
    return True

def calculate_hours(input_val, shift_type):
    """
    input_val: str or int (1-16, 'u', 'up', 'l4')
    shift_type: int (1, 2, 3)
    Returns: (total_hours, night_hours, type_label, pay_multiplier)
    """
    input_str = str(input_val).lower().strip()
    
    total_hours = 0
    night_hours = 0
    type_label = "Work"
    pay_multiplier = 1.0
    
    if input_str == 'u':
        total_hours = 8
        night_hours = 0
        type_label = "Vacation"
        pay_multiplier = 1.0
    elif input_str == 'up':
        total_hours = 0
        night_hours = 0
        type_label = "Unpaid Vacation"
        pay_multiplier = 0.0
    elif input_str == 'l4':
        total_hours = 8
        night_hours = 0
        type_label = "Sick Leave"
        pay_multiplier = 0.8
    else:
        try:
            total_hours = float(input_str)
            if shift_type == 3:
                night_hours = 8 # Assuming full night shift
            else:
                night_hours = 0
        except ValueError:
            total_hours = 0
            
    return total_hours, night_hours, type_label, pay_multiplier

def get_report_summary(records):
    total_h = 0
    night_h = 0
    vacation_h = 0
    sick_h = 0
    weekend_h = 0
    
    # We'll need to parse records from GS
    # For now, this is a placeholder for the logic
    return {
        "total": total_h,
        "night": night_h,
        "vacation": vacation_h,
        "sick": sick_h,
        "weekend": weekend_h
    }
