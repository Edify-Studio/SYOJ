# -*- coding: utf-8 -*-
import os
import time
import zipfile
import urllib.parse
import urllib.request
import json
import codecs
import subprocess
import psutil

_SYZOJ_URL = "http://localhost:8811"
_DOWNLOAD_TESTDATA_URL = _SYZOJ_URL + "/static/uploads"
_GET_TASK_URL = _SYZOJ_URL + "/api/waiting_judge"
_UPLOAD_TASK_URL = _SYZOJ_URL + "/api/update_judge"
_SESSION_ID = "77783949202395150352388871624955475980489287735056"
_BASE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)))
_TESTDATA_DIR = os.path.join(_BASE_DIR, "testdata")

if not os.path.isdir(_TESTDATA_DIR):
    os.mkdir(_TESTDATA_DIR)


def get_judge_task():
    global _GET_TASK_URL, _SESSION_ID
    url = _GET_TASK_URL + "?" + urllib.parse.urlencode({"session_id": _SESSION_ID})
    task = urllib.request.urlopen(url).read()
    return json.loads(bytes.decode(task))


def upload_judge_result(result, judge_id):
    global _UPLOAD_TASK_URL, _SESSION_ID
    url = _UPLOAD_TASK_URL + "/" + str(judge_id) + "?" + urllib.parse.urlencode({"session_id": _SESSION_ID})
    data = str.encode(urllib.parse.urlencode({"result": json.dumps(result)}))
    req = urllib.request.Request(url, data)
    response = urllib.request.urlopen(req)
    return bytes.decode(response.read())


def download_file(url, des):
    df = urllib.request.urlopen(url)
    f = open(des, "w+b")
    while True:
        data = df.read(4096)
        if data:
            f.write(data)
        else:
            break
    df.close()
    f.close()


def unzip_as_testdata(testdata, des_dir):
    if not os.path.isdir(des_dir):
        os.mkdir(des_dir)

    zip_file = zipfile.ZipFile(testdata)

    for name in zip_file.namelist():
        with open(os.path.join(des_dir, name), "wb") as f:
            f.write(zip_file.read(name))
            f.close()

    zip_file.close()


def get_testdata_dir(testdata_name):
    global _TESTDATA_DIR, _DOWNLOAD_TESTDATA_URL
    testdata_dir = os.path.join(_TESTDATA_DIR, testdata_name)
    if os.path.isdir(testdata_dir):
        return testdata_dir

    tmp_zip_file = _TESTDATA_DIR + testdata_name + "_tmp.zip"
    download_file(_DOWNLOAD_TESTDATA_URL + "/" + testdata_name, tmp_zip_file)
    unzip_as_testdata(tmp_zip_file, testdata_dir)
    os.remove(tmp_zip_file)

    return testdata_dir


def write_src(source, target):
    if os.path.isfile(target):
        os.remove(target)
    with codecs.open(target, "w", "utf-8") as f:
        f.write(source)


f = "g++ %s -O2 -Wall -lm --static -DONLINE_JUDGE -o main.exe"


