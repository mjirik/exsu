  
[![Build Status](https://travis-ci.org/mjirik/exsu.svg?branch=master)](https://travis-ci.org/mjirik/exsu)
[![Coverage Status](https://coveralls.io/repos/github/mjirik/exsu/badge.svg?branch=master)](https://coveralls.io/github/mjirik/exsu?branch=master)
[![PyPI version](https://badge.fury.io/py/exsu.svg)](http://badge.fury.io/py/exsu)


# exsu

Experiment support tools prepared for computer vision experiments. 
Output directory and spreadsheet file is managed by package.

* Spreadsheet data and report images are stored into output directory
* Images are reported according a selected severity
* Common spreadseet containing complete history from all output directories can be produced
* Version of particular python package can be reported in the spreadsheet
* Repository status, git hash and dirty files can be reported in the spreadsheet

## Write spreadsheet data

```python
from pathlib import Path
import exsu

outputdir = Path("./test_report/")
commonsheet = Path("./test_report_common_spreadsheet.xlsx")

report = exsu.report.Report(outputdir=outputdir, additional_spreadsheet_fn=commonsheet)
report.add_cols_to_actual_row({"Col1": 25, "Col2": "test string", "Col5": 5})
report.add_cols_to_actual_row({"Col2": "prepsanu", "Col1": 26, "Col4": "ctyrka"})
report.finish_actual_row()

report.add_cols_to_actual_row({"Col1": 27, "Col2": "test string", "Col3": "trojka"})
report.finish_actual_row()

# Save all into `outputdir` and also into `commonsheet`
report.dump()

# new write to common excel
report.init()
report.add_cols_to_actual_row({"Col1": 28, "Col2": "new line to common", "Col7": 77})
report.finish_actual_row()
report.dump()

```

## Write image data

Write image data into output directory

```python
from pathlib import Path
import numpy as np
import exsu

outputdir = Path("./test_report/")
commonsheet = Path("./test_report_common_spreadsheet.xlsx")

fn = "test_image.png"
img = 50 + np.random.rand(100, 100) * 30
img[20:60, 20:60] += 100
img = img.astype(np.uint8)
report = exsu.report.Report(outputdir=outputdir, additional_spreadsheet_fn=commonsheet)
report.imsave(fn, img)
```


## Git repository info

```python
from pathlib import Path
import numpy as np
import exsu
report = exsu.report.Report(repodir=Path(__file__).parent.resolve())
report.finish_actual_row()
report.df
```
Output DataFrame
```
                               repo exsu id  ...  repo exsu dirty files
0  1da301da36cec0fb931f60dd9acca790ec715892  ...      exsu/git_tools.py
```

More than one repositories can be added with `report.add_repo(repodir, reponame=None)`.


## Automatically report versions of selected packages

The version of crucial packages can be reported with the data.

```python
import exsu
report = exsu.report.Report(check_version_of=["numpy", "scipy"])
report.finish_actual_row()
report.df

```
