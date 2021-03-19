def check_list_contains_objects_of_type(obj_list, count, searched_type):
    c = 0
    for obj in obj_list:
        if searched_type is None:
            if obj is None:
                c += 1
        else:
            if type(obj) == searched_type:
                c += 1
    assert c == count, f"Found {c} {searched_type} objects, but expected {count}!"
