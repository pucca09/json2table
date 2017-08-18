<link href="http://kevinburke.bitbucket.org/markdowncss/markdown.css" rel="stylesheet"></link>

# json2table
flattens the nested json object, extracts the properties into a csv format and restore into MongoDB collection

### Installation
```
python setup.py install
```

# json2table

## TEMPLATE

First of all, you need to provide a template describing the schema of the collection(table)


```
template = {"name": "build_col_test9",
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

* **"name"** : MongoDB collection name
* **"schema"**:schema for MongoDB collection
* **"schema"-"column_name"**: column name
* **"schema"-"path"**: join by "*"
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
                     "hobby":["sing"],
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
#only extration
table_records = bd.extraction(json_list)
#extraction values and export to MongoDB
tabel_records = bd.export_to_db(json_list)

```

#### Example1
Template:
```
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
```
Results:

<table class="table table-bordered table-striped table-condensed">
    <tr>
        <td>id</td>
        <td>first_name</td>
        <td>age</td>
    </tr>
    <tr>
        <td>1</td>
      <td>john</td>
        <td>27</td>
    </tr>
    <tr>
        <td>2</td>
        <td>scott</td>
        <td>29</td>
    </tr>
    <tr>
        <td>3</td>
        <td>tom</td>
        <td>10</td>
    </tr>
</table>

#### Example2
Template:

```
template = {"name":"build_col_test2",
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

<table class="table table-bordered table-striped table-condensed">
    <tr>
        <td>id</td>
        <td>first_name</td>
        <td>age</td>
        <td>company</td>
    </tr>
    <tr>
        <td>1</td>
        <td>john</td>
        <td>27</td>
        <td>ibm</td>
    </tr>
    <tr>
        <td>2</td>
        <td>scott</td>
        <td>29</td>
        <td>ibm</td>
    </tr>
    <tr>
        <td>3</td>
        <td>tom</td>
        <td>10</td>
        <td>ibm</td>
    </tr>

</table>

#### Example3
Template:

```
template = {"name": "build_col_test3",
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

<table class="table table-bordered table-striped table-condensed">
    <tr>
        <td>id</td>
        <td>language</td>
    </tr>
    <tr>
        <td>1</td>
        <td>c#</td>

    </tr>
    <tr>
        <td>1</td>
        <td>python</td>

    </tr>
    <tr>
        <td>1</td>
        <td>go</td>
    </tr>

    <tr>
        <td>2</td>
        <td>c++</td>

    </tr>
    <tr>
        <td>2</td>
        <td>python</td>

    </tr>
    <tr>
        <td>2</td>
        <td>vb</td>

    </tr>
     <tr>
        <td>3</td>
        <td>java</td>

    </tr>
    <tr>
        <td>3</td>
        <td>scala</td>

    </tr>

</table>


#### Example4
Template:
```
template = {"name": "build_col_test4",
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

<table class="table table-bordered table-striped table-condensed">
    <tr>
        <td>id</td>
        <td>language</td>
        <td>grade</td>
    </tr>
    <tr>
        <td>1</td>
        <td>c#</td>
        <td>80</td>

    </tr>
    <tr>
        <td>1</td>
        <td>python</td>
       <td>81</td>
    </tr>
    <tr>
        <td>1</td>
        <td>go</td>
        <td>82</td>
    </tr>

    <tr>
        <td>2</td>
        <td>c++</td>
        <td>90</td>

    </tr>
    <tr>
        <td>2</td>
        <td>python</td>
        <td>85</td>
    </tr>
    <tr>
        <td>2</td>
        <td>vb</td>
        <td>82</td>
    </tr>
     <tr>
        <td>3</td>
        <td>java</td>
        <td>90</td>

    </tr>
    <tr>
        <td>3</td>
        <td>scala</td>
        <td>85</td>

    </tr>

</table>

#### Example5
Template:

```
template = {"name": "build_col_test5",
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

<table class="table table-bordered table-striped table-condensed">
    <tr>
        <td>id</td>
        <td>language</td>
        <td>grade</td>
    </tr>
    <tr>
        <td>1</td>
        <td>c#</td>
        <td>80 point</td>

    </tr>
    <tr>
        <td>1</td>
        <td>python</td>
       <td>81 point</td>
    </tr>
    <tr>
        <td>1</td>
        <td>go</td>
        <td>82 point</td>
    </tr>

    <tr>
        <td>2</td>
        <td>c++</td>
        <td>90 point</td>

    </tr>
    <tr>
        <td>2</td>
        <td>python</td>
        <td>85 point</td>
    </tr>
    <tr>
        <td>2</td>
        <td>vb</td>
        <td>82 point</td>
    </tr>
     <tr>
        <td>3</td>
        <td>java</td>
        <td>90 point</td>

    </tr>
    <tr>
        <td>3</td>
        <td>scala</td>
        <td>85 point</td>

    </tr>

</table>

####Example6
Template:
```
template = {"name": "build_col_test6",
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

<table class="table table-bordered table-striped table-condensed">
    <tr>
        <td>id</td>
        <td>friend</td>

    </tr>
    <tr>
        <td>1</td>
        <td>peter</td>

    </tr>
    <tr>
        <td>1</td>
        <td>rose</td>
    </tr>

    <tr>
        <td>2</td>
        <td>henry</td>

    </tr>
    <tr>
        <td>2</td>
        <td>jane</td>
    </tr>

   
</table>
|Tables         | Are           | Cool  |
| ------------- |:-------------:| -----:|
| col 3 is      | right-aligned | $1600 |
| col 2 is      | centered      |   $12 |
| zebra stripes | are neat      |    $1 |