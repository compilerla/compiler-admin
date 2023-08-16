# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/compilerla/compiler-admin/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                     |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|----------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| compiler\_admin/\_\_init\_\_.py          |        5 |        2 |        0 |        0 |     60% |       5-7 |
| compiler\_admin/commands/\_\_init\_\_.py |        2 |        0 |        0 |        0 |    100% |           |
| compiler\_admin/commands/convert.py      |       36 |        0 |       22 |        1 |     98% |    58->66 |
| compiler\_admin/commands/create.py       |       13 |        0 |        2 |        0 |    100% |           |
| compiler\_admin/commands/delete.py       |       10 |        0 |        2 |        0 |    100% |           |
| compiler\_admin/commands/info.py         |        9 |        0 |        0 |        0 |    100% |           |
| compiler\_admin/commands/init.py         |       31 |        0 |       12 |        1 |     98% |    20->17 |
| compiler\_admin/commands/offboard.py     |       37 |        2 |       10 |        1 |     94% |     63-64 |
| compiler\_admin/commands/restore.py      |       13 |        0 |        2 |        0 |    100% |           |
| compiler\_admin/commands/signout.py      |       10 |        0 |        2 |        0 |    100% |           |
| compiler\_admin/main.py                  |       54 |        1 |       22 |        2 |     96% |80->exit, 85 |
| compiler\_admin/services/\_\_init\_\_.py |        0 |        0 |        0 |        0 |    100% |           |
| compiler\_admin/services/google.py       |       58 |        0 |       18 |        0 |    100% |           |
|                                **TOTAL** |  **278** |    **5** |   **92** |    **5** | **97%** |           |


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