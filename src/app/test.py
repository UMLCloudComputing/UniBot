import course

def getCourse(courseID):
    return course.get_course_name(course.get_html_response(course.get_course_url(courseID)))


print(getCourse("COMP.1020"))