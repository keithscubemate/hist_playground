import marimo

__generated_with = "0.11.23"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    return (mo,)


@app.cell
async def _():
    import pandas as pd
    import numpy as np
    import micropip
    import json
    await micropip.install('altair')
    import altair as alt
    return alt, json, micropip, np, pd


@app.cell
def _(mo):
    mo.md(r"""# Data Import and Process""")
    return


@app.cell
def _(json):
    original_data = {}
    with open("./pretty_lmf.json", 'r', encoding='utf-16') as fin:
        _file_data = fin.read()
        original_data = json.loads(_file_data)
    return fin, original_data


@app.cell
def _(original_data):
    from histogram import Histogram, bytes_to_arr
    import base64
    from copy import deepcopy

    processed_data = []
    hist_data = []

    def b64_to_hist(b64: str, width: int, bin_size: int) -> Histogram:
        _arr = base64.b64decode(b64)
        _a_int = bytes_to_arr(_arr, 4)[:width]
        _hist = Histogram.from_array(_a_int, bin_size)
        return _hist


    for _d in original_data:
        _new_d = {}
        _other_d = {}

        # grab data to persist
        if (comm := _d["Comment"]) == "":
            _new_d["Comment"] = "no align"
        else:
            _new_d["Comment"] = _d["Comment"]
        _new_d["TestId"] = _d["TestId"]
        _new_d["SampleNumber"] = _d["SampleNumber"]
        _new_d["LnMetric"] = _d["LnMetric"]
        _new_d["LnImperial"] = _d["LnImperial"]
        _new_d["Fineness"] = _d["Fineness"]
        _new_d["MaturityRatio1"] = _d["MaturityRatio1"]
        _new_d["ThetaAverage"] = b64_to_hist(_d["Maturity1Histogram"], 20, 0.05).mean()

        # convert histograms
        if (comm := _d["Comment"]) == "":
            _other_d["Comment"] = "no align"
        else:
            _other_d["Comment"] = _d["Comment"]
        _other_d["TestId"] = _d["TestId"]
        _other_d["LengthHistogramMetric"] = b64_to_hist(_d["LengthHistogramMetric"], 60, 1)
        _other_d["LengthHistogramImperial"] = b64_to_hist(_d["LengthHistogramImperial"], 80, 1/32)
        _other_d["FinenessHistogram"] = b64_to_hist(_d["FinenessHistogram"], 20, 25)
        _other_d["Maturity1Histogram"] = b64_to_hist(_d["Maturity1Histogram"], 20, 0.05)

        processed_data.append(_new_d)
        hist_data.append(_other_d)
    return (
        Histogram,
        b64_to_hist,
        base64,
        bytes_to_arr,
        comm,
        deepcopy,
        hist_data,
        processed_data,
    )


@app.cell
def _(mo):
    mo.md(r"""# Graphs""")
    return


@app.cell
def _(mo):
    mo.md(r"""## Processing""")
    return


@app.cell
def _(original_data, pd, processed_data):
    samples = pd.DataFrame(processed_data)

    _ids = [_d["TestId"] for _d in original_data]

    max_id = max(_ids) + 1
    min_id = min(_ids) - 1
    return max_id, min_id, samples


@app.cell
def _(alt, max_id, min_id, mo, samples):
    len_chart = mo.ui.altair_chart(alt.Chart(samples).mark_point().encode(
        y='LnMetric',
        x=alt.X('TestId',scale=alt.Scale(domain=[min_id, max_id])),
        color='Comment'
    ))
    return (len_chart,)


@app.cell
def _(alt, max_id, min_id, mo, samples):
    mat_chart = mo.ui.altair_chart(alt.Chart(samples).mark_point().encode(
        y='MaturityRatio1',
        x=alt.X('TestId',scale=alt.Scale(domain=[min_id, max_id])),
        color='Comment'
    ))

    theta_chart = mo.ui.altair_chart(alt.Chart(samples).mark_point().encode(
        y='ThetaAverage',
        x=alt.X('TestId',scale=alt.Scale(domain=[min_id, max_id])),
        color='Comment'
    ))
    return mat_chart, theta_chart


@app.cell
def _(alt, max_id, min_id, mo, samples):
    fine_chart = mo.ui.altair_chart(alt.Chart(samples).mark_point().encode(
        y='Fineness',
        x=alt.X('TestId',scale=alt.Scale(domain=[min_id, max_id])),
        color='Comment'
    ))
    return (fine_chart,)


@app.cell
def _(mo):
    mo.md(r"""# Just Graphs""")
    return


@app.cell
def _(len_chart, mo):
    mo.vstack(
        [
            mo.md("### Len"),
            len_chart,
        ]
    )
    return


@app.cell
def _(mat_chart, mo, theta_chart):
    mo.vstack(
        [
            mo.md("### Maturity"),
            theta_chart,
            mat_chart,
        ]
    )
    return


@app.cell
def _(fine_chart, mo):
    mo.vstack(
        [
            mo.md("### Fineness"),
            fine_chart,
        ]
    )
    return


@app.cell
def _(mo):
    mo.md("""## Histogram Viewer""")
    return


@app.cell
def _(mo):
    radiogroup = mo.ui.radio(
        options=[
            "LengthHistogramMetric",
            "LengthHistogramImperial",
            "FinenessHistogram",
            "Maturity1Histogram",
        ],
        value="LengthHistogramMetric",
        label="choose one"
    )
    return (radiogroup,)


@app.cell
def _(hist_data, mo):
    slider = mo.ui.slider(start=0, stop=len(hist_data) - 1, value=0)
    return (slider,)


@app.cell
def _(alt, hist_data, mo, pd, radiogroup, slider):
    _na_data = hist_data[2][radiogroup.value].hist
    _na_id = hist_data[2]["TestId"]
    _na_comment = hist_data[2]["Comment"]
    _data = hist_data[slider.value][radiogroup.value].hist
    _id = hist_data[slider.value]["TestId"]
    _comment = hist_data[slider.value]["Comment"]

    _na_frame_data = pd.DataFrame({'bin': range(len(_na_data)), 'numbers': _na_data})
    _frame_data = pd.DataFrame({'bin': range(len(_data)), 'numbers': _data})

    na_hist_chart =  alt.Chart(_na_frame_data).mark_bar().encode(
        alt.X('bin:O', title='Bin (Index)'),
        alt.Y('numbers:Q', title='Height')
    )

    hist_chart =  alt.Chart(_frame_data).mark_bar().encode(
        alt.X('bin:O', title='Bin (Index)'),
        alt.Y('numbers:Q', title='Height')
    )

    mo.vstack([
        radiogroup,
        mo.hstack([slider, mo.md(f"Has value: {slider.value}")]),
        mo.md(f"### {_id}:{_comment}"),
        hist_chart,
        mo.md(f"### {_na_id}:{_na_comment}"),
        na_hist_chart,
    ])
    return hist_chart, na_hist_chart


if __name__ == "__main__":
    app.run()
