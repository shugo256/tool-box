import re, os, subprocess
from urllib import request, parse
from bs4 import BeautifulSoup

from modules.atcoder.config import *

# コンテストURLからコンテストのパス('/contests/abc001/')と名前('AtCoder Beginer ...')を取り出す
# 入力が None の場合は最新コンテストのものを返す
def get_contest_info(contest_url=None):
    if contest_url:
        contest_soup = BeautifulSoup(request.urlopen(contest_url), "html.parser")

        contest_path = contest_url.replace(BASE_URL, '/')
        contest_name = contest_soup.h1.text
    else:
        # アーカイブから直近のコンテストを取得
        archive_url = request.urlopen(parse.urljoin(BASE_URL, CONTESTS_ARCHIVE_PATH))
        archive_soup = BeautifulSoup(archive_url, "html.parser")

        latest = archive_soup.find('a', href=re.compile(CONTESTS_BASE_PATH + "/[a-z0-9\-]+(?<!archive)$"))
        
        contest_path = latest.get('href')
        contest_name = latest.text
    
    return contest_path, contest_name


# コンテスト以下のパス('/contests/abc001/...')からファイルのprefix('001')を決定
def gen_contest_prefix(contest_path):
    contest_str = contest_path.replace(CONTESTS_BASE_PATH, '').split('/')[1]

    if contest_str[:3] in ['abc', 'arc', 'agc']:
        prefix = contest_str[3:]
    else:
        contest_str = contest_str.replace('-', '_')
        contest_str = re.sub('([a-z])([0-9])|([0-9])([a-z])', '\\1_\\2', contest_str) # a0 -> a_0 , 0a -> 0_a

        prefix = contest_str.title()
    
    return prefix


# コンテストのパスから問題名たちを取得
def get_task_names(contest_path):
    tasks_path = os.path.join(contest_path, "tasks")
    tasks_url = request.urlopen(parse.urljoin(BASE_URL, tasks_path))

    tasks_soup = BeautifulSoup(tasks_url, "html.parser")
    task_parts = tasks_soup.find_all('a', href=re.compile(tasks_path + "/.+$"))

    # 配列を二個ずつに分割する技 参考: https://iogi.hatenablog.com/entry/split-list-into-sublist
    task_dict = {
        char.text: name.text.replace(' ', '_').replace('/', '-') 
        for char, name in zip(*[iter(task_parts)]*2)
    }

    return task_dict


# コンテストのURLからファイルのprefixを決定、ユーザーに確認し、場合によっては修正してもらう
def ask_contest_prefix(contest_path):
    prefix = gen_contest_prefix(contest_path)

    print("\ngenerated prefix : {}\n".format(prefix))
    print("if the prefix is okay for you, just press [Enter]")
    print("if not, input the prefix")

    user_prefix = input('>>> ')
    if len(user_prefix) > 0:
        prefix = user_prefix
    print() # 改行

    return prefix


# 問題用のファイル名を取得
def gen_file_name(contest_prefix, task_char, task_name):
    return '_'.join([contest_prefix, task_char, task_name]) + EXTENTION


# テンプレートファイルを生成する
def create_template_file(file_name):
    if not file_name.endswith(EXTENTION):
        file_name += EXTENTION
    print('generating {}...'.format(file_name))
    with open(file_name, 'w') as f:
        subprocess.call(['cat', TEMPLATE_PATH], stdout=f)
    subprocess.call(['code', file_name])