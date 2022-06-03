def form_html_validated(POST_dict):

    for index in POST_dict:
        if not POST_dict[index]:
            return False
    return True
