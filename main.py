from pprint import pprint
from que_run import proceed_que

if __name__ == "__main__":
    questions, heading_info = proceed_que()
    pprint(heading_info)
    pprint(questions)
