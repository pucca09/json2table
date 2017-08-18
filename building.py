from flatten_json import flatten
import re

class BuildTable():
    def __init__(self, params, db=None):
        self.db = db
        self.col = params.get("name","")
        self.parse_schema(params)
        # self.unique_key_prefix()

    def extraction(self, json_list):
        return reduce(lambda x, y: x + self.extract_row_value(y), json_list, [])

    def export_to_db(self, json_list):
        assert self.db != None ,"db is not defined"
        assert self.col != "", "collection name is not defined"
        records = self.extraction(json_list)
        self.db[self.col].drop()
        self.db[self.col].insert_many(records)
        return records

    def parse_schema(self, params):

        self.schema = []
        try:
            for column in params["schema"]:
                if column.get("replace") != None:
                    try:
                        column["replace"]["pattern"] = regExr(column["replace"]["pattern"])
                        column["replace"]["sub"] = regExr(column["replace"]["sub"])
                    except:
                        print("SCHEMA FORMAT ERROR: pattern not exist")

                if column["value"] == "v" and column["privilege"] == "_CONSTANT_":
                    pass
                else:
                    column["path"] = regExr(column["path"])
                    if (column["value"] == "v"):
                        column["path"] = "^" + column["path"] + "$"

                self.schema.append(column)
        except:
            assert params.get("schema") != None,"schema is not defined"
        # LOG.debug("parsed schema is {0}".format(self.schema))

    # def unique_key_prefix(self):
    #     unique_column_path_list = []
    #     for column in self.schema:
    #         if column["privilege"] == "_LEAF_":
    #             unique_column_path_list.append(column["path"])
    #     self.LCP = longestCommonPrefix(unique_column_path_list)

    def extract_row_value(self, json_object):
        flatted_json = flatten(json_object, "*")
        # LOG.debug(flatted_json.keys())
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
                            exit(-1)
                            # LOG.error("SCHEMA FORMAT ERROR: 'path' do not exisit")
                        match = re.search(re.compile(path), key)
                        if match != None:
                            groups = match.groups()
                            # LOG.debug(format("groups length:{0},groups{1},path:{2},key:{3}".format(len(groups),groups,column["path"],key)))
                            if column.get("replace") != None:
                                sub_string = re.sub(column["replace"]["pattern"], column["replace"]["sub"],
                                                    groups[len(groups) - 1])
                                records[column["column_name"]][match.group()] = sub_string
                            else:
                                records[column["column_name"]][match.group()] = groups[len(groups) - 1]
                if column["value"] == "v" and column["privilege"] == "_VARIABLE_":
                    for key in flatted_json.keys():
                        try:
                            path = column["path"]
                        except:
                            exit(-1)
                            # LOG.error("SCHEMA FORMAT ERROR: 'path' do not exisit")
                        match = re.search(re.compile(path), key)

                        if match != None:
                            # LOG.debug("{0} and {1} is match".format(path, key))
                            if column.get("replace") != None:
                                sub_string = re.sub(column["replace"]["pattern"], column["replace"]["sub"],
                                                    flatted_json[key])
                                records[column["column_name"]][key] = sub_string
                            else:
                                records[column["column_name"]][key] = flatted_json[key]

                if column["value"] == "v" and column["privilege"] == "_CONSTANT_":
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
                        # sub_string = re.sub(column["replace"]["pattern"], column["replace"]["sub"],
                        #                     flatted_json[column["path"]])
                        # records[column["column_name"]][column["path"]] = sub_string

                        for path, values in records[column["column_name"]].items():
                            records[column["column_name"]][path] = [
                                re.sub(column["replace"]["pattern"], column["replace"]["sub"], x) for x in values]

        # LOG.debug("records is {0}".format(records))
        # unique_required_column_list = []
        # for column in self.schema:
        #     if column["privilege"] == "_LEAF_" and column["default"] == "_REQUIRE_":
        #         unique_required_column_list.append(column)
        #
        # seed = unique_required_column_list[random.randint(0, len(unique_required_column_list) - 1)]
        # seed_record_list = [{"path":k,seed["column_name"]:v} for k,v in records[seed["column_name"]].items()]

        # if there not exists _VARIABLE_
        exists_variable = False
        for column in self.schema:
            if column["privilege"] == "_VARIABLE_":
                exists_variable = True
                break
        rows = []
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
        variable_depth_dict = {}
        for column in self.schema:
            if column["privilege"] == "_VARIABLE_":
                depth = len(column["path"].split("*"))
                variable_depth_dict[column["column_name"]] = depth
        # LOG.debug("variable column depth:{0}".format(variable_depth_dict))

        # pick seed column
        seed = {"column_name": "", "depth": 0, "path": ""}
        # if exists variable with k value
        for column in self.schema:
            if column["privilege"] == "_VARIABLE_" and column["value"] == "k":
                if variable_depth_dict[column["column_name"]] > seed["depth"]:
                    seed["column_name"] = column["column_name"]
                    seed["depth"] = variable_depth_dict[column["column_name"]]
                    seed["path"] = column["path"]
        if seed["depth"] == 0:
            for column in self.schema:
                if column["privilege"] == "_VARIABLE_" and column["default"] == "_REQUIRE_":
                    if variable_depth_dict[column["column_name"]] > seed["depth"]:
                        seed["column_name"] = column["column_name"]
                        seed["depth"] = variable_depth_dict[column["column_name"]]
                        seed["path"] = column["path"]

        # LOG.debug("seed column is {0}".format(seed))
        seed_record_list = [{"path": k, seed["column_name"]: v} for k, v in records[seed["column_name"]].items()]
        # LOG.debug("seed record list is {0}".format(seed_record_list))

        rows = []
        for record in seed_record_list:
            row = {}
            row[seed["column_name"]] = record[seed["column_name"]]
            required_break = False
            for column in self.schema:
                if column["column_name"] != seed["column_name"]:
                    # _VARIABLE_
                    if column["privilege"] == "_VARIABLE_":
                        lcp = longestCommonPrefix([del_border_re(seed["path"]), del_border_re(column["path"])])
                        # LOG.debug("lcp is {0}, seed path is {1},column path is {2}".format(lcp, del_border_re(seed["path"]),del_border_re(column["path"])))
                        s1 = re.search(re.compile(lcp), record["path"]).group()
                        find_flag = False
                        for key, value in records[column["column_name"]].items():
                            s2 = re.search(re.compile(lcp), key).group()
                            if s1 == s2:
                                find_flag = True
                                # if row.get(column["column_name"]) == None:
                                #     row[column["column_name"]] = value
                                # else:
                                #     if isinstance(row[column["column_name"]],basestring):
                                #         _value = row[column["column_name"]]
                                #         row[column["column_name"]] = [_value,value]
                                #     elif isinstance(row[column["column_name"]],list):
                                #         row[column["column_name"]].append(value)
                                row[column["column_name"]] = value
                                break

                        if find_flag == False:
                            if column["default"] != "_REQUIRE_":
                                row[column["column_name"]] = column["default"]
                            else:
                                required_break = True
                                break
                                # if variable_depth_dict[column["column_name"]] < seed["depth"]:
                                #     find_flag = False
                                #     for key, value in records[column["column_name"]].items():
                                #         if (record["path"].startswith(key)):
                                #             find_flag = True
                                #             row[column["column_name"]] = value
                                #     if find_flag == False:
                                #         if column["default"] != "_REQUIRE_":
                                #             row[column["column_name"]] = column["default"]
                                #         else:
                                #             required_break = True
                                #             break
                                # if variable_depth_dict[column["column_name"]] > seed["depth"]:
                                #     # s1 = re.search(re.compile(self.LCP),record["path"]).group()
                                #     # find_flag = False
                                #     # for key,value in records[column["column_name"]].items():
                                #     #     s2 = re.search(re.compile(self.LCP), key).group()
                                #     #     if s1==s2:
                                #     #         find_flag = True
                                #     #         row[column["column_name"]] = value
                                #     #         break
                                #     # if find_flag == False:
                                #     #     if column["default"] != "_REQUIRE_":
                                #     #         row[column["column_name"]] = column["default"]
                                #     #     else:
                                #     #         break
                                #     find_flag = False
                                #     for key, value in records[column["column_name"]].items():
                                #         if (key.startswith(record["path"])):
                                #             find_flag = True
                                #             row[column["column_name"]] = value
                                #             break
                                #     if find_flag == False:
                                #         if column["default"] != "_REQUIRE_":
                                #             row[column["column_name"]] = column["default"]
                                #         else:
                                #             required_break = True
                                #             break

                    # _CONSTANT_
                    if column["privilege"] == "_CONSTANT_":
                        if column.get("path") == None or column["path"] == "":
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
    # regx = re.compile("family\*([^\*]+)\*")
    # str = "family*hello*why"
    # match = re.search(regx,str)
    # conn = pymongo.MongoClient(host="127.0.0.1", port=27017)
    # db = conn["netdata"]
    #
    # root_dir = os.path.dirname(os.path.dirname(__file__))
    # print root_dir
    #
    # params = json.load(open(os.path.join(root_dir, "build_collection", "l2_ris"), "r"))
    # bd = BuildTable(params, db)
    # json_list = json.load(open(os.path.join(root_dir, "fetch_config", "parse_conf.txt"), "r"))
    #
    # res = bd.export_to_db(json_list)

    # bd.export_to_db(res)
    pass
