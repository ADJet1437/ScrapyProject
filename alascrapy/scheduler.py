#!/usr/bin/env python
# -*- coding: utf-8 -*-

from alascrapy.lib.conf import get_project_conf
from scheduler.scheduler import Scheduler


def main():
    """ Scheduler scripts, reads from the database all
        schedules and determines if any spider should
        be executed at this time.
    """
    #path = dirname(realpath(__file__))
    project_conf = get_project_conf()
    scheduler = Scheduler(project_conf)
    scheduler.run_scheduler()

if __name__ == '__main__':
    main()
