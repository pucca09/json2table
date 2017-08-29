from flatten_json import flatten
import re
import sys
from functools import reduce


class BuildTable():
    def __init__(self, params):
        self.parse_schema(params["schema"])


    def extraction(self, json_list):
        rows = reduce(lambda x, y: x + self.extract_row_value(y), json_list, [])
        return rows

    def parse_schema(self, params):
        self.schema = []
        for column in params:
            if column.get("replace") != None:
                try:
                    column["replace"]["pattern"] = regExr(column["replace"]["pattern"])
                    column["replace"]["sub"] = regExr(column["replace"]["sub"])
                except:
                    print("SCHEMA FORMAT ERROR: pattern not exist")
                    sys.exit(-1)

            if column["value"] == "v" and column["type"] == "_CONSTANT_":
                pass
            else:
                column["path"] = regExr(column["path"])
                if (column["value"] == "v"):
                    column["path"] = "^" + column["path"] + "$"

            self.schema.append(column)


    def extract_row_value(self, json_object):
        flatted_json = flatten(json_object, "*")
        records = {}
        for column in self.schema:
            if column.get("value") == None or column["value"] == "":
                continue
            else:
                records[column["column_name"]] = {}
                if column["value"] == "k":
                    for key in flatted_json.keys():
                        try:
                            path = column["path"]
                        except:
                            print("SCHEMA FORMAT ERROR: 'path' do not exisit")
                            sys.exit(-1)
                        match = re.search(re.compile(path), key)
                        if match != None:
                            groups = match.groups()

                            if column.get("replace") != None:
                                sub_string = re.sub(column["replace"]["pattern"], column["replace"]["sub"],
                                                    groups[len(groups) - 1])
                                records[column["column_name"]][match.group()] = sub_string
                            else:
                                records[column["column_name"]][match.group()] = groups[len(groups) - 1]

                if column["value"] == "v" and column["type"] == "_VARIABLE_":
                    for key in flatted_json.keys():
                        try:
                            path = column["path"]
                        except:
                            print("SCHEMA FORMAT ERROR: 'path' do not exisit")
                            sys.exit(-1)
                        match = re.search(re.compile(path), key)

                        if match != None:
                            if column.get("replace") != None:
                                sub_string = re.sub(column["replace"]["pattern"], column["replace"]["sub"],
                                                    flatted_json[key])
                                records[column["column_name"]][key] = sub_string
                            else:
                                records[column["column_name"]][key] = flatted_json[key]

                if column["value"] == "v" and column["type"] == "_CONSTANT_":
                    if flatted_json.get(column["path"]) != None:
                        if column.get("replace") != None:
                            sub_string = re.sub(column["replace"]["pattern"], column["replace"]["sub"],
                                                flatted_json[column["path"]])
                            records[column["column_name"]][column["path"]] = sub_string
                        else:
                            records[column["column_name"]][column["path"]] = flatted_json[column["path"]]

                if column["value"] == "array":
                    path = column["path"]

                    for key in flatted_json.keys():
                        match = re.search(re.compile(path), key)
                        if match != None:
                            _key = match.group()
                            if records[column["column_name"]].get(_key) == None:
                                records[column["column_name"]][_key] = [flatted_json[key]]
                            else:
                                records[column["column_name"]][_key].append(flatted_json[key])
                    if column.get("replace") != None:

                        for path, values in records[column["column_name"]].items():
                            records[column["column_name"]][path] = [
                                re.sub(column["replace"]["pattern"], column["replace"]["sub"], x) for x in values]

        exists_variable = False
        for column in self.schema:
            if column["type"] == "_VARIABLE_":
                exists_variable = True
                break
        if exists_variable == False:
            rows = self.not_exist_variable(records)
        else:
            rows = self.exists_variable(records)
        return rows

    def not_exist_variable(self, records):
        row = {}
        for column in self.schema:

            if column.get("path") == None or column["path"] == "":
                row[column["column_name"]] = column["default"]
            else:
                if records[column["column_name"]].get(column["path"]) != None:
                    row[column["column_name"]] = records[column["column_name"]][column["path"]]
                else:
                    if column["default"] != "_REQUIRE_":
                        row[column["column_name"]] = column["default"]
                    else:
                        break
        return [row]

    def exists_variable(self, records):
        global df
        variable_depth_dict = {}
        for column in self.schema:
            if column["type"] == "_VARIABLE_":
                depth = len(column["path"].split("*"))
                variable_depth_dict[column["column_name"]] = depth

        # pick seed column
        seed = {"column_name": "", "depth": 0, "path": ""}
        # if exists variable with k value
        for column in self.schema:
            if column["type"] == "_VARIABLE_" and column["value"] == "k" and column["default"] == "_REQUIRE_":
                if variable_depth_dict[column["column_name"]] > seed["depth"]:
                    seed["column_name"] = column["column_name"]
                    seed["depth"] = variable_depth_dict[column["column_name"]]
                    seed["path"] = column["path"]
        if seed["depth"] == 0:
            for column in self.schema:
                if column["type"] == "_VARIABLE_" and column["default"] == "_REQUIRE_":
                    if variable_depth_dict[column["column_name"]] > seed["depth"]:
                        seed["column_name"] = column["column_name"]
                        seed["depth"] = variable_depth_dict[column["column_name"]]
                        seed["path"] = column["path"]


        seed_record_list = [{"path": k, seed["column_name"]: v} for k, v in records[seed["column_name"]].items()]


        rows = []
        for record in seed_record_list:
            row = {}
            row[seed["column_name"]] = record[seed["column_name"]]
            required_break = False
            for column in self.schema:
                if column["column_name"] != seed["column_name"]:
                    # _VARIABLE_
                    if column["type"] == "_VARIABLE_":
                        lcp = longestCommonPrefix([del_border_re(seed["path"]), del_border_re(column["path"])])
                        s1 = re.search(re.compile(lcp), record["path"]).group()
                        find_flag = False
                        for key, value in records[column["column_name"]].items():
                            s2 = re.search(re.compile(lcp), key).group()
                            if s1 == s2:
                                find_flag = True
                                row[column["column_name"]] = value
                                break

                        if find_flag == False:
                            if column["default"] != "_REQUIRE_":
                                row[column["column_name"]] = column["default"]
                            else:
                                required_break = True
                                break

                    # _CONSTANT_
                    if column["type"] == "_CONSTANT_":
                        if column.get("path") == None or column["path"] == "":
                            if self.check_default_variable(column["default"]):
                                VARIABLE_PATTERN = re.compile("\$\{([0-9a-zA-Z_-]+)\}")
                                default_var_list = VARIABLE_PATTERN.findall(column["default"])
                                default_value = column["default"]
                                for var in default_var_list:
                                    default_value = default_value.replace("${" + var + "}", row[var])
                                row[column["column_name"]] = default_value

                            else:
                                row[column["column_name"]] = column["default"]
                        else:
                            if records[column["column_name"]].get(column["path"]) != None:
                                row[column["column_name"]] = records[column["column_name"]][column["path"]]
                            else:
                                if column["default"] != "_REQUIRE_":
                                    row[column["column_name"]] = column["default"]
                                else:
                                    required_break = True
                                    break
            if required_break == False:
                rows.append(row)

        return rows


    def check_array_column(self):
        col_name_list = []
        for column in self.schema:
            if column["value"] == "array":
                col_name_list.append(column["column_name"])

        return col_name_list

    def check_default_variable(self, str):
        VARIABLE_PATTERN = re.compile("\$\{([0-9a-zA-Z_-]+)\}")
        if re.search(VARIABLE_PATTERN, str) != None:
            return True
        else:
            return False


