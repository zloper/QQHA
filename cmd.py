# TODO Class with generated attr like list_name ???
import datetime
import json
import os
import re
import shutil

from flask import Flask, render_template, request, redirect, url_for


# TODO flask menu with file names
# TODO button clear all results


class Table():
    log = []  # TODO user steps for backward and save as pickle?

    def __init__(self, json_name: str):
        self.fl_name = json_name
        self.dct = self.read_table()
        self.table_name = list(self.dct.keys())[0]
        self.columns_list = list(self.dct[self.table_name].get("1", {'description': '', 'link': '', 'result': ''}))

    def generate_table(self):
        keys = self.dct[self.table_name][0].keys()
        for key in keys:
            print(key)

        for line in self.dct[self.table_name]:
            for k in keys:
                print(line[k])

    def read_table(self):
        with open(self.fl_name, "r", encoding='utf-8') as f:
            return json.load(f)

    def save_table(self):
        with open(self.fl_name, "w") as f:
            json.dump(self.dct, f)

    def rq_change_result(self, id, result):
        self.dct[self.table_name][id]["result"] = result
        self.save_table()

    def copy(self):
        now = datetime.datetime.now()
        dt_string = now.strftime("_ver_%d%m%y_%H%M")
        nm = self.fl_name
        if "_ver_" in nm:
            nm = re.sub(r'(_ver_\d{6}_\d{4}.json)', '.json', nm)
        new_name = nm.replace(".json", dt_string + ".json")

        try:
            shutil.copy(self.fl_name, new_name)
        except:
            print("file exist")

    def delete(self):
        if self.fl_name.endswith("Main_template.json"):
            return

        if self.fl_name.endswith(".json"):
            try:
                os.remove(self.fl_name)
            except:
                print("can't delete file %s" % self.fl_name)

    def print_table(self):
        print("Table:", self.table_name)
        print("Columns:", self.columns_list)
        for k, v in self.dct[self.table_name].items():
            print(" Line:", k, v)
        return self.dct[self.table_name]

    def update(self, dct):
        self.dct[self.table_name].update(dct)
        # print("dbg", self.dct)
        self.save_table()

    def get_lines(self):
        # return self.read_table()[self.table_name].items()
        result = []
        dct = self.read_table()[self.table_name]
        for id in dct:
            tmp = {}
            tmp["id"] = id
            tmp.update(dct[id])
            result.append(tmp)
        return result

    def add_row(self):
        self.dct[self.table_name]
        new_id = str(len(self.dct[self.table_name]) + 1)
        tmp = {}
        for k in self.columns_list:
            tmp[k] = ""
        self.dct[self.table_name][new_id] = tmp
        # print(self.dct[self.table_name])
        self.save_table()

    def rm_row(self, rm_id):
        dct = self.dct
        dct[self.table_name].pop(rm_id, None)
        self.reindex()
        self.save_table()

    def reindex(self):
        i = 0
        reindexed_dct = {}
        for _, v in self.dct[self.table_name].items():
            i += 1
            reindexed_dct[str(i)] = v
        self.dct[self.table_name] = reindexed_dct


app = Flask(__name__)


@app.route("/", methods=['GET', 'POST'])
def main_page():
    # tbl = Table("./checklists/Main_template.json")
    # tbl.rq_change_result(id="2", result="YEAH!")
    files = os.listdir("./checklists")
    if request.method == "GET":
        # TODO add to rq dtm of file modify
        return render_template("main_page.html", fl_list=files)

    if request.method == "POST":
        # TODO add to rq dtm of file modify
        if request.form['BTN'].startswith('Open file'):
            name = request.form['BTN'].split('Open file')[1]
            return redirect(url_for("table_page", fl_name=name.strip()))

        elif request.form['BTN'].startswith('Copy file'):
            name = request.form['BTN'].split('Copy file')[1]
            tb_c = Table("./checklists/%s" % name.strip())
            tb_c.copy()
            return redirect(url_for("main_page"))

        elif request.form['BTN'].startswith('Delete file'):
            # TODO "are you sure?" --popup
            name = request.form['BTN'].split('Delete file')[1]
            tb_d = Table("./checklists/%s" % name.strip())
            tb_d.delete()
            return redirect(url_for("main_page"))


@app.route("/table/<fl_name>", methods=['GET', 'POST'])
def table_page(fl_name):
    tb = Table("./checklists/%s" % fl_name.strip())
    if request.method == "GET":
        # TODO add to rq dtm of file modify
        lines = tb.get_lines()
        return render_template("table_page.html", table_name=tb.table_name, columns=tb.columns_list, lines=lines,
                               fl_name=fl_name.strip())


@app.route('/update', methods=['POST'])
def update():
    if request.method == 'POST':
        r = dict(request.form)
        print(r)
        new_table = {}
        rm_id = None
        for k, v in r.items():
            if k.startswith("@rm_row--"):
                rm_id = k.split("@rm_row--")[1]
                print(rm_id)

            if "-@@@-" in k:
                key = k.split("-@@@-")[0]
                id = k.split("-@@@-")[1]
                new_table.setdefault(str(id), {})
                new_table[str(id)][key] = v
        tb = Table("./checklists/%s" % r['fl_name'])
        tb.update(new_table)
        if r.get("new_row", False) == "True":
            tb.add_row()

        if rm_id is not None:
            tb.rm_row(rm_id)
        if r.get("back_btn", False)  == "True":
            return redirect(url_for("main_page"))
        return redirect(url_for("table_page", fl_name=r['fl_name']))



if __name__ == "__main__":
    app.run(debug=True)

#
# rq_change_result("Main_template.json", "2", "?123")
# print(read_table("Main_template.json"))

# generate_table("list_name", tst)
