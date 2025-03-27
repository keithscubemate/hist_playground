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
    import micropip
    import json
    await micropip.install('altair')
    import altair as alt
    return alt, json, micropip, pd


@app.cell
def _(json):
    data = ""
    with open("./pretty_trash.json", 'r', encoding='utf-16') as fin:
        _file_data = fin.read()
        data = json.loads(_file_data)
    return data, fin


@app.cell
def _(data):
    for d in data:
        d["Comment"] = d["ft"][0]["Comment"]
    return (d,)


@app.cell
def _(data):
    data
    return


@app.cell
def _(data, pd):
    samples = pd.DataFrame(data)
    return (samples,)


@app.cell
def _(alt, mo, samples):
    chart = mo.ui.altair_chart(alt.Chart(samples).mark_point().encode(
        x='TotalTrashSize',
        y='testid',
        color='Comment'
    ))
    return (chart,)


@app.cell
def _(chart):
    chart
    return


if __name__ == "__main__":
    app.run()
