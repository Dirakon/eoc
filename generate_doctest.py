#!/usr/bin/env python3

from os.path import exists
import sys
import os
import json

def find_nth_substr(original_text: str, substr_to_find: str, n: int) -> int:
    start = original_text.find(substr_to_find)
    while start >= 0 and n > 1:
        start = original_text.find(substr_to_find, start+len(substr_to_find))
        n -= 1
    return start

def try_get_segment(original_text: str, segment_name: str, generated_mapping_file: str) -> str | None:
    segment_start = original_text.find(f"<{segment_name}>")
    segment_end = original_text.find(f"</{segment_name}>")
    if segment_end < 0 or segment_start < 0:
        print(f"Cannot find segment {segment_name} in {generated_mapping_file}")
        return None
    segment = original_text[segment_start + len(f"<{segment_name}>"):segment_end].strip()
    return segment

def main():
    eo_file = sys.argv[1]
    generated_mapping_file = sys.argv[2]
    comment_placeholder = sys.argv[3]


    eo_file_content = open(eo_file).read()
    directory_of_genenerated_mapping_file = os.path.dirname(generated_mapping_file)
    generated_mapping_content:list[str] = json.loads(open(generated_mapping_file).read())

    for i, documentation in enumerate(generated_mapping_content):
        explanation = try_get_segment(documentation, "explanation", generated_mapping_file) or "<NOT-FOUND>"
        doctest_output = try_get_segment(documentation, "doctest-output", generated_mapping_file)
        doctest_code = try_get_segment(documentation, "doctest-code", generated_mapping_file)
        if doctest_output is None or doctest_code is None:
            continue

        out_file = os.path.join(directory_of_genenerated_mapping_file, str(i), "app.eo")
        expected_out_file = os.path.join(directory_of_genenerated_mapping_file, str(i), "expected.txt")
        os.makedirs(os.path.dirname(out_file), exist_ok=True)
        if exists(out_file):
            os.remove(out_file)
        if exists(expected_out_file):
            os.remove(expected_out_file)

        explanation_as_comment = "# " + explanation.replace('\n', '\n# ')
        correct_mark_start = find_nth_substr(eo_file_content, comment_placeholder, i + 1)
        eo_file_with_new_documentation = (eo_file_content[:correct_mark_start] + \
            explanation_as_comment + \
            eo_file_content[correct_mark_start + len(comment_placeholder):]).strip() + \
            "\n" + \
            "\n" + \
            "# Doctest\n" + \
            "[] > doctest-entry\n" + \
            "  seq > @\n" + \
            "    *\n" + \
            "      QQ.io.stdout\n" + \
            "        \"<START>\"\n" + \
            "      doctest\n" + \
            "      QQ.io.stdout\n" + \
            "        \"<END>\"\n" + \
            "\n" + \
            "# Doctest\n" + \
            doctest_code
        open(out_file, 'w').write(eo_file_with_new_documentation)
        open(expected_out_file, 'w').write(doctest_output)

if __name__ == "__main__":
    main()
