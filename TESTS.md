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
................................                                                                                                                                                                               [100%]
```

### Run Tests and Generate Code Coverage HTML Report

```bash
$ pytest --cov=fcp7xml_to_unreal --cov-report=html
................................                                                                                                                                                                               [100%]

Coverage HTML written to dir htmlcov
54 passed in 3.25s
```

Open ./htmlcov/index.html in a web browser to inspect details of the test results.

## Functional Tests

Two sample XML exports from editing applications (and expected filter results) are provided in [./tests/resources](./tests/resources/).

### Test Export from Adobe Premiere

[./tests/resources/test_XML_export_premiere.xml](./tests/resources/test_XML_export_premiere.xml) is from Adobe Premiere. To repeat the filtering on this file, make a copy of the [config file](./src/premiere_to_ue/config.yaml) in a working directory and uncomment the following lines:

```bash
...
# Here are the values for the Premiere test .xml file
CONFORMSHOT_BURNIN_PREFIX: "Sc_"
CONFORMSCENE_BURNIN_PREFIX: "seq"
```

Run `premiere-to-ue` from the working directory, and the updated config settings should be honored. Process [./tests/resources/test_XML_export_premiere.xml](./tests/resources/test_XML_export_premiere.xml). The filtering should produce identical results to the provided example filtered file.

### Test Export from DaVinci Resolve

[./tests/resources/test_XML_export_resolve.xml](./tests/resources/test_XML_export_resolve.xml) is from DaVinci Resolve. To repeat the filtering on this file, use the default [config file](./src/premiere_to_ue/config.yaml) provided. You may need to remove or rename any local copies of `config.yaml`.

Run `premiere-to-ue` and process [./tests/resources/test_XML_export_resolve.xml](./tests/resources/test_XML_export_resolve.xml). The filtering should produce identical results to the provided example filtered file.
