import pandas as pd
import re
from datetime import datetime, timedelta
from collections import defaultdict

def is_valid_email(email):
    if not email:
        return False
    if '@' not in email:
        return False
    parts = email.split('@')
    if len(parts) != 2:
        return False
    local_part = parts[0]
    domain_part = parts[1]
    if not domain_part.endswith(".com"):
        return False
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", local_part):
        return False
    return True

def find_latest_consecutive_absences(attendance_data):
    student_absences = defaultdict(list)
    for record in attendance_data:
        if record['status'] == 'Absent':
            student_absences[record['student_id']].append(datetime.strptime(record['attendance_date'], '%Y-%m-%d').date())

    result = []
    for student_id, absent_dates in student_absences.items():
        if not absent_dates:
            continue

        absent_dates.sort()
        latest_long_streak = None
        current_streak_start = None
        current_streak_end = None
        current_streak_length = 0

        for i in range(len(absent_dates)):
            if current_streak_start is None:
                current_streak_start = absent_dates[i]
                current_streak_end = absent_dates[i]
                current_streak_length = 1
            elif absent_dates[i] == current_streak_end + timedelta(days=1):
                current_streak_end = absent_dates[i]
                current_streak_length += 1
            else:
                if current_streak_length > 3:
                    if latest_long_streak is None or current_streak_end > latest_long_streak['absence_end_date']:
                        latest_long_streak = {
                            'student_id': student_id,
                            'absence_start_date': current_streak_start,
                            'absence_end_date': current_streak_end,
                            'total_absent_days': current_streak_length
                        }
                current_streak_start = absent_dates[i]
                current_streak_end = absent_dates[i]
                current_streak_length = 1
        if current_streak_length > 3:
            if latest_long_streak is None or current_streak_end > latest_long_streak['absence_end_date']:
                latest_long_streak = {
                    'student_id': student_id,
                    'absence_start_date': current_streak_start,
                    'absence_end_date': current_streak_end,
                    'total_absent_days': current_streak_length
                }

        if latest_long_streak:
            result.append(latest_long_streak)

    return result

def run():
    attendance_data = [
        {'student_id': 101, 'attendance_date': '2024-03-01', 'status': 'Absent'},
        {'student_id': 101, 'attendance_date': '2024-03-02', 'status': 'Absent'},
        {'student_id': 101, 'attendance_date': '2024-03-03', 'status': 'Absent'},
        {'student_id': 101, 'attendance_date': '2024-03-04', 'status': 'Absent'},
        {'student_id': 101, 'attendance_date': '2024-03-05', 'status': 'Present'},
        {'student_id': 102, 'attendance_date': '2024-03-02', 'status': 'Absent'},
        {'student_id': 102, 'attendance_date': '2024-03-03', 'status': 'Absent'},
        {'student_id': 102, 'attendance_date': '2024-03-04', 'status': 'Absent'},
        {'student_id': 102, 'attendance_date': '2024-03-05', 'status': 'Absent'},
        {'student_id': 103, 'attendance_date': '2024-03-05', 'status': 'Absent'},
        {'student_id': 103, 'attendance_date': '2024-03-06', 'status': 'Absent'},
        {'student_id': 103, 'attendance_date': '2024-03-07', 'status': 'Absent'},
        {'student_id': 103, 'attendance_date': '2024-03-08', 'status': 'Absent'},
        {'student_id': 103, 'attendance_date': '2024-03-09', 'status': 'Absent'},
        {'student_id': 104, 'attendance_date': '2024-03-01', 'status': 'Present'},
        {'student_id': 104, 'attendance_date': '2024-03-02', 'status': 'Present'},
        {'student_id': 104, 'attendance_date': '2024-03-03', 'status': 'Absent'},
        {'student_id': 104, 'attendance_date': '2024-03-04', 'status': 'Present'},
        {'student_id': 104, 'attendance_date': '2024-03-05', 'status': 'Present'},
    ]

    students_data = {
        'student_id': [101, 102, 103, 104, 105],
        'student_name': ['Alice Johnson', 'Bob Smith', 'Charlie Brown', 'David Lee', 'Eva White'],
        'parent_email': ['alice_parent@example.com', 'bob_parent@example.com', 'invalid_email.com', 'invalid_email.com', 'eva_white@example.com']
    }
    absence_output = find_latest_consecutive_absences(attendance_data)
    absence_df = pd.DataFrame(absence_output)
    students_df = pd.DataFrame(students_data)
    final_df = pd.merge(absence_df, students_df, on='student_id', how='left')

    final_df['email'] = final_df['parent_email'].apply(lambda x: x if is_valid_email(x) else None)
    def generate_message(row):
        if pd.notna(row['email']):
            return (
                f"Dear Parent, your child {row['student_name']} was absent from "
                f"{row['absence_start_date']} to {row['absence_end_date']} for "
                f"{row['total_absent_days']} days. Please ensure their attendance improves."
            )
        return None
    final_df['msg'] = final_df.apply(generate_message, axis=1)
    final_df = final_df[['student_id', 'absence_start_date', 'absence_end_date', 'total_absent_days', 'email', 'msg']]
    return final_df
if __name__ == "__main__":
    output_df = run()
    print(output_df.to_string())