# Tests

Tests for this product are set up with `pytest`.

## Run Tests With `pytest`

```bash
$ pytest
......................................................                                                                                                                [100%]
54 passed in 0.64s
```

## Run Tests and Display Code Coverage

```bash
pytest --cov=premiere_to_ue
......................................................                                                                                                                [100%]
============================================================================== tests coverage ==============================================================================
_____________________________________________________________ coverage: platform win32, python 3.9.10-final-0 ______________________________________________________________

Name                                                             Stmts   Miss  Cover
------------------------------------------------------------------------------------
.venv\Lib\site-packages\premiere_to_ue\__init__.py                  33      6    82%
.venv\Lib\site-packages\premiere_to_ue\models\Audio.py              41      1    98%
.venv\Lib\site-packages\premiere_to_ue\models\Episode.py           227     11    95%
.venv\Lib\site-packages\premiere_to_ue\models\Note.py                8      1    88%
.venv\Lib\site-packages\premiere_to_ue\models\Shot.py               60      2    97%
.venv\Lib\site-packages\premiere_to_ue\models\__init__.py            0      0   100%
.venv\Lib\site-packages\premiere_to_ue\models\helpers.py            26      0   100%
.venv\Lib\site-packages\premiere_to_ue\xml_helpers\__init__.py       0      0   100%
.venv\Lib\site-packages\premiere_to_ue\xml_helpers\reports.py      101     19    81%
.venv\Lib\site-packages\premiere_to_ue\xml_ui.py                    75      1    99%
------------------------------------------------------------------------------------
TOTAL                                                              571     41    93%
54 passed in 3.05s
```

## Run Tests and Generate Code Coverage HTML Report

```bash
$ pytest --cov=premiere_to_ue --cov-report=html
......................................................                                                                                                                [100%]
============================================================================== tests coverage ==============================================================================
_____________________________________________________________ coverage: platform win32, python 3.9.10-final-0 ______________________________________________________________

Coverage HTML written to dir htmlcov
54 passed in 3.25s
```

Open ./htmlcov/index.html in a web browser to inspect details of the test results.
