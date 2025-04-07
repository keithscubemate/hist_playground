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
def _(json):
    data = {}
    with open("./pretty_trash.json", 'r', encoding='utf-16') as fin:
        _file_data = fin.read()
        data = json.loads(_file_data)
    
    for _d in data:
        _d["Comment"] = _d["ft"][0]["Comment"]
    return data, fin


@app.cell
def _(data):
    from histogram import Histogram, bytes_to_arr
    import base64
    from copy import deepcopy

    def last_continuous_zero(d):
        i = 0
        while i < len(d) and d[i] == 0:
            i += 1
        return i

    new_data = []

    for _d in data:
        _new_d = deepcopy(_d)
        _arr = base64.b64decode(_d["TrashHistogram"])
        _a_int = bytes_to_arr(_arr, 4)[:400]
        _hist = Histogram.from_array(_a_int, 10)
        _new_d["TrashHistogram"] = _hist
        _new_d["last_continuous_zero"] = last_continuous_zero(_hist.hist) * 10

        new_data.append(_new_d)
    return (
        Histogram,
        base64,
        bytes_to_arr,
        deepcopy,
        last_continuous_zero,
        new_data,
    )


@app.cell
def _(last_continuous_zero, new_data):
    vals_by_comment = {}

    for _d in new_data:
        comment = _d["Comment"]
        val = _d["TotalTrashSize"]
        if comment not in vals_by_comment:
            vals_by_comment[comment] = [val]
        else:
            vals_by_comment[comment] += [val]

    def avg(d):
        if len(d) < 1: 
            return 0
        return sum(d) / len(d)

    avg_by_comment = {c: avg(v) for c, v in vals_by_comment.items()}

    no_align_avg = avg_by_comment["aj-salt-trash-no-align"]
    no_align_min_hist_bin = [
        last_continuous_zero(_d["TrashHistogram"].hist)
        for _d in new_data
    ]


    for comm, val in avg_by_comment.items():
        real_m = val / no_align_avg
        real_b = val - no_align_avg

        result = {
            "avg": val,
            "real_m": real_m,
            "real_b": real_b
        }

        avg_by_comment[comm] = result
    return (
        avg,
        avg_by_comment,
        comm,
        comment,
        no_align_avg,
        no_align_min_hist_bin,
        real_b,
        real_m,
        result,
        val,
        vals_by_comment,
    )


@app.cell
def _(avg_by_comment):
    avg_by_comment
    return


@app.cell
def _(new_data, pd):
    samples = pd.DataFrame(new_data)
    return (samples,)


@app.cell
def _(samples):
    samples
    return


@app.cell
def _(mo, new_data):
    data_len = len(new_data[0]["TrashHistogram"].hist)

    slider = mo.ui.slider(start=0, stop=len(new_data) - 1, value=0)
    bin_range_slider = mo.ui.slider(start=1, stop=data_len - 1, value=1)
    return bin_range_slider, data_len, slider


@app.cell
def _(alt, mo, new_data, pd, slider):
    _data = new_data[slider.value]["TrashHistogram"].hist

    _frame_data = pd.DataFrame({'bin': range(len(_data)), 'numbers': _data})

    hist_chart =  alt.Chart(_frame_data).mark_bar().encode(
        alt.X('bin:O', title='Bin (Index)'),
        alt.Y('numbers:Q', title='Height')
    )

    mo.vstack([
        mo.hstack([slider, mo.md(f"Has value: {slider.value}")]),
        hist_chart
    ])
    return (hist_chart,)


@app.cell
def _(alt, data, mo, samples):
    ids = list(set(_d["testid"] for _d in data))

    min_id = min(ids) - 1
    max_id = max(ids) + 1

    chart = mo.ui.altair_chart(alt.Chart(samples).mark_point().encode(
        x='TotalTrashSize',
        y='last_continuous_zero',
        color='Comment'
    ))
    return chart, ids, max_id, min_id


@app.cell
def _(chart):
    chart
    return


if __name__ == "__main__":
    app.run()
