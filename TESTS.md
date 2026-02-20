# Tests

## Unit Tests

Tests for this product are set up with `pytest`.

### Run Tests With `pytest`

```bash
$ pytest
......................................................                                                                                                                [100%]
54 passed in 0.64s
```

### Run Tests and Display Code Coverage

```bash
$ pytest --cov=fcp7xml_to_unreal
......................................................                                                                                                                [100%]
============================================================================== tests coverage ==============================================================================
_____________________________________________________________ coverage: platform win32, python 3.9.10-final-0 ______________________________________________________________

Name                                                                Stmts   Miss  Cover
---------------------------------------------------------------------------------------
.venv\Lib\site-packages\fcp7xml_to_unreal\__init__.py                  33      6    82%
.venv\Lib\site-packages\fcp7xml_to_unreal\models\Audio.py              41      1    98%
.venv\Lib\site-packages\fcp7xml_to_unreal\models\Episode.py           227     11    95%
.venv\Lib\site-packages\fcp7xml_to_unreal\models\Note.py                8      1    88%
.venv\Lib\site-packages\fcp7xml_to_unreal\models\Shot.py               60      2    97%
.venv\Lib\site-packages\fcp7xml_to_unreal\models\__init__.py            0      0   100%
.venv\Lib\site-packages\fcp7xml_to_unreal\models\helpers.py            26      0   100%
.venv\Lib\site-packages\fcp7xml_to_unreal\xml_helpers\__init__.py       0      0   100%
.venv\Lib\site-packages\fcp7xml_to_unreal\xml_helpers\reports.py      101     19    81%
.venv\Lib\site-packages\fcp7xml_to_unreal\xml_ui.py                    75      1    99%
---------------------------------------------------------------------------------------
TOTAL                                                                 571     41    93%
54 passed in 3.20s
```

### Run Tests and Generate Code Coverage HTML Report

```bash
$ pytest --cov=fcp7xml_to_unreal --cov-report=html
......................................................                                                                                                                [100%]
============================================================================== tests coverage ==============================================================================
_____________________________________________________________ coverage: platform win32, python 3.9.10-final-0 ______________________________________________________________

Coverage HTML written to dir htmlcov
54 passed in 3.40s
```

Open `./htmlcov/index.html` in a web browser to inspect details of the test results.

## Functional Tests

Two sample XML exports from editing applications (and expected filter results) are provided in [./tests/resources](./tests/resources/).

### Test Export from Adobe Premiere

[./tests/resources/test_XML_export_premiere.xml](./tests/resources/test_XML_export_premiere.xml) is from Adobe Premiere. To repeat the filtering on this file, make a copy of the [config file](./src/fcp7xml_to_unreal/config.yaml) in a working directory and uncomment the following lines:

```bash
...
# Here are the values for the Premiere test .xml file
CONFORMSHOT_BURNIN_PREFIX: "Sc_"
CONFORMSCENE_BURNIN_PREFIX: "seq"
```

Run `fcp7xml-to-unreal` from the working directory, and the updated config settings should be honored. Process [./tests/resources/test_XML_export_premiere.xml](./tests/resources/test_XML_export_premiere.xml). The filtering should produce identical results to the provided example filtered file.

### Test Export from DaVinci Resolve

[./tests/resources/test_XML_export_resolve.xml](./tests/resources/test_XML_export_resolve.xml) is from DaVinci Resolve. To repeat the filtering on this file, use the default [config file](./src/fcp7xml_to_unreal/config.yaml) provided. You may need to remove or rename any local copies of `config.yaml`.

Run `fcp7xml-to-unreal` and process [./tests/resources/test_XML_export_resolve.xml](./tests/resources/test_XML_export_resolve.xml). The filtering should produce identical results to the provided example filtered file.
