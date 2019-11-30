  
[![Build Status](https://travis-ci.org/mjirik/exsu.svg?branch=master)](https://travis-ci.org/mjirik/exsu)
[![Coverage Status](https://coveralls.io/repos/github/mjirik/exsu/badge.svg?branch=master)](https://coveralls.io/github/mjirik/exsu?branch=master)
[![PyPI version](https://badge.fury.io/py/exsu.svg)](http://badge.fury.io/py/exsu)


# exsu

Experiment support tools prepared for computer vision experiments. 
Output directory and spreadsheet file is managed by package.

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
