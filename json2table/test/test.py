import pymongo
import unittest2

from json2table.building import BuildTable

json_list = [
    {
        "id": '1',
        "name": {
            "first": "john",
            "last": "johnson"
        },
        "age": '27',
        "languages":{
            "c#":{
                "grade":"80",
                "class":"A"
            },
            "python":{
                "grade":"81",
                "class":"B"
                        },
            "go":{
                "grade":"82",
                "class":"C"
                        }

        },
		"gender":"male",
        "friends":[
            {"name":"peter",
             "intimacy":{
                 "hobby":["swim","football"],
                 "age_diff":"2"
                }
             },
            {"name":"rose",
                 "intimacy":{
                     "hobby":["swim"],
                     "age_diff":"3"
                    }
                 }
        ]
     },
     {
        "id": '2',
        "name": {
            "first": "scott",
            "middle": "scottster",
            "last": "scottson"
        },
        "age": '29',
        "languages": {
            "c++":{
                "grade":"90",
                "class":"A"
            },
            "python":{
                "grade":"85",
                "class":"B"
                        },
            "vb":{
                "grade":"82",
                "class":"C"
                        }
        },
        "gender":"male",
        "friends":[
            {"name":"henry",
             "intimacy":{
                 "hobby":["dance","football"],
                 "age_diff":"2"
                }
             },
            {"name":"jane",
                 "intimacy":{
                     "hobby":["sing"],
                     "age_diff":"3"
                    }
                 }
        ]
     },
    {
        "id": '3',
        "name": {
            "first": "tom",
            "middle": "peter",
            "last": "rick"
        },
        "languages": {
            "java":{
                "grade":"90",
                "class":"A"
            },
            "scala":{
                "grade":"85",
                "class":"B"
                        }
        }
     }
]
conn = pymongo.MongoClient(host="127.0.0.1", port=27017)
db = conn["build_col_test"]

