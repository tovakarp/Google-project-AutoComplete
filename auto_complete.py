import json
from init_data import simplify_word
from auto_complete_data import AutoCompleteData
from string import ascii_lowercase


def merge_two_list(list1, list2):
    if not list1:
        return list2
    elif not list2:
        return list1
    elif list1[0].score < list2[0].score:
        return [list2[0]] + merge_two_list(list1, list2[1:])
    else:
        return [list1[0]] + merge_two_list(list1[1:], list2)


def merge_three_lists(list_1, list_2, list_3):
    return merge_two_list(merge_two_list(list_1, list_2), list_3)


def calculate_omit_add_score(prefix_len, index):
    score = {1: 10, 2: 8, 3: 6, 4: 4}
    try:
        return 2 * prefix_len - score[index]
    except:
        return 2 * prefix_len - 2


def calculate_replace_score(prefix_len, index):
    score = {1: 5, 2: 4, 3: 3, 4: 2}
    try:
        return 2 * prefix_len - score[index]
    except:
        return 2 * prefix_len - 1


# TODO: divide omit_character, add_character and replace_character funcs


def omit_character(data_dict, prefix, length, completion_list):
    reversed_prefix = prefix[::-1]
    list = []
    no_dup_list = [[x.source_text, x.offset] for x in completion_list]

    for i in range(len(prefix)):
        try:
            path_list = data_dict[(reversed_prefix[:i] + reversed_prefix[i + 1:])[::-1]]
            score = calculate_omit_add_score(len(prefix) - 1, len(prefix) - i)

            for sentence in path_list:
                if [sentence[0], sentence[1]] not in no_dup_list:
                    list.append(AutoCompleteData(sentence[0], sentence[1], score))
                    no_dup_list.append([sentence[0], sentence[1]])
                    if len(list) == length:
                        return list
        except:
            continue
    return list


def add_character(data_dict, prefix, length, completion_list):
    reversed_prefix = prefix[::-1]
    list = []
    no_dup_list = [[x.source_text, x.offset] for x in completion_list]

    for i in range(len(prefix)):
        for char in ascii_lowercase:
            try:
                path_list = data_dict[(reversed_prefix[:i] + char + reversed_prefix[i:])[::-1]]
                score = calculate_omit_add_score(len(prefix), len(prefix) - i + 1)

                for sentence in path_list:
                    if [sentence[0], sentence[1]] not in no_dup_list:
                        list.append(AutoCompleteData(sentence[0], sentence[1], score))
                        no_dup_list.append([sentence[0], sentence[1]])
                        if len(list) == length:
                            return list
            except:
                continue
    return list


def replace_character(data_dict, prefix, length, completion_list):
    reversed_prefix = prefix[::-1]
    list = []
    no_dup_list = [[x.source_text, x.offset] for x in completion_list]
    for i in range(len(prefix)):
        for char in ascii_lowercase:
            try:
                path_list = data_dict[(reversed_prefix[:i] + char + reversed_prefix[i + 1:])[::-1]]
                score = calculate_replace_score(len(prefix) - 1, len(prefix) - i)

                for sentence in path_list:
                    if [sentence[0], sentence[1]] not in no_dup_list:
                        list.append(AutoCompleteData(sentence[0], sentence[1], score))
                        no_dup_list.append([sentence[0], sentence[1]])
                        if len(list) == length:
                            return list
            except:
                continue
    return list


def get_all_similar_completions(data_dic, prefix, length, completion_list):
    omit_completions = omit_character(data_dic, prefix, length, completion_list)
    add_completions = add_character(data_dic, prefix, length, completion_list)
    replace_completions = replace_character(data_dic, prefix, length, completion_list)

    return merge_three_lists(omit_completions, add_completions, replace_completions)


def filter_best_similar_completions(list):
    list_length = len(list) - 1
    no_dup_list = [[x.source_text, x.offset] for x in list][::-1]
    for i, obj in enumerate(no_dup_list):
        if no_dup_list.count(obj) > 1:
            list.pop(list_length - i)
            no_dup_list[i] = []


def find_similar_completions(data_dict, prefix, length, completion_list):
    similar_completions = get_all_similar_completions(data_dict, prefix, length, completion_list)
    filter_best_similar_completions(similar_completions)

    return similar_completions[:length] if len(similar_completions) >= length else similar_completions


def find_identical_completions(data, prefix, completion_list):
    for sentence in data:
        completion_list.append(AutoCompleteData(sentence[0], sentence[1], len(prefix) * 2))

    return completion_list


def find_completions(data, prefix):
    completion_list = []
    try:
        completion_list = find_identical_completions(data[prefix], prefix, completion_list)
    except:
        return find_similar_completions(data, prefix, 5, completion_list)

    length = len(completion_list)
    if length < 5:
        completion_list += find_similar_completions(data, prefix, 5 - length, completion_list)
    return completion_list


def get_best_5_completions(prefix: str):
    with open('offline_data.json', 'r') as file:
        prefix = simplify_word(prefix)[:10] if len(prefix) > 10 else simplify_word(prefix)
        data = json.load(file)
    return find_completions(data, prefix)


def print_results(best_completions):
    if len(best_completions) > 0:
        print(f"Here {len(best_completions)} suggestions:")
    else:
        print("Oops, no matching results...")
        return
    for index, completion in enumerate(best_completions, 1):
        print(
            f"{index}. {completion.completed_sentence} ({completion.source_text} {completion.offset})\t(score: {completion.score})")
    print()


def auto_completion():
    npt = ""
    print("Enter your text <'#' to exit>:")
    while True:
        npt = npt + input(npt)
        if npt[-1] == '#':
            break
        print_results(get_best_5_completions(npt))