def list_to_string(rows, col_name_list):
    _rows = []
    for row in rows:
        _row = row
        for key, values in row.items():
            if key in col_name_list and isinstance(values, list):
                _row[key] = "&&".join(values)
        _rows.append(_row)
    return _rows


def string_to_list(rows, col_name_list):
    _rows = []
    for row in rows:
        _row = row
        for key, values in row.items():
            if key in col_name_list and isinstance(values, basestring):
                _row[key] = values.split("&&")
        _rows.append(_row)
    return _rows


def longestCommonPrefix(strs):
    """
    :type strs: List[str]
    :rtype: str
    """
    length = len(strs);
    if length == 0:
        return '';
    if length == 1:
        return strs[0];
    flag = True;
    maxLen = 0;
    for i in range(length):
        if len(strs[i]) == 0:
            return '';
    while flag:
        for i in range(length - 1):
            if strs[i][maxLen] != strs[i + 1][maxLen]:
                flag = False;
                break;
            else:
                if len(strs[i]) == maxLen + 1 or len(strs[i + 1]) == maxLen + 1:
                    flag = False;
                if i == length - 2:
                    maxLen += 1;
    return strs[0][0:maxLen];


def regExr(str):
    return str.replace("*", "\*").replace("$VAL", "([^\*]+)").replace("$NUM", "(\d+)").replace("$SPACE", "\s").replace(
        "$NOT_SPACE", "\S").replace("$QUOT", "\\").replace("$GT", ">").replace("$LT", "<")


def del_border_re(str):
    if str[-1] == "$":
        return str[1:-2]
    else:
        return str


if __name__ == '__main__':
    pass





