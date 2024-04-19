# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/compilerla/compiler-admin/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                        |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|-------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| compiler\_admin/\_\_init\_\_.py             |        7 |        2 |        0 |        0 |     71% |      8-10 |
| compiler\_admin/commands/\_\_init\_\_.py    |        0 |        0 |        0 |        0 |    100% |           |
| compiler\_admin/commands/convert.py         |       43 |        0 |       26 |        1 |     99% |    66->74 |
| compiler\_admin/commands/create.py          |       21 |        0 |        6 |        0 |    100% |           |
| compiler\_admin/commands/delete.py          |       18 |        0 |        8 |        1 |     96% |    24->30 |
| compiler\_admin/commands/info.py            |        8 |        0 |        0 |        0 |    100% |           |
| compiler\_admin/commands/init.py            |       36 |        0 |       14 |        1 |     98% |    21->18 |
| compiler\_admin/commands/offboard.py        |       47 |        2 |       16 |        2 |     94% |42->48, 75-76 |
| compiler\_admin/commands/reset\_password.py |       19 |        0 |        6 |        0 |    100% |           |
| compiler\_admin/commands/restore.py         |       16 |        0 |        4 |        0 |    100% |           |
| compiler\_admin/commands/signout.py         |       18 |        0 |        8 |        1 |     96% |    24->30 |
| compiler\_admin/main.py                     |       63 |        1 |       24 |        2 |     97% |96->exit, 101 |
| compiler\_admin/services/\_\_init\_\_.py    |        0 |        0 |        0 |        0 |    100% |           |
| compiler\_admin/services/google.py          |       75 |        2 |       26 |        1 |     97% |   115-116 |
|                                   **TOTAL** |  **371** |    **7** |  **138** |    **9** | **97%** |           |


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