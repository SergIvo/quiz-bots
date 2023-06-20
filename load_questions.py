import os
import re

from argparse import ArgumentParser


def get_questions_from_file(file_path):
    with open(file_path, 'r', encoding='KOI8-R') as file:
        content = file.read()
    return content


def parse_questions_from_text(text):
    question_blocks = re.findall(r'\bВопрос.+?Ответ:.+?(?=\n\n)', text, flags=re.DOTALL)
    print('Found: ', len(question_blocks))
    
    questions = []
    for question_block in question_blocks:
        question = re.search(r'(?<=:\s).+(?=\sОтвет)', question_block, flags=re.DOTALL).group()
        try:
            answer = re.search(r'(?<=Ответ:\s).+', question_block, flags=re.DOTALL).group()
        except:
            print(question_block)
            answer = None
        questions.append({question: answer})
    
    return questions


if  __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        'questions_directory', 
        type=str,
        help='path to directory with questions files'
    )
    args = parser.parse_args()
    questions_directory = args.questions_directory

    questions_filenames = os.listdir(args.questions_directory)
    for filename in questions_filenames:
        file_path = os.path.join(questions_directory, filename)
        questions_text = get_questions_from_file(file_path)
        questions = parse_questions_from_text(questions_text)

