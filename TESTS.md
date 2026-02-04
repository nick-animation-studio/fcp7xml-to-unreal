# Tests

Tests for this product are set up with `pytest`.

## Run Tests With `pytest`

```bash
$ pytest
................................                                                                                                                                                                               [100%]
32 passed in 2.90s
```

## Run Tests and Display Code Coverage

```bash
$ pytest --cov=fcp7xml_to_unreal
................................                                                                                                                                                                               [100%]
================================================================================================== tests coverage ===================================================================================================
__________________________________________________________________________________ coverage: platform win32, python 3.9.10-final-0 __________________________________________________________________________________

Name                                                               Stmts   Miss  Cover
--------------------------------------------------------------------------------------
.venv\Lib\site-packages\fcp7xml_to_unreal\__init__.py                    19      0   100%
.venv\Lib\site-packages\fcp7xml_to_unreal\models\Audio.py                40      1    98%
.venv\Lib\site-packages\fcp7xml_to_unreal\models\Episode.py             234     97    59%
.venv\Lib\site-packages\fcp7xml_to_unreal\models\Note.py                  7      0   100%
.venv\Lib\site-packages\fcp7xml_to_unreal\models\Shot.py                 48      0   100%
.venv\Lib\site-packages\fcp7xml_to_unreal\models\__init__.py              0      0   100%
.venv\Lib\site-packages\fcp7xml_to_unreal\models\helpers.py              25      0   100%
.venv\Lib\site-packages\fcp7xml_to_unreal\xml_helpers\__init__.py         0      0   100%
.venv\Lib\site-packages\fcp7xml_to_unreal\xml_helpers\reports.py        126     37    71%
.venv\Lib\site-packages\fcp7xml_to_unreal\xml_helpers\syncsketch.py      91     26    71%
.venv\Lib\site-packages\fcp7xml_to_unreal\xml_ui.py                      97     31    68%
--------------------------------------------------------------------------------------
TOTAL                                                                687    192    72%
32 passed in 4.06s
```

## Run Tests and Generate Code Coverage HTML Report

```bash
$ pytest --cov=fcp7xml_to_unreal --cov-report=html
................................                                                                                                                                                                               [100%]
================================================================================================== tests coverage ===================================================================================================
__________________________________________________________________________________ coverage: platform win32, python 3.9.10-final-0 __________________________________________________________________________________

Coverage HTML written to dir htmlcov
32 passed in 5.39s
```

Open ./htmlcov/index.html in a web browser to inspect details of the test results.
