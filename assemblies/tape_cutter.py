'''
This model is for a parametric tape cutter.

The top and bottom parts are printed and bolted around
a roll of tape and the metal strip recycled from a tinfoil
or saranwrap dispenser is inserted into the slot on the
side of the model.
'''

from wtforms.validators import DataRequired
from wtforms import FloatField
from flask_wtf import FlaskForm

import cadquery as cq
from jupyter_cadquery import set_defaults

# remove "clean" to avoid errors OCP kernel error
cq.occ_impl.shapes.Shape.clean = lambda x: x

set_defaults(
    # tree_width=100,
    # cad_width=400,
    axes=True,
    axes0=True,
    tools=True,
)


def make_tape_cutter(tape_od, tape_id, tape_width, cutter_width=5, cutter_thickness=0.1):

    version = 3
    screw_d = 3.1
    screw_head_d = 5  # 5.9
    screw_depth = 2.5 + 1
    nut_d = 6
    nut_h = 4

    tape_width = float(tape_width)

    # non-configurable
    cutter_thickness_gap = cutter_thickness + .4

    tape_offset = 1

    holder_thickness = 6

    tape_od = float(tape_od)
    tape_id = float(tape_id)

    tape_outer_d = tape_od
    tape_inner_d = tape_id
    tape_thickness = (tape_outer_d - tape_inner_d) / 2

    tape_expanded_outer_d = tape_outer_d + tape_offset
    tape_expanded_inner_d = tape_inner_d - tape_offset
    tape_expanded_width = tape_width + tape_offset
    tape_expanded_thickness = tape_thickness + (tape_offset * 2)

    # holder_circle_diameter = tape_expanded_thickness * 2.5

    tape = (
        cq.Workplane("left")
        .circle(tape_outer_d/2)
        .extrude(tape_width/2, both=True)
        .circle(tape_inner_d/2)
        .cutThruAll()
    )

    tape_expanded = (
        cq.Workplane("left")
        .circle(tape_expanded_outer_d/2)
        .extrude(tape_expanded_width / 2, both=True)
        .circle(tape_expanded_inner_d/2)
        .cutThruAll()
    )

    cutter_offset_z = tape_expanded_outer_d/2 + (holder_thickness / 4)
    cutter_offset_y = -holder_thickness + 0.5

    body_angle = 30

    cutter = (
        cq.Workplane("left")
        .box(cutter_thickness, cutter_width, tape_expanded_width)
        .translate((0, cutter_offset_y,  cutter_offset_z))
        .rotateAboutCenter((1, 0, 0), 15)
        .rotate((0, 0, 0), (1, 0, 0), body_angle)
    )

    cutter_hole = (
        cq.Workplane("left")
        .box(cutter_thickness_gap, cutter_width, tape_expanded_width)
        .translate((0, cutter_offset_y,  cutter_offset_z))
        .rotateAboutCenter((1, 0, 0), 15)
        .rotate((0, 0, 0), (1, 0, 0), body_angle)
    )

    pts = [
        (0 + tape_expanded_inner_d/2, -tape_expanded_width/2),
        (0 + tape_expanded_inner_d/2, tape_expanded_width/2),
        (tape_expanded_thickness + tape_expanded_inner_d/2, tape_expanded_width/2),
        (tape_expanded_thickness + tape_expanded_inner_d/2, -tape_expanded_width/2),

    ]
    body = cq.Workplane("ZX").polyline(pts).close().revolve(
        body_angle, axisStart=(0, -1), axisEnd=(0, 1)).mirror('XZ', union=True)

    body = body.intersect(tape_expanded)

    body = body.shell(holder_thickness)

    body = body.cut(tape_expanded)

    body = body.cut(cutter_hole)

    # TODO check that holder_thickness >= screw_head_d otherwise there will be issues

    tape_offset = (tape_thickness / 2) + (tape_inner_d/2)

    body = (
        body
        .faces(">X")
        .workplane()
        .polarArray(
            radius=(tape_expanded_outer_d/2) + holder_thickness/2,
            startAngle=-(body_angle * 1.5) / 2,
            angle=body_angle * 1.5,
            count=3,
        )
        .cboreHole(screw_d, screw_head_d, screw_depth)
    )

    body = (
        body
        .faces(">X")
        .workplane(-holder_thickness*2)
        .polarArray(
            radius=(tape_expanded_outer_d/2) + holder_thickness/2,
            startAngle=-(body_angle * 1.5) / 2,
            angle=body_angle * 1.5,
            count=3,
        )
        .rect(nut_d, nut_h*10)
        .cutBlind(-nut_h)
    )

    body = (
        body
        .faces(">X")
        .workplane()
        .polarArray(
            radius=(tape_expanded_inner_d/2) - holder_thickness/2,
            startAngle=-body_angle / 2,
            angle=body_angle,
            count=2,
        )
        .cboreHole(screw_d, screw_head_d, screw_depth)
    )

    body = (
        body
        .faces(">X")
        .workplane(-holder_thickness*2)
        .polarArray(
            radius=(tape_expanded_inner_d/2) - holder_thickness/2,
            startAngle=-body_angle / 2,
            angle=body_angle,
            count=2,
        )
        .rect(nut_d, nut_h*10)
        .cutBlind(-nut_h)
    )

    body_top, body_bottom = (
        body
        .faces(">X")
        .workplane(-holder_thickness)
        .split(keepTop=True, keepBottom=True).all()
    )

    return {
        'version': version,
        'parameters': {
            'tape_od': tape_od,
            'tape_id': tape_id,
            'tape_width': tape_width,
        },
        'parts': {
            'top': body_top,
            'bottom': body_bottom,
            'tape': tape,
            'cutter': cutter,
        },
    }


# TODO: Is there any good way to work in different sets of parameter defaults?
big_3m_masking_tape = {
    'tape_od': 115,
    'tape_id': 75,
    'tape_width': 49,
}

small_3m_masking_tape = {
    'tape_od': 115,
    'tape_id': 75,
    'tape_width': 18,
}


# cq.exporters.export(body_bottom,f"tape_cutter_bottom_v{version}_w{tape_width}id{tape_id}od{tape_od}.stl")
# cq.exporters.export(body_top,f"tape_cutter_top_v{version}_w{tape_width}id{tape_id}od{tape_od}.stl")

make = make_tape_cutter


class Form(FlaskForm):
    tape_od = FloatField(
        'Outer Diameter',
        description="The outer diameter of the tape roll in mm",
        validators=[DataRequired()],
        default=115,
        render_kw={
            'units': 'mm',
        },
    )
    tape_id = FloatField(
        'Inner Diameter',
        description="The inner diameter of the tape roll in mm",
        validators=[DataRequired()],
        default=75,
        render_kw={
            'units': 'mm',
        },
    )
    tape_width = FloatField(
        'Width',
        description="The width of the tape roll in mm",
        validators=[DataRequired()],
        default=49,
        render_kw={
            'units': 'mm',
        },
    )
