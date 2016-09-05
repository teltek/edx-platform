from xmodule.modulestore.django import modulestore
from courseware import grades
from django.db import transaction

import logging

log = logging.getLogger(__name__)

def get_courses_progress(request, course_enrollments):
    """
    Builds a dict with the list of courses given the student grade,
    the course lowest passing grade and if the student passes the course.

    Args:
        request (Request): the request that has called this function
        course_enrollments (list[CourseEnrollment]): a list of course enrollments.

    Returns:
        A dictionary with the student grade, the course lowest passing grade
        and if the student passes the course per course enrollment of the student.
    """
    courses_progress = dict()
    for enrollment in course_enrollments:
        courses_progress[enrollment.course_id] = get_course_progress(request, request.user, enrollment.course_id)
    return courses_progress


def get_course_progress(request, student, course_id):
    """
    Gives a dict with the student grade on a course,
    the course lowest passing grade and if the student passes the course.

    Args:
        request (Request): the request that has called this function
        student (User): the user to grade
        course_id (CourseKey): the course id to grade

    Returns:
        A dictionary with the student grade, the course lowest passing grade
        and if the student passes the course per course enrollment of the student.
    """
    course_progress = dict()
    course = modulestore().get_course(course_id, depth=0)
    course_progress = {
        'student_grade': 0.0,
        'course_lowest_passing_grade': 1.0,
        'pass': False
        }
    try:
        grade = grades.grade(student, request, course)
        course_progress['student_grade'] = grade['percent']
        course_progress['course_lowest_passing_grade'] = course.lowest_passing_grade
        if grade['percent'] >= course.lowest_passing_grade:
            course_progress['pass'] = True
    except transaction.TransactionManagementError as e:
        log.error('There was an error calculating the grade of the student {0} in course {1}: {2}'.format(student, course_id, e))
        pass

    return course_progress