class UniTests(unittest2.TestCase):
    # @unittest2.skip("")
    def test1_constant(self):
        params = {"name":"build_col_test1",
                  "schema":[
                  {
                    "column_name":"id",
                    "path":"id",
                    "privilege":"_CONSTANT_",
                    "default":"_REQUIRE_",
                    "value":"v"
                  },
                  {
                      "column_name": "first_name",
                      "path": "name*first",
                      "privilege": "_CONSTANT_",
                      "default": "_REQUIRE_",
                      "value": "v"
                  },
                  {
                      "column_name": "age",
                      "path": "age",
                      "privilege": "_CONSTANT_",
                      "default": "10",
                      "value": "v"
                  }
                  ]}
        bd = BuildTable(params,db)
        actual = bd.extraction(json_list)
        # print("actual is {0}".format(actual))
        expected = [{'id':'1','first_name':'john',"age":'27'},{'id':'2','first_name':'scott','age':'29'},{'id':'3','first_name':'tom','age':'10'}]
        self.assertEqual(actual, expected)
        bd = BuildTable(params, db)
        res = bd.export_to_db(json_list)

    # @unittest2.skip("")
    def test2_constant(self):
        params = {"name":"build_col_test2",
                  "schema":[
                  {
                    "column_name":"id",
                    "path":"id",
                    "privilege":"_CONSTANT_",
                    "default":"_REQUIRE_",
                    "value":"v"
                  },
                  {
                      "column_name": "first_name",
                      "path": "name*first",
                      "privilege": "_CONSTANT_",
                      "default": "_REQUIRE_",
                      "value": "v"
                  },
                  {
                      "column_name": "age",
                      "path": "age",
                      "privilege": "_CONSTANT_",
                      "default": "10",
                      "value": "v"
                  },
                  {
                      "column_name": "company",
                      "path": "",
                      "privilege": "_CONSTANT_",
                      "default": "ibm",
                      "value": "v"
                  }
                  ]}
        # bd = BuildTable(params,db)
        # actual = bd.extraction(json_list)
        # print("actual is {0}".format(actual))
        bd = BuildTable(params, db)
        res = bd.export_to_db(json_list)

    # @unittest2.skip("")
    def test3_variable(self):
        params = {"name": "build_col_test3",
                  "schema": [
                      {
                          "column_name": "id",
                          "path": "id",
                          "privilege": "_CONSTANT_",
                          "default": "_REQUIRE_",
                          "value": "v"
                      },
                      {
                          "column_name": "language",
                          "path": "languages*$VAL",
                          "privilege": "_VARIABLE_",
                          "default": "",
                          "value": "k"
                      }]}

        bd = BuildTable(params, db)
        res = bd.export_to_db(json_list)

    # @unittest2.skip("")
    def test4_variable(self):
        params = {"name": "build_col_test4",
                  "schema": [
                      {
                          "column_name": "id",
                          "path": "id",
                          "privilege": "_CONSTANT_",
                          "default": "_REQUIRE_",
                          "value": "v"
                      },
                      {
                          "column_name": "language",
                          "path": "languages*$VAL",
                          "privilege": "_VARIABLE_",
                          "default": "",
                          "value": "k"
                      },
                      {
                          "column_name": "grade",
                          "path": "languages*$VAL*grade",
                          "privilege": "_VARIABLE_",
                          "default": "-",
                          "value": "v"
                      }
                  ]}
        # bd = BuildTable(params,db)
        # actual = bd.extraction(json_list)
        # print("actual is {0}".format(actual))
        # print("actual is {0}".format(bd.extract_row_value(json_list[0])))

        bd = BuildTable(params, db)
        res = bd.export_to_db(json_list)
    # @unittest2.skip("")
    def test5_default(self):
        params = {"name": "build_col_test5",
                  "schema": [
                      {
                          "column_name": "id",
                          "path": "id",
                          "privilege": "_CONSTANT_",
                          "default": "_REQUIRE_",
                          "value": "v"
                      },
                      {
                          "column_name": "language",
                          "path": "languages*$VAL",
                          "privilege": "_VARIABLE_",
                          "default": "",
                          "value": "k"
                      },
                      {
                          "column_name": "gender",
                          "path": "gender",
                          "privilege": "_CONSTANT_",
                          "default": "female",
                          "value": "v"
                      }
                  ]}
        # bd = BuildTable(params,db)
        # actual = bd.extraction(json_list)
        # print("actual is {0}".format(actual))
        bd = BuildTable(params, db)
        res = bd.export_to_db(json_list)

    # @unittest2.skip("")
    def test6_replace(self):
        params = {"name": "build_col_test6",
                  "schema": [
                      {
                          "column_name": "id",
                          "path": "id",
                          "privilege": "_CONSTANT_",
                          "default": "_REQUIRE_",
                          "value": "v"
                      },
                      {
                          "column_name": "language",
                          "path": "languages*$VAL",
                          "privilege": "_VARIABLE_",
                          "default": "",
                          "value": "k"
                      },
                      {
                          "column_name": "grade",
                          "path": "languages*$VAL*grade",
                          "privilege": "_VARIABLE_",
                          "replace":{
                              "pattern":"$VAL",
                              "sub":"$QUOTg$LT1$GT point"
                          },
                          "default":"",
                          "value": "v"
                      }
                  ]}
        bd = BuildTable(params,db)
        actual = bd.extraction(json_list)
        print("actual is {0}".format(actual))

        res = bd.export_to_db(json_list)

    # @unittest2.skip("")
    def test7_list(self):
        params = {"name": "build_col_test7",
                  "schema": [
                      {
                          "column_name": "id",
                          "path": "id",
                          "privilege": "_CONSTANT_",
                          "default": "_REQUIRE_",
                          "value": "v"
                      },
                      {
                          "column_name": "friend",
                          "path": "friends*$NUM*name",
                          "privilege": "_VARIABLE_",
                          "default":"_REQUIRE_",
                          "value": "v"
                      }]}
        # bd = BuildTable(params,db)
        # actual = bd.extraction(json_list)
        # print("actual is {0}".format(actual))
        bd = BuildTable(params, db)
        res = bd.export_to_db(json_list)

    # @unittest2.skip("")
    def test8_list(self):
        params = {"name": "build_col_test8",
                  "schema": [
                      {
                          "column_name": "id",
                          "path": "id",
                          "privilege": "_CONSTANT_",
                          "default": "_REQUIRE_",
                          "value": "v"
                      },
                      {
                          "column_name": "friend",
                          "path": "friends*$NUM*name",
                          "privilege": "_VARIABLE_",
                          "default":"_REQUIRE_",
                          "value": "v"
                      },
                      {
                          "column_name": "intimacy",
                          "path": "friends*$NUM*intimacy*$VAL",
                          "privilege": "_VARIABLE_",
                          "default": "",
                          "value": "k"
                      }
                  ]}
        # bd = BuildTable(params,db)
        # actual = bd.extraction(json_list)
        # print("actual is {0}".format(actual))

        bd = BuildTable(params,db)
        # actual = bd.extract_row_value(json_list[0])
        # print(actual)
        res = bd.export_to_db(json_list)
    # @unittest2.skip("")
    def test9_list(self):
        params = {"name": "build_col_test9",
                  "schema": [
                      {
                          "column_name": "id",
                          "path": "id",
                          "privilege": "_CONSTANT_",
                          "default": "_REQUIRE_",
                          "value": "v"
                      },
                      {
                          "column_name": "friend",
                          "path": "friends*$NUM*name",
                          "privilege": "_VARIABLE_",
                          "default":"_REQUIRE_",
                          "value": "v"
                      },
                      {
                          "column_name": "hobby",
                          "path": "friends*$NUM*intimacy*hobby",
                          "privilege": "_VARIABLE_",
                          "default": "",
                          "value": "array",
                          "replace":{
                              "pattern":"$VAL",
                              "sub":"$QUOTg$LT1$GT ==="
                          }
                      }
                  ]}

        bd = BuildTable(params, db)
        # actual = bd.extract_row_value(json_list[0])
        # print(actual)
        res = bd.export_to_db(json_list)

if __name__ == '__main__':
    unittest2.main()


