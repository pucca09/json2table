<link href="http://kevinburke.bitbucket.org/markdowncss/markdown.css" rel="stylesheet"></link>

# json2table
flattens the nested json object, convert an array of non-hierarchial json objects to table-format data

### Installation
```
python setup.py install
```

# json2table

## TEMPLATE

First of all, you need to provide a template describing the schema of the collection(table)


```
template = {
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
                      },
                      {
                          "column_name": "intimacy",
                          "path": "friends*$NUM*intimacy*$VAL",
                          "privilege": "_VARIABLE_",
                          "default": "",
                          "value": "k"
                      }
                  ]}
```

#### Anotation

* **"schema"**:schema for a table-format data
* **"schema"-"column_name"**: column name
* **"schema"-"path"**: json path joined with "*"
* **"schema"-"privilege"**:if the path doesn't include variable symbol such as $VAL,$NUM, then the privilege of the column is '_CONSTANT_',else '_VARIABLE_'
* **"schema"-"default"**: fill the missing value with default value, unless the type being '_REQUIRE_'. If "default" is set to be '_REQUIRE_',rows with this column value missed will be deleted
* **"schema"-"value"**:extract the column value from json key or value. 'k' stands for json key,'v' for single value,'array' for values list
* **"schema"-"replace"**:use regular expression to subtitute the extracted column value. 'pattern' represents the regular expression,"sub" represents the subtitute string

The json format does not support some special characters, so some symbols are defined to represent these special characters.

+ **$VAL** => regexr:"([^\*]+)"
+ **$NUM** => regexr: "(\d+)"
+ **$SPACE"**=> regexr: "\s"
+ **$NOT_SPACE** => regexr:"\S"
+ **$QUOT** => "\\"
+ **$GT** => ">"
+ **$LT** => "<"


## Data
Data is provided with a list of dict. You can use the function of JSON module to load data from json file

```
    json_list = [
    {
        "id": "1",
        "name": {
            "first": "john",
            "last": "johnson"
        },
        "age": "7",
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
                 "hobby":["swimming","football"],
                 "age_diff":"2"
                }
             },
            {"name":"rose",
                 "intimacy":{
                     "hobby":["swimming"],
                     "age_diff":"3"
                    }
                 }
        ]
     },
     {
        "id": "2",
        "name": {
            "first": "scott",
            "middle": "scottster",
            "last": "scottson"
        },
        "age": "29",
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
                     "hobby":["singing"],
                     "age_diff":"3"
                    }
                 }
        ]
     },
    {
        "id": "3",
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

```
## USAGE

```
from json2table.building import BuildTable
bd = BuildTabel(template) #create instance with template
json_list = json.load(open('data\example',"w"))
#extration
table_records = bd.extraction(json_list)

```
After extraction, you can export data to DB or transform into Pandas.Dataframe
```
# Assume that 'db' is an instance of pymongo client
db[collection_name].insert_many(table_records)
# Transform into Pandas.Dataframe
import pandas as pds
df = pds.Dataframe(table_records)
```
#### Example1
Template:
```
params = {
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
```
Results:

id | first_name | age
-- | ---------|------
1 | john | 27
2 | scott | 29
3 | tom | 10


#### Example2
Template:

```
template = {
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
```
Results:

id | first_name | age | company
-- | ---------|----|-----
1 | john | 27 | ibm
2 | scott | 29 | ibm
3 | tom | 10 | ibm


#### Example3
Template:

```
template = {
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
```
Results:

id | language
------------ | -------------
1 | c#
1 | python
1 | go
2 | c++
2 | python
2 | vb
3 | java
2 | scala


#### Example4
Template:
```
template = {
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
```
Results:

id | language | grade
-- | ---------|------
1 | c# | 80
1 | python | 81
1 | go | 82
2 | c++ | 90
2 | python | 85
2 | vb | 82
3 | java | 90
2 | scala | 85

#### Example5
Template:

```
template = {
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
                          "default":"",
                          "replace":{
                              "pattern":"$VAL",
                              "sub":"$QUOTg$LT1$GT point"
                          },
                          "value": "v"
                      }
                  ]}
```
Results:

id | language | grade
-- | ---------|------
1 | c# | 80 point
1 | python | 81 point
1 | go | 82 point
2 | c++ | 90 point
2 | python | 85 point
2 | vb | 82 point
3 | java | 90 point
2 | scala | 85 point

#### Example6
Template:

```
template = {
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
```
Results:

id | friend
------------ | -------------
1 | peter
1 | rose
2 | henry
2 | jane

#### Example7
Template:

```
template = {
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
```
Results:

id | friend | hobby
------------ | ------------- | ---------
1 | peter | ["swimming","football"]
1 | rose | ["swimming"]
2 | henry | ["dance","football"]
2 | jane | ["singing"]
