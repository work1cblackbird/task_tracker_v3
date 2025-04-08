# -*- coding: utf-8 -*-
"""
Модуль для фильтрации задач по различным параметрам
"""

from datetime import datetime, timedelta
from config import TaskStatuses, CalendarConfig

class TaskFilter:
    """Класс для фильтрации списка задач"""

    @staticmethod
    def filter_by_status(tasks, status):
        """
        Фильтрация задач по статусу
        :param tasks: Список задач из БД
        :param status: Статус для фильтрации (из TaskStatuses)
        :return: Отфильтрованный список задач
        """
        if status.lower() == 'all':
            return tasks
        return [task for task in tasks if task[2] == status]

    @staticmethod
    def filter_by_period(tasks, period):
        """
        Фильтрация задач по временному периоду
        :param tasks: Список задач из БД
        :param period: Период для фильтрации (сегодня/неделя/месяц/все)
        :return: Отфильтрованный список задач
        """
        if period == 'all':
            return tasks

        now = datetime.now()
        date_format = CalendarConfig.DATE_FORMAT

        if period == 'today':
            today_str = now.strftime(date_format)
            return [task for task in tasks 
                   if datetime.strptime(task[4], date_format).date() == now.date()]

        elif period == 'week':
            week_start = now - timedelta(days=now.weekday())
            week_end = week_start + timedelta(days=6)
            return [task for task in tasks 
                   if week_start.date() <= datetime.strptime(task[4], date_format).date() <= week_end.date()]

        elif period == 'month':
            month_start = datetime(now.year, now.month, 1)
            month_end = datetime(now.year, now.month + 1, 1) - timedelta(days=1)
            return [task for task in tasks 
                   if month_start.date() <= datetime.strptime(task[4], date_format).date() <= month_end.date()]

        return tasks

    @staticmethod
    def filter_by_custom_date(tasks, start_date, end_date):
        """
        Фильтрация задач по произвольному периоду
        :param tasks: Список задач из БД
        :param start_date: Начальная дата (str в формате CalendarConfig.DATE_FORMAT)
        :param end_date: Конечная дата (str в формате CalendarConfig.DATE_FORMAT)
        :return: Отфильтрованный список задач
        """
        date_format = CalendarConfig.DATE_FORMAT
        try:
            start = datetime.strptime(start_date, date_format).date()
            end = datetime.strptime(end_date, date_format).date()
            
            return [task for task in tasks 
                   if start <= datetime.strptime(task[4], date_format).date() <= end]
        except ValueError:
            return tasks

    @staticmethod
    def filter_by_author(tasks, username):
        """
        Фильтрация задач по автору
        :param tasks: Список задач из БД
        :param username: Имя пользователя (без @)
        :return: Отфильтрованный список задач
        """
        return [task for task in tasks if task[3] == username]

    @staticmethod
    def apply_filters(tasks, status_filter=None, period_filter=None, 
                    author_filter=None, custom_dates=None):
        """
        Применение нескольких фильтров одновременно
        :param tasks: Исходный список задач
        :param status_filter: Фильтр по статусу
        :param period_filter: Фильтр по периоду (сегодня/неделя/месяц)
        :param author_filter: Фильтр по автору
        :param custom_dates: Кортеж (start_date, end_date) для произвольного периода
        :return: Отфильтрованный список задач
        """
        filtered_tasks = tasks
        
        if status_filter:
            filtered_tasks = TaskFilter.filter_by_status(filtered_tasks, status_filter)
            
        if period_filter:
            filtered_tasks = TaskFilter.filter_by_period(filtered_tasks, period_filter)
            
        if custom_dates:
            start_date, end_date = custom_dates
            filtered_tasks = TaskFilter.filter_by_custom_date(
                filtered_tasks, start_date, end_date)
                
        if author_filter:
            filtered_tasks = TaskFilter.filter_by_author(filtered_tasks, author_filter)
            
        return filtered_tasks