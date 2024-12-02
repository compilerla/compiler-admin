# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/compilerla/compiler-admin/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                          |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|---------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| compiler\_admin/\_\_init\_\_.py               |        7 |        2 |        0 |        0 |     71% |      8-10 |
| compiler\_admin/api/toggl.py                  |       44 |        0 |        0 |        0 |    100% |           |
| compiler\_admin/commands/\_\_init\_\_.py      |        0 |        0 |        0 |        0 |    100% |           |
| compiler\_admin/commands/info.py              |        8 |        0 |        0 |        0 |    100% |           |
| compiler\_admin/commands/init.py              |       36 |        0 |       12 |        1 |     98% |    21->18 |
| compiler\_admin/commands/time/\_\_init\_\_.py |        9 |        0 |        2 |        0 |    100% |           |
| compiler\_admin/commands/time/convert.py      |       16 |        0 |        4 |        0 |    100% |           |
| compiler\_admin/commands/time/download.py     |       15 |        0 |        8 |        0 |    100% |           |
| compiler\_admin/commands/user/\_\_init\_\_.py |       15 |        0 |        2 |        0 |    100% |           |
| compiler\_admin/commands/user/alumni.py       |       45 |        0 |       10 |        0 |    100% |           |
| compiler\_admin/commands/user/convert.py      |       46 |        0 |       28 |        1 |     99% |    71->79 |
| compiler\_admin/commands/user/create.py       |       21 |        0 |        6 |        0 |    100% |           |
| compiler\_admin/commands/user/delete.py       |       18 |        0 |        8 |        1 |     96% |    24->30 |
| compiler\_admin/commands/user/offboard.py     |       45 |        2 |       14 |        2 |     93% |42->48, 72-73 |
| compiler\_admin/commands/user/reset.py        |       24 |        0 |       10 |        0 |    100% |           |
| compiler\_admin/commands/user/restore.py      |       16 |        0 |        4 |        0 |    100% |           |
| compiler\_admin/commands/user/signout.py      |       18 |        0 |        8 |        1 |     96% |    24->30 |
| compiler\_admin/main.py                       |       94 |        2 |        6 |        2 |     96% |  205, 209 |
| compiler\_admin/services/\_\_init\_\_.py      |        0 |        0 |        0 |        0 |    100% |           |
| compiler\_admin/services/files.py             |       31 |        0 |        4 |        1 |     97% |    37->40 |
| compiler\_admin/services/google.py            |       76 |        2 |       22 |        1 |     97% |   116-117 |
| compiler\_admin/services/harvest.py           |       32 |        0 |        2 |        0 |    100% |           |
| compiler\_admin/services/toggl.py             |       65 |        1 |       14 |        3 |     95% |49, 132->134, 134->137 |
|                                     **TOTAL** |  **681** |    **9** |  **164** |   **13** | **97%** |           |


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