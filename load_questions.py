import os
import re
import json

from argparse import ArgumentParser


def get_questions_from_file(file_path):
    with open(file_path, 'r', encoding='KOI8-R') as file:
        content = file.read()
    return content


def parse_questions_from_text(text):
    question_blocks = re.findall(
        r'\bВопрос.+?Ответ:.+?(?=\n\n)',
        text,
        flags=re.DOTALL
    )

    questions = {}
    for question_block in question_blocks:
        question = re.search(
            r'(?<=:\s).+(?=\sОтвет)',
            question_block,
            flags=re.DOTALL
        ).group()
        answer = re.search(
            r'(?<=Ответ:\s).+',
            question_block,
            flags=re.DOTALL
        ).group()
        questions[question] = answer
    return questions


def load_questions_from_files(questions_directory, limit=None):
    questions_filenames = os.listdir(args.questions_directory)
    all_questions = {}
    for filename in questions_filenames[:limit]:
        file_path = os.path.join(questions_directory, filename)
        questions_text = get_questions_from_file(file_path)
        questions = parse_questions_from_text(questions_text)
        all_questions.update(questions)
    return all_questions


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        'questions_directory',
        type=str,
        help='path to directory with questions files'
    )
    parser.add_argument(
        'files_limit',
        type=str,
        help='Number of questions files to load'
    )
    args = parser.parse_args()
    questions_directory = args.questions_directory
    files_limit = int(args.files_limit)

    all_questions = load_questions_from_files(questions_directory, files_limit)
    with open('questions.json', 'w', encoding='utf8') as file:
        json.dump(all_questions, file, indent=4, ensure_ascii=False)
