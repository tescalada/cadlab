from flask import Flask, request, send_from_directory, render_template
# from flask_caching import Cache

import cadquery as cq
import logging

from jupyter_cadquery.cadquery import show
from ipywidgets.embed import embed_data

import importlib
import glob
import os
import sys
from pathlib import Path

from timeit import default_timer
from contextlib import contextmanager
from config import Config


@contextmanager
def timer(name):
    t_start = default_timer()
    try:
        yield
    finally:
        t_end = default_timer()
        app.logger.debug(f"{name} timer: {t_end - t_start} seconds")


app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)
app.config.from_object(Config())
app.logger.setLevel(logging.DEBUG)
# cache = Cache(app)

ASSEMBLIES = [Path(os.path.basename(f)).stem for f in glob.glob("assemblies/*.py")]


# Disable
def disable_prints():
    sys.stdout = open(os.devnull, 'w')

# Restore


def enable_prints():
    sys.stdout = sys.__stdout__


def get_form(assembly, args):
    module = importlib.import_module(f"assemblies.{assembly}")
    form = module.Form(**args)
    return form


# this doesnt actually work because it cant pickle the model
# @cache.memoize()
def get_result(assembly, args):
    app.logger.debug(f"{assembly}, {args}")
    module = importlib.import_module(f"assemblies.{assembly}")
    form = module.Form(**args)
    result = module.make(**form.data)
    return result


@app.route("/")
def index():
    """list assemblies"""
    return render_template("index.html", assemblies=ASSEMBLIES)


@app.route("/<assembly>/view", methods=["POST", "GET"])
@app.route("/<assembly>/<model>/view", methods=["POST", "GET"])
def cad_view(assembly, model=None):
    """View the assembly or model."""
    with timer("modeling"):
        result = get_result(assembly, request.args)
    form = get_form(assembly, request.args)

    files = result["parts"].keys()

    try:
        disable_prints()

        with timer("show"):
            if model in result["parts"]:
                # show a specific part
                w = show(result["parts"][model])
            else:
                # show the entire assembly
                w = show(*result["parts"].values())

        enable_prints()
    except:
        enable_prints()
        raise
    finally:
        enable_prints()

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
    with timer("dl modeling"):
        result = get_result(assembly, request.args)

    part = result["parts"][model]

    params = "_".join("{}{}".format(p, v) for p, v in result["parameters"].items())
    filename = f"{assembly}_{model}_v{result['version']}_{params}.stl"

    with timer("dl exporting"):
        cq.exporters.export(part, filename)

    return send_from_directory(".", filename, as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0")
