from xmodule.modulestore.django import modulestore
from courseware import grades
from courseware.grades import MaxScoresCache, get_score
from django.db import transaction
from django.conf import settings

from openedx.core.djangoapps.signals.signals import GRADES_UPDATED
from courseware.model_data import FieldDataCache, ScoresClient
from courseware.module_render import get_module_for_descriptor
from util.module_utils import yield_dynamic_descriptor_descendants
from xmodule import graders
from xmodule.graders import Score
from student.models import anonymous_id_for_user
from courseware.access import has_access

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
        grade = calculate_grade(student, request, course)
        course_progress['student_grade'] = grade['percent']
        course_progress['course_lowest_passing_grade'] = course.lowest_passing_grade
        if grade['percent'] >= course.lowest_passing_grade:
            course_progress['pass'] = True
    except transaction.TransactionManagementError as e:
        log.error('There was an error calculating the grade of the student {0} in course {1}: {2}'.format(student, course_id, e))
        pass

    return course_progress


def calculate_grade(student, request, course, keep_raw_scores=False, field_data_cache=None, scores_client=None):
    """
    Returns the grade of the student.

    Also sends a signal to update the minimum grade requirement status.
    """
    grade_summary = _grade(student, request, course, keep_raw_scores, field_data_cache, scores_client)
    responses = GRADES_UPDATED.send_robust(
        sender=None,
        username=student.username,
        grade_summary=grade_summary,
        course_key=course.id,
        deadline=course.end
    )

    for receiver, response in responses:
        log.info('Signal fired when student grade is calculated. Receiver: %s. Response: %s', receiver, response)

    return grade_summary


def _grade(student, request, course, keep_raw_scores, field_data_cache, scores_client):
    """
    Unwrapped version of "grade"

    This grades a student as quickly as possible. It returns the
    output from the course grader, augmented with the final letter
    grade. The keys in the output are:

    course: a CourseDescriptor

    - grade : A final letter grade.
    - percent : The final percent for the class (rounded up).
    - section_breakdown : A breakdown of each section that makes
      up the grade. (For display)
    - grade_breakdown : A breakdown of the major components that
      make up the final grade. (For display)
    - keep_raw_scores : if True, then value for key 'raw_scores' contains scores
      for every graded module

    More information on the format is in the docstring for CourseGrader.
    """

    if field_data_cache is None:
        field_data_cache = grades.field_data_cache_for_grading(course, student)
    if scores_client is None:
        scores_client = ScoresClient.from_field_data_cache(field_data_cache)

    # Dict of item_ids -> (earned, possible) point tuples. This *only* grabs
    # scores that were registered with the submissions API, which for the moment
    # means only openassessment (edx-ora2)
    # We need to import this here to avoid a circular dependency of the form:
    # XBlock --> submissions --> Django Rest Framework error strings -->
    # Django translation --> ... --> courseware --> submissions
    from submissions import api as sub_api  # installed from the edx-submissions repository

    submissions_scores = sub_api.get_scores(
        course.id.to_deprecated_string(),
        anonymous_id_for_user(student, course.id)
    )
    max_scores_cache = MaxScoresCache.create_for_course(course)

    # For the moment, we have to get scorable_locations from field_data_cache
    # and not from scores_client, because scores_client is ignorant of things
    # in the submissions API. As a further refactoring step, submissions should
    # be hidden behind the ScoresClient.
    max_scores_cache.fetch_from_remote(field_data_cache.scorable_locations)

    grading_context = course.grading_context
    raw_scores = []

    totaled_scores = {}
    # This next complicated loop is just to collect the totaled_scores, which is
    # passed to the grader
    for section_format, sections in grading_context['graded_sections'].iteritems():
        format_scores = []
        for section in sections:
            section_descriptor = section['section_descriptor']
            section_name = section_descriptor.display_name_with_default

            # some problems have state that is updated independently of interaction
            # with the LMS, so they need to always be scored. (E.g. combinedopenended ORA1)
            # TODO This block is causing extra savepoints to be fired that are empty because no queries are executed
            # during the loop. When refactoring this code please keep this outer_atomic call in mind and ensure we
            # are not making unnecessary database queries.
            should_grade_section = any(
                descriptor.always_recalculate_grades for descriptor in section['xmoduledescriptors']
            )

            # If there are no problems that always have to be regraded, check to
            # see if any of our locations are in the scores from the submissions
            # API. If scores exist, we have to calculate grades for this section.
            if not should_grade_section:
                should_grade_section = any(
                    descriptor.location.to_deprecated_string() in submissions_scores
                    for descriptor in section['xmoduledescriptors']
                )

            if not should_grade_section:
                should_grade_section = any(
                    descriptor.location in scores_client
                    for descriptor in section['xmoduledescriptors']
                )

            # If we haven't seen a single problem in the section, we don't have
            # to grade it at all! We can assume 0%
            if should_grade_section:
                scores = []

                def create_module(descriptor):
                    '''creates an XModule instance given a descriptor'''
                    # TODO: We need the request to pass into here. If we could forego that, our arguments
                    # would be simpler
                    return get_module_for_descriptor(
                        student, request, descriptor, field_data_cache, course.id, course=course
                    )

                descendants = yield_dynamic_descriptor_descendants(section_descriptor, student.id, create_module)
                for module_descriptor in descendants:
                    user_access = has_access(
                        student, 'load', module_descriptor, module_descriptor.location.course_key
                    )
                    if not user_access:
                        continue

                    (correct, total) = get_score(
                        student,
                        module_descriptor,
                        create_module,
                        scores_client,
                        submissions_scores,
                        max_scores_cache,
                    )
                    if correct is None and total is None:
                        continue

                    if settings.GENERATE_PROFILE_SCORES:    # for debugging!
                        if total > 1:
                            correct = random.randrange(max(total - 2, 1), total + 1)
                        else:
                            correct = total

                    graded = module_descriptor.graded
                    if not total > 0:
                        # We simply cannot grade a problem that is 12/0, because we might need it as a percentage
                        graded = False

                    scores.append(
                        Score(
                            correct,
                            total,
                            graded,
                            module_descriptor.display_name_with_default,
                            module_descriptor.location
                        )
                    )

                __, graded_total = graders.aggregate_scores(scores, section_name)
                if keep_raw_scores:
                    raw_scores += scores


            else:
                graded_total = Score(0.0, 1.0, True, section_name, None)

            #Add the graded total to totaled_scores
            if graded_total.possible > 0:
                format_scores.append(graded_total)
            else:
                log.info(
                    "Unable to grade a section with a total possible score of zero. " +
                    str(section_descriptor.location)
                )

        totaled_scores[section_format] = format_scores

    # Grading policy might be overriden by a CCX, need to reset it
    course.set_grading_policy(course.grading_policy)
    grade_summary = course.grader.grade(totaled_scores, generate_random_scores=settings.GENERATE_PROFILE_SCORES)

    # We round the grade here, to make sure that the grade is an whole percentage and
    # doesn't get displayed differently than it gets grades
    grade_summary['percent'] = round(grade_summary['percent'] * 100 + 0.05) / 100

    letter_grade = grades.grade_for_percentage(course.grade_cutoffs, grade_summary['percent'])
    grade_summary['grade'] = letter_grade
    grade_summary['totaled_scores'] = totaled_scores   # make this available, eg for instructor download & debugging
    if keep_raw_scores:
        # way to get all RAW scores out to instructor
        # so grader can be double-checked
        grade_summary['raw_scores'] = raw_scores

    max_scores_cache.push_to_remote()

    return grade_summary

