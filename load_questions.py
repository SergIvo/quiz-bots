import os

from argparse import ArgumentParser


def get_questions_from_file(file_path):
    with open(file_path, 'r', encoding='KOI8-R') as file:
        content = file.read()
    return content


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
    file_path = os.path.join(questions_directory, questions_filenames[0])
    file_content = get_questions_from_file(file_path)
    print(file_content[:20])
