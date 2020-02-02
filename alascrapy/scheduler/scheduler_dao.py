# -*- coding: utf-8 -*-

def get_schedules(mysql_manager):
    schedules = mysql_manager.execute_select(
        """SELECT id,
                  spider_name,
                  hours,
                  days_of_week,
                  days_of_month,
                  months
           FROM feed_in_conf.alascrapy_schedules
           WHERE enabled=True""")
    if schedules:
        return schedules
    return []

def get_schedule_params(mysql_manager, schedule_id):
    args = [schedule_id]
    params = mysql_manager.execute_select(
        """SELECT parameter,
                  parameter_value
           FROM feed_in_conf.alascrapy_run_params
           WHERE schedule_id=%s""", args )
    if params:
        return params
    return []

