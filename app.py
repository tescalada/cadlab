from flask import Flask, request, send_from_directory, render_template
import cadquery as cq
import logging

from jupyter_cadquery.cadquery import show
from ipywidgets.embed import embed_data

import importlib
import glob
import os
from pathlib import Path


app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
app.config.from_pyfile("config.cfg")
app.logger.setLevel(logging.DEBUG)

ASSEMBLIES = [Path(os.path.basename(f)).stem for f in glob.glob("assemblies/*.py")]


def get_form(assembly):
    module = importlib.import_module(f"assemblies.{assembly}")
    return module.Form


def get_assembly_fn(assembly):
    module = importlib.import_module(f"assemblies.{assembly}")
    #cache.memoize.memoize(module.make)
    return module.make


@app.route("/")
def index():
    """list assemblies"""
    return render_template("index.html", assemblies=ASSEMBLIES)


@app.route("/<assembly>/view", methods=["POST", "GET"])
@app.route("/<assembly>/<model>/view", methods=["POST", "GET"])
def cad_view(assembly, model=None):
    """View the assembly or model."""
    form_cls = get_form(assembly)
    form = form_cls(request.form, **request.args)

    fn = get_assembly_fn(assembly)
    result = fn(**form.data)

    files = result["parts"].keys()

    if model in result["parts"]:
        # show a specific part
        w = show(result["parts"][model])
    else:
        # show the entire assembly
        w = show(*result["parts"].values())

    data = embed_data(views=w.cq_view.renderer)

    return render_template(
        "cadview.html",
        manager_state=data["manager_state"],
        widget_views=data["view_specs"],
        assembly=assembly,
        model=model,
        form=form,
        download_url_params=form.data,
        files=files,
        assemblies=ASSEMBLIES,
    )


@app.route("/<assembly>/<model>/download", methods=["POST", "GET"])
def stl_download(assembly, model):
    """Download the stl."""
    form_cls = get_form(assembly)
    form = form_cls(request.form, **request.args)

    fn = get_assembly_fn(assembly)
    result = fn(**form.data)

    part = result["parts"][model]

    params = "_".join("{}{}".format(p, v) for p, v in result["parameters"].items())
    filename = f"{assembly}_{model}_v{result['version']}_{params}.stl"

    cq.exporters.export(part, filename)

    return send_from_directory(".", filename, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
