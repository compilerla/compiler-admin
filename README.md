# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/compilerla/compiler-admin/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                          |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|---------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| compiler\_admin/\_\_init\_\_.py               |        7 |        2 |        0 |        0 |     71% |      8-10 |
| compiler\_admin/api/toggl.py                  |       56 |        0 |        0 |        0 |    100% |           |
| compiler\_admin/commands/\_\_init\_\_.py      |        0 |        0 |        0 |        0 |    100% |           |
| compiler\_admin/commands/info.py              |        9 |        0 |        0 |        0 |    100% |           |
| compiler\_admin/commands/init.py              |       34 |        0 |       10 |        1 |     98% |    20->17 |
| compiler\_admin/commands/time/\_\_init\_\_.py |       12 |        1 |        0 |        0 |     92% |        12 |
| compiler\_admin/commands/time/convert.py      |       24 |        0 |        2 |        0 |    100% |           |
| compiler\_admin/commands/time/download.py     |       44 |        0 |       14 |        0 |    100% |           |
| compiler\_admin/commands/time/lock.py         |       14 |        0 |        2 |        0 |    100% |           |
| compiler\_admin/commands/time/verify.py       |       88 |        4 |       48 |        8 |     91% |37, 39, 41, 42->45, 45->54, 54->66, 102->exit, 108 |
| compiler\_admin/commands/user/\_\_init\_\_.py |       24 |        1 |        0 |        0 |     96% |        18 |
| compiler\_admin/commands/user/backupcodes.py  |       12 |        0 |        2 |        0 |    100% |           |
| compiler\_admin/commands/user/convert.py      |       37 |        0 |       20 |        1 |     98% |    52->60 |
| compiler\_admin/commands/user/create.py       |       20 |        0 |        4 |        0 |    100% |           |
| compiler\_admin/commands/user/deactivate.py   |       44 |        2 |       10 |        1 |     94% |     43-44 |
| compiler\_admin/commands/user/delete.py       |       18 |        0 |        6 |        1 |     96% |    18->24 |
| compiler\_admin/commands/user/offboard.py     |       49 |        2 |       14 |        2 |     94% |34->40, 68-69 |
| compiler\_admin/commands/user/reactivate.py   |       45 |        0 |       12 |        0 |    100% |           |
| compiler\_admin/commands/user/reset.py        |       25 |        0 |        8 |        0 |    100% |           |
| compiler\_admin/commands/user/restore.py      |       15 |        0 |        2 |        0 |    100% |           |
| compiler\_admin/commands/user/signout.py      |       18 |        0 |        6 |        1 |     96% |    18->24 |
| compiler\_admin/main.py                       |       16 |        2 |        2 |        1 |     83% |    14, 23 |
| compiler\_admin/services/\_\_init\_\_.py      |        0 |        0 |        0 |        0 |    100% |           |
| compiler\_admin/services/files.py             |       31 |        0 |        4 |        1 |     97% |    37->40 |
| compiler\_admin/services/google.py            |      101 |        2 |       28 |        1 |     98% |   136-137 |
| compiler\_admin/services/harvest.py           |       47 |        0 |        6 |        0 |    100% |           |
| compiler\_admin/services/time.py              |       39 |       10 |       28 |       10 |     70% |20, 23, 25, 27, 32, 35, 38, 41, 43, 46 |
| compiler\_admin/services/toggl.py             |      119 |        0 |       22 |        1 |     99% |    76->82 |
|                                     **TOTAL** |  **948** |   **26** |  **250** |   **29** | **95%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/compilerla/compiler-admin/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/compilerla/compiler-admin/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/compilerla/compiler-admin/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/compilerla/compiler-admin/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fcompilerla%2Fcompiler-admin%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/compilerla/compiler-admin/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.