def trace_resources(subp, time_limit, memory_limit):
    begin_time = time.clock()
    maxmem = 0
    current_time = begin_time
    try:
        pspro = psutil.Process(subp.pid)
    except Exception:
        return (1024, 0)
    current_time = time.clock()
    while pspro.is_running():
        try:
            maxmem = max(maxmem, pspro.memory_info().rss // 1024)
        except Exception:
            return (maxmem, current_time - begin_time)
        current_time = time.clock()
        if current_time - begin_time > time_limit:
            subp.terminate()
            return (maxmem, -1)
        if maxmem > memory_limit:
            subp.terminate()
            return (-1, current_time - begin_time)
    return (maxmem, current_time - begin_time)


def compile_and_run(cfg):
    res = {}
    global compiled
    if not compiled:
        p = subprocess.Popen(f % cfg['source_name'],
                             shell=True,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             universal_newlines=True)
        begin_t = time.clock()
        out, err = p.communicate(timeout=20)
        end_t = time.clock()
        if end_t - begin_t > 19:
            p.terminate()
            time.sleep(1)
            res['score'] = 0
            res['status'] = 'Compile Error'
            res['compile_info'] = "Compile Time Too Long!"
            return res
        if p.returncode != 0:
            res['score'] = 0
            res['status'] = 'Compile Error'
            res['compile_info'] = out + err
            return res
    compiled = True
    o = open(cfg['out_file'], "w+")
    infile = open(cfg['in_file'], "r")
    p = subprocess.Popen('main.exe',
                         stdin=infile,
                         stdout=o,
                         stderr=subprocess.STDOUT)
    me, ti = trace_resources(p,
                             cfg['time_limit'] / 1000.0,
                             cfg['memory_limit'] * 1024)
    p.kill()
    p.wait(timeout=1)
    infile.close()
    o.close()
    if me == -1:
        res['score'] = 0
        res['status'] = 'Memory Limit Exceed'
        res['use_time'] = int(ti * 1000)
        res['memory_used'] = cfg['memory_limit'] * 1024
        return res
    if ti == -1:
        res['score'] = 0
        res['status'] = 'Time Limit Exceed'
        res['use_time'] = cfg['time_limit']
        res['memory_used'] = me
        return res
    if p.returncode != 0:
        res['score'] = 0
        res['status'] = 'Runtime Error'
        return res
    res['use_time'] = int(ti * 1000)
    res['use_memory'] = me
    try:
        curr = open(cfg['out_file']).read().replace('\r', '').split()
        user = open(cfg['ans_file']).read().replace('\r', '').split()
        os.remove(cfg['out_file'])
    except Exception:
        res['score'] = 0
        res['status'] = "System Error"
        return res
    if curr == user:
        res['score'] = 1
        res['status'] = "Accepted"
        return res
    res['score'] = 0
    res['status'] = "Wrong Answer"
    return res


def run(source_file, std_in, std_out, time_limit, memory_limit):
    user_out = "user_tmp.out"

    CFG = {
        'language': 'C++',
        'source_name': source_file,
        'in_file': std_in,
        'out_file': user_out,
        'ans_file': std_out,
        'time_limit': time_limit,
        'memory_limit': memory_limit,
        'compile option': ['-lm', '-DONLINE_JUDGE']
    }

    res = compile_and_run(CFG)

    result = {}
    result['status'] = res['status']

    if 'use_time' not in res:
        result['time_used'] = 0
    else:
        result["time_used"] = res["use_time"]
    if 'use_memory' not in res:
        result['memory_used'] = 1024
    else:
        result["memory_used"] = res["use_memory"]

    result['score'] = res['score']

    if 'in' in res:
        result["input"] = res['in'][0: min(120, len(res['in']))]
        if len(res['in']) > 120:
            result["input"] += '\n...'
    if 'ans' in res:
        result["answer"] = res['ans'][0: min(120, len(res['ans']))]
        if len(res['ans']) > 120:
            result["answer"] += '\n...'
    if 'out' in res:
        result["user_out"] = res['out'][0: min(120, len(res['out']))]
        if len(res['out']) > 120:
            result["user_out"] += '\n...'
    if 'compile_info' in res:
        result['compile_info'] = res['compile_info']
        if len(res['compile_info']) > 256:
            result["compile_info"] += '\n...'

    return result


def judge(source, time_limit, memory_limit, testdata):
    result = {"status": "Judging", "score": 0, "total_time": 0, "max_memory": 0, "case_num": 0}
    target = "tjudger_source_file.cpp"

    testdata_dir = get_testdata_dir(testdata)

    write_src(source, target)

    with open(os.path.join(testdata_dir, "data_rule.txt")) as f:
        data_rule = f.read()
    lines = data_rule.split('\n')
    for i in range(0, len(lines)):
        lines[i] = lines[i].replace('\r', '').replace('\n', '')
    dt_no = lines[0].split()
    std_in = lines[1]
    std_out = lines[2]
    global compiled
    compiled = False

    for i, no in enumerate(dt_no):
        std_in_file = os.path.join(testdata_dir, std_in.replace("#", str(no)))
        std_out_file = os.path.join(testdata_dir, std_out.replace("#", str(no)))
        res = run(target, std_in_file, std_out_file, time_limit, memory_limit)

        if res['status'] == "Compile Error":
            result['compiler_output'] = res['compile_info']
            result['status'] = "Compile Error"
            return result

        result[i] = res
        result["case_num"] += 1
        result["total_time"] += res["time_used"]
        if res["memory_used"] > result["max_memory"]:
            result["max_memory"] = res["memory_used"]

        if res["status"] == "Accepted":
            result["score"] += 100.0 / len(dt_no) * res['score']
        elif result["status"] == "Judging":
            result["status"] = res["status"]

    result["score"] = int(result["score"] + 0.1)
    if result["status"] == "Judging":
        result["status"] = "Accepted"
    return result


def main():
    while True:
        time.sleep(1)
        task = get_judge_task()
        if not task["have_task"]:
            continue
        try:
            result = judge(task["code"], task["time_limit"], task["memory_limit"], task["testdata"])
        except Exception as e:
            result = {"status": "System Error", "score": 0, "total_time": 0, "max_memory": 0, "case_num": 0}
            upload_judge_result(result, task["judge_id"])
            raise e
        upload_judge_result(result, task["judge_id"])


def test_connect_to_server():
    task = get_judge_task()
    testdata_dir = get_testdata_dir(task["testdata"])
    print(task)
    print(testdata_dir)
    print(upload_judge_result({"status": "System Error",
                               "score": 0,
                               "total_time": 0,
                               "max_memory": 0,
                               "case_num": 0},
                              task["judge_id"]))


if __name__ == '__main__':
    # test_connect_to_server()
    # main()
    while True:
        main()
