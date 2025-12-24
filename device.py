import gdsfactory as gf
import gfelib as gl

import numpy as np
import functools

from pdk import LAYERS, PDK

PDK.activate()

static_cell = functools.partial(gf.cell, check_instances=False)

# GLOBAL CONSTANTS
CHIP_SIZE = 8000
CHIP_BORDER_WIDTH = 200

ANGLE_RESOLUTION = 0.1
CAVITY_WIDTH = 40

RELEASE_SPEC = gl.datatypes.ReleaseSpec(
    hole_radius=3,
    distance=6,
    angle_resolution=18,
    layer=LAYERS.DEVICE_REMOVE,
)

CENTER_CARRIAGE_RADIUS = 375
CENTER_CARRIAGE_NITRIDE_RADIUS = 350
CENTER_CARRIAGE_OXIDE_RADIUS = 300
CENTER_CARRIAGE_CAVITY_RADIUS = 250

RFLEX_INNER_RADIUS0 = 400
RFLEX_INNER_RADIUS1 = 425
RFLEX_ANCHOR_RADIUS0 = 1600
RFLEX_ANCHOR_RADIUS1 = 1680
RFLEX_BEAM_WIDTH = 3.5
RFLEX_BEAM_SPEC = gl.datatypes.BeamSpec(
    thick_length=(0, 0.8),
    thick_width=(40, 0),
    thick_offset=(0, 0),
)
RFLEX_BEAM_ANGLES = [35, 60]

RDRIVE_INNER_RADIUS = 1700
RDRIVE_MID_RADIUS = 1900
RDRIVE_OUTER_RADIUS = 2150
RDRIVE_TEETH_PITCH = 0.5
RDRIVE_TEETH_WIDTH = 7
RDRIVE_TEETH_HEIGHT = 6.5
RDRIVE_TEETH_CLEARANCE = 2.5
RDRIVE_TEETH_PHASE = [-120, 0, 120]
RDRIVE_TEETH_COUNT = 90
RDRIVE_ROTOR_SPAN = 160

ZDRIVE_CLEARANCE = 8
ZDRIVE_INNER_RADIUS = 2250
ZDRIVE_OUTER_RADIUS = 2500
ZDRIVE_RING_SPAN = 60
ZDRIVE_ANCHOR_SIZE = 120

ZCANT_WIDTH = 600
ZCANT_LENGTH1 = 600
ZCANT_LENGTH2 = 100
ZCANT_BEAM1_WIDTH = 5
ZCANT_BEAM1_LENGTH = 100
ZCANT_BEAM2_WIDTH = 5
ZCANT_BEAM2_LENGTH = 100
ZCANT_STUB_WIDTH = 40
ZCANT_STUB_INSET = 70
ZCANT_STUB_ANCHOR_SIZE = 250

ZACTUATOR_WIDTH = 2800
ZACTUATOR_LENGTH = 700
ZACTUATOR_LENGTH_STEP = 5
ZACTUATOR_BEAM1_WIDTH = 4
ZACTUATOR_BEAM1_LENGTH = 150
ZACTUATOR_BEAM2_WIDTH = 4
ZACTUATOR_BEAM2_LENGTH = 40

ZR_CONNECTOR_SPANS = [
    (-30, -25),
    (15, 20),
    (60, 65),
]

WIRE_BOND_SIZE = 300
WIRE_BOND_OFFSET = 2200

CHIP_BOND_RADIUS = 2600
CHIP_BOND_SPAN = 60
CHIP_BOND_MARKER_SIZE = 100

CAP_CHIP_SIZE = 5000
CAP_TRENCH_INNER_RADIUS = 450
CAP_TRENCH_OUTER_RADIUS = 2600


via = gl.basic.via(
    radius_first=20,
    radius_last=100,
    geometry_layers=[
        LAYERS.VIAS_ETCH,
        LAYERS.POLY,
        LAYERS.OXIDE,
        LAYERS.NITRIDE,
    ],
    angle_resolution=ANGLE_RESOLUTION,
)


@static_cell
def chip_border() -> gf.Component:
    c = gf.Component()

    _ = c << gl.device.chip_border(
        size=(CHIP_SIZE, CHIP_SIZE),
        width=CHIP_BORDER_WIDTH,
        geometry_layer=LAYERS.DEVICE,
        handle_layer=LAYERS.HANDLE_P7,
        centered=True,
        release_spec=RELEASE_SPEC,
    )

    pos = 2 * WIRE_BOND_SIZE + WIRE_BOND_OFFSET + CAVITY_WIDTH
    size = 0.5 * CHIP_SIZE - CHIP_BORDER_WIDTH - pos - CAVITY_WIDTH
    for r in [0, 90, 180, 270]:
        ref = c << gf.components.rectangle(
            size=(size, size),
            layer=LAYERS.DEVICE,
            centered=False,
        )
        ref.move((pos, pos))
        ref.rotate(angle=r, center=(0, 0))

    return c


@static_cell
def center_carriage() -> gf.Component:
    c = gf.Component()

    _ = c << gf.components.circle(
        radius=CENTER_CARRIAGE_RADIUS,
        angle_resolution=ANGLE_RESOLUTION,
        layer=LAYERS.DEVICE,
    )

    _ = c << gf.components.circle(
        radius=CENTER_CARRIAGE_RADIUS,
        angle_resolution=ANGLE_RESOLUTION,
        layer=LAYERS.HANDLE_P0,
    )

    _ = c << gf.components.circle(
        radius=CENTER_CARRIAGE_NITRIDE_RADIUS,
        angle_resolution=ANGLE_RESOLUTION,
        layer=LAYERS.NITRIDE,
    )

    _ = c << gf.components.circle(
        radius=CENTER_CARRIAGE_NITRIDE_RADIUS,
        angle_resolution=ANGLE_RESOLUTION,
        layer=LAYERS.CAP_NITRIDE,
    )

    _ = c << gf.components.circle(
        radius=CENTER_CARRIAGE_OXIDE_RADIUS,
        angle_resolution=ANGLE_RESOLUTION,
        layer=LAYERS.OXIDE,
    )

    _ = c << gf.components.circle(
        radius=CENTER_CARRIAGE_OXIDE_RADIUS,
        angle_resolution=ANGLE_RESOLUTION,
        layer=LAYERS.CAP_OXIDE,
    )

    _ = c << gf.components.circle(
        radius=CENTER_CARRIAGE_CAVITY_RADIUS,
        angle_resolution=ANGLE_RESOLUTION,
        layer=LAYERS.HANDLE_REMOVE,
    )

    _ = c << gf.components.circle(
        radius=CENTER_CARRIAGE_CAVITY_RADIUS,
        angle_resolution=ANGLE_RESOLUTION,
        layer=LAYERS.CAP_BACKSIDE,
    )

    _ = c << gl.basic.ring(
        radius_inner=CAP_TRENCH_INNER_RADIUS,
        radius_outer=CAP_TRENCH_OUTER_RADIUS,
        angles=(0, 360),
        geometry_layer=LAYERS.CAP_TRENCH_ETCH,
        angle_resolution=ANGLE_RESOLUTION,
        release_spec=None,
    )

    return c


@static_cell
def r_flexure_half() -> gf.Component:
    c = gf.Component()

    _ = c << gl.flexure.butterfly(
        radius0=RFLEX_INNER_RADIUS0,
        radius1=RFLEX_INNER_RADIUS1,
        radius2=RFLEX_ANCHOR_RADIUS0,
        width_beam=RFLEX_BEAM_WIDTH,
        angles=RFLEX_BEAM_ANGLES,
        release_inner=True,
        geometry_layer=LAYERS.DEVICE,
        angle_resolution=ANGLE_RESOLUTION,
        beam_spec=RFLEX_BEAM_SPEC,
        release_spec=RELEASE_SPEC,
    )

    beam_angle = RFLEX_BEAM_ANGLES[0]
    anchor_angle0 = beam_angle + 0.5 * RFLEX_BEAM_WIDTH / RFLEX_ANCHOR_RADIUS0 / (
        np.pi / 180
    )

    _ = c << gl.basic.ring(
        radius_inner=RFLEX_ANCHOR_RADIUS0,
        radius_outer=RFLEX_ANCHOR_RADIUS1,
        angles=(-anchor_angle0, anchor_angle0),
        geometry_layer=LAYERS.DEVICE,
        angle_resolution=ANGLE_RESOLUTION,
        release_spec=None,
    )

    _ = c << gl.basic.ring(
        radius_inner=RFLEX_ANCHOR_RADIUS0,
        radius_outer=RFLEX_ANCHOR_RADIUS1,
        angles=(-anchor_angle0, anchor_angle0),
        geometry_layer=LAYERS.HANDLE_P1,
        angle_resolution=ANGLE_RESOLUTION,
        release_spec=None,
    )

    return c


@static_cell
def r_drive_half() -> gf.Component:
    c = gf.Component()

    _ = c << gl.actuator.rotator_gear(
        radius_inner=RDRIVE_INNER_RADIUS,
        radius_gap=RDRIVE_MID_RADIUS,
        radius_outer=RDRIVE_OUTER_RADIUS,
        teeth_pitch=RDRIVE_TEETH_PITCH,
        teeth_width=RDRIVE_TEETH_WIDTH,
        teeth_height=RDRIVE_TEETH_HEIGHT,
        teeth_clearance=RDRIVE_TEETH_CLEARANCE,
        teeth_phase=RDRIVE_TEETH_PHASE,
        teeth_count=RDRIVE_TEETH_COUNT,
        inner_rotor=True,
        rotor_span=RDRIVE_ROTOR_SPAN,
        geometry_layer=LAYERS.DEVICE,
        angle_resolution=ANGLE_RESOLUTION,
        release_spec=RELEASE_SPEC,
    )

    beam_angle = 90 - RFLEX_BEAM_ANGLES[1]
    connector0_angle = beam_angle + 0.5 * RFLEX_BEAM_WIDTH / RFLEX_ANCHOR_RADIUS1 / (
        np.pi / 180
    )
    _ = c << gl.basic.ring(
        radius_inner=RFLEX_ANCHOR_RADIUS0,
        radius_outer=RDRIVE_INNER_RADIUS
        + gl.utils.sagitta_offset_safe(
            radius=RDRIVE_INNER_RADIUS,
            chord=0,
            angle_resolution=ANGLE_RESOLUTION,
        ),
        angles=(-connector0_angle, connector0_angle),
        geometry_layer=LAYERS.DEVICE,
        angle_resolution=ANGLE_RESOLUTION,
        release_spec=RELEASE_SPEC,
    )

    connector1_angle = 0.5 * beam_angle
    _ = c << gl.basic.ring(
        radius_inner=CENTER_CARRIAGE_RADIUS
        - gl.utils.sagitta_offset_safe(
            radius=CENTER_CARRIAGE_RADIUS,
            chord=0,
            angle_resolution=ANGLE_RESOLUTION,
        ),
        radius_outer=RFLEX_ANCHOR_RADIUS0
        + gl.utils.sagitta_offset_safe(
            radius=RFLEX_ANCHOR_RADIUS0,
            chord=0,
            angle_resolution=ANGLE_RESOLUTION,
        ),
        angles=(-connector1_angle, connector1_angle),
        geometry_layer=LAYERS.DEVICE,
        angle_resolution=ANGLE_RESOLUTION,
        release_spec=RELEASE_SPEC,
    )

    _ = c << gl.basic.ring(
        radius_inner=RDRIVE_MID_RADIUS + 0.5 * CAVITY_WIDTH,
        radius_outer=ZDRIVE_OUTER_RADIUS,
        angles=(-90, 90),
        geometry_layer=LAYERS.HANDLE_P1,
        angle_resolution=ANGLE_RESOLUTION,
        release_spec=None,
    )

    handle_connector_inner_radius = RFLEX_ANCHOR_RADIUS1 - gl.utils.sagitta_offset_safe(
        radius=RFLEX_ANCHOR_RADIUS1,
        chord=0,
        angle_resolution=ANGLE_RESOLUTION,
    )
    handle_connector_outer_radius = (
        RDRIVE_MID_RADIUS
        + 0.5 * CAVITY_WIDTH
        + gl.utils.sagitta_offset_safe(
            radius=RDRIVE_MID_RADIUS + 0.5 * CAVITY_WIDTH,
            chord=0,
            angle_resolution=ANGLE_RESOLUTION,
        )
    )
    _ = c << gl.basic.ring(
        radius_inner=handle_connector_inner_radius,
        radius_outer=handle_connector_outer_radius,
        angles=(-90, -0.5 * RDRIVE_ROTOR_SPAN),
        geometry_layer=LAYERS.HANDLE_P1,
        angle_resolution=ANGLE_RESOLUTION,
        release_spec=None,
    )

    _ = c << gl.basic.ring(
        radius_inner=handle_connector_inner_radius,
        radius_outer=handle_connector_outer_radius,
        angles=(0.5 * RDRIVE_ROTOR_SPAN, 90),
        geometry_layer=LAYERS.HANDLE_P1,
        angle_resolution=ANGLE_RESOLUTION,
        release_spec=None,
    )

    return c


@static_cell
def z_cant_half() -> gf.Component:
    c = gf.Component()

    x0 = ZCANT_BEAM1_WIDTH - 0.5 * ZDRIVE_ANCHOR_SIZE
    x1 = 0.5 * (ZCANT_LENGTH1 + ZCANT_LENGTH2)
    x2 = x1 + ZDRIVE_CLEARANCE + 0.5 * ZCANT_STUB_WIDTH - 0.5 * ZCANT_STUB_ANCHOR_SIZE
    x3 = x1 + 2 * ZDRIVE_CLEARANCE + ZCANT_STUB_WIDTH
    x4 = ZCANT_LENGTH1
    x5 = x4 + ZCANT_LENGTH2
    x6 = x5 + 0.5 * ZDRIVE_ANCHOR_SIZE - ZACTUATOR_BEAM1_WIDTH
    x7 = x6 + ZACTUATOR_LENGTH - ZDRIVE_ANCHOR_SIZE - ZDRIVE_CLEARANCE
    x8 = x6 + ZACTUATOR_LENGTH - 0.5 * ZDRIVE_ANCHOR_SIZE - 0.5 * ZACTUATOR_BEAM2_WIDTH

    y0 = 0.5 * ZDRIVE_CLEARANCE
    y1 = (
        0.5 * ZCANT_WIDTH
        + ZCANT_BEAM2_LENGTH
        - 1.5 * ZDRIVE_ANCHOR_SIZE
        - ZACTUATOR_BEAM1_LENGTH
    )
    y2 = 0.5 * ZCANT_WIDTH - ZCANT_STUB_INSET
    y3 = 0.5 * ZCANT_WIDTH
    y4 = y3 + ZDRIVE_CLEARANCE
    y5 = y3 + ZCANT_BEAM1_LENGTH
    y6 = ZDRIVE_ANCHOR_SIZE
    y7 = y6 + ZACTUATOR_BEAM2_LENGTH
    y8 = 0.5 * ZACTUATOR_WIDTH
    y9 = 0.5 * ZACTUATOR_WIDTH + ZACTUATOR_BEAM2_LENGTH

    rect0_ref = c << gf.components.rectangle(
        size=(x1, y3 - y0),
        layer=LAYERS.DEVICE,
        centered=False,
    )
    rect0_ref.movey(y0)

    rect1_ref = c << gf.components.rectangle(
        size=(x3 - x1, y2 - y1 - ZDRIVE_CLEARANCE),
        layer=LAYERS.DEVICE,
        centered=False,
    )
    rect1_ref.move((x1, y1 + ZDRIVE_CLEARANCE))

    rect2_ref = c << gf.components.rectangle(
        size=(x4 - x3, y3 - y1 - ZDRIVE_CLEARANCE),
        layer=LAYERS.DEVICE,
        centered=False,
    )
    rect2_ref.move((x3, y1 + ZDRIVE_CLEARANCE))

    rect3_ref = c << gf.components.rectangle(
        size=(x5 - x1 - ZDRIVE_CLEARANCE, y1),
        layer=LAYERS.DEVICE,
        centered=False,
    )
    rect3_ref.movex(x1 + ZDRIVE_CLEARANCE)

    stub_ref = c << gl.basic.rectangle(
        size=(ZCANT_STUB_WIDTH, ZCANT_STUB_INSET),
        geometry_layer=LAYERS.DEVICE,
        centered=False,
        release_spec=RELEASE_SPEC,
    )
    stub_ref.move((x1 + ZDRIVE_CLEARANCE, y2 + ZDRIVE_CLEARANCE))

    stub_anchor_ref = c << gf.components.rectangle(
        size=(ZCANT_STUB_ANCHOR_SIZE, ZCANT_STUB_ANCHOR_SIZE),
        layer=LAYERS.DEVICE,
        centered=False,
    )
    stub_anchor_ref.move((x2, y4))

    via_ref = c << via
    via_ref.move((x2 + 0.5 * ZCANT_STUB_ANCHOR_SIZE, y4 + 0.5 * ZCANT_STUB_ANCHOR_SIZE))

    beam0_ref = c << gf.components.rectangle(
        size=(ZCANT_BEAM1_WIDTH, ZCANT_BEAM1_LENGTH),
        layer=LAYERS.DEVICE,
        centered=False,
    )
    beam0_ref.movey(y3)

    beam1_ref = c << gf.components.rectangle(
        size=(ZCANT_BEAM2_WIDTH, ZCANT_BEAM2_LENGTH),
        layer=LAYERS.DEVICE,
        centered=False,
    )
    beam1_ref.move((x4 - ZCANT_BEAM2_WIDTH, y3))

    anchor0_ref = c << gf.components.rectangle(
        size=(0.5 * ZDRIVE_ANCHOR_SIZE, ZDRIVE_ANCHOR_SIZE),
        layer=LAYERS.DEVICE,
        centered=False,
    )
    anchor0_ref.move((x0, y5))

    anchor1_ref = c << gf.components.rectangle(
        size=(ZDRIVE_ANCHOR_SIZE, WIRE_BOND_OFFSET - y5),
        layer=LAYERS.DEVICE,
        centered=False,
    )
    anchor1_ref.move((x4 - ZCANT_BEAM2_WIDTH, y5))

    beam2_ref = c << gf.components.rectangle(
        size=(ZACTUATOR_BEAM1_WIDTH, ZACTUATOR_BEAM1_LENGTH),
        layer=LAYERS.DEVICE,
        centered=False,
    )
    beam2_ref.move((x5 - ZACTUATOR_BEAM1_WIDTH, y1))

    anchor2_ref = c << gl.basic.rectangle(
        size=(0.5 * ZDRIVE_ANCHOR_SIZE, ZDRIVE_ANCHOR_SIZE),
        geometry_layer=LAYERS.DEVICE,
        centered=False,
        release_spec=RELEASE_SPEC,
    )
    anchor2_ref.move((x5 - ZACTUATOR_BEAM1_WIDTH, y1 + ZACTUATOR_BEAM1_LENGTH))

    x_size = (x7 - x6) / ZACTUATOR_LENGTH_STEP
    for x, y in zip(
        np.linspace(x6, x7 - x_size, ZACTUATOR_LENGTH_STEP),
        np.linspace(y5, 0.5 * ZACTUATOR_WIDTH, ZACTUATOR_LENGTH_STEP),
    ):
        rect_ref = c << gl.basic.rectangle(
            size=(x_size, y),
            geometry_layer=LAYERS.DEVICE,
            centered=False,
            release_spec=RELEASE_SPEC,
        )
        rect_ref.movex(x)

    anchor3_ref = c << gf.components.rectangle(
        size=(ZDRIVE_ANCHOR_SIZE, ZDRIVE_ANCHOR_SIZE),
        layer=LAYERS.DEVICE,
        centered=False,
    )
    anchor3_ref.movex(x7 + ZDRIVE_CLEARANCE)

    beam3_ref = c << gf.components.rectangle(
        size=(ZACTUATOR_BEAM2_WIDTH, ZACTUATOR_BEAM2_LENGTH),
        layer=LAYERS.DEVICE,
        centered=False,
    )
    beam3_ref.move((x8, y6))

    rect4_ref = c << gl.basic.rectangle(
        size=(ZDRIVE_ANCHOR_SIZE + ZDRIVE_CLEARANCE, y8 - y7),
        geometry_layer=LAYERS.DEVICE,
        centered=False,
        release_spec=RELEASE_SPEC,
    )
    rect4_ref.move((x7, y7))

    beam4_ref = c << gf.components.rectangle(
        size=(ZACTUATOR_BEAM2_WIDTH, ZACTUATOR_BEAM2_LENGTH),
        layer=LAYERS.DEVICE,
        centered=False,
    )
    beam4_ref.move((x8, y8))

    anchor4_ref = c << gf.components.rectangle(
        size=(ZDRIVE_ANCHOR_SIZE, WIRE_BOND_OFFSET - y9),
        layer=LAYERS.DEVICE,
        centered=False,
    )
    anchor4_ref.move((x7 + ZDRIVE_CLEARANCE, y9))

    wire_bond0_ref = c << gf.components.rectangle(
        size=(WIRE_BOND_SIZE, WIRE_BOND_SIZE),
        layer=LAYERS.DEVICE,
        centered=False,
    )
    wire_bond0_ref.move(
        (
            x4 - ZCANT_BEAM2_WIDTH - 0.5 * WIRE_BOND_SIZE + 0.5 * ZDRIVE_ANCHOR_SIZE,
            WIRE_BOND_OFFSET,
        )
    )

    wire_bond1_ref = c << gf.components.rectangle(
        size=(WIRE_BOND_SIZE, WIRE_BOND_SIZE),
        layer=LAYERS.DEVICE,
        centered=False,
    )
    wire_bond1_ref.move(
        (
            x7 + ZDRIVE_CLEARANCE - WIRE_BOND_SIZE + ZDRIVE_ANCHOR_SIZE,
            WIRE_BOND_OFFSET,
        )
    )

    return c


@static_cell
def z_drive_half() -> gf.Component:
    c = gf.Component()

    ring_angle = (
        (0.5 * ZCANT_WIDTH + ZCANT_BEAM1_LENGTH) / ZDRIVE_INNER_RADIUS / (np.pi / 180)
    )
    _ = c << gl.basic.ring(
        radius_inner=ZDRIVE_INNER_RADIUS,
        radius_outer=ZDRIVE_OUTER_RADIUS,
        angles=(ring_angle, 0.5 * ZDRIVE_RING_SPAN),
        geometry_layer=LAYERS.DEVICE,
        angle_resolution=ANGLE_RESOLUTION,
        release_spec=None,
    )

    z_cant_half_ref = c << z_cant_half()
    z_cant_half_ref.movex(ZDRIVE_INNER_RADIUS)

    return c


@static_cell
def z_drive() -> gf.Component:
    c = gf.Component()

    _ = c << z_drive_half()
    ref = c << z_drive_half()
    ref.mirror_y(0)

    rect_ref = c << gl.basic.rectangle(
        size=(ZCANT_LENGTH1 + ZCANT_LENGTH2, ZCANT_WIDTH),
        geometry_layer=LAYERS.HANDLE_P0,
        centered=False,
        release_spec=None,
    )
    rect_ref.move((ZDRIVE_INNER_RADIUS, -0.5 * ZCANT_WIDTH))

    return c


@static_cell
def zr_connector_half() -> gf.Component:
    c = gf.Component()

    for span in ZR_CONNECTOR_SPANS:
        _ = c << gl.basic.ring(
            radius_inner=RDRIVE_OUTER_RADIUS
            - gl.utils.sagitta_offset_safe(
                radius=RDRIVE_OUTER_RADIUS,
                chord=0,
                angle_resolution=ANGLE_RESOLUTION,
            ),
            radius_outer=ZDRIVE_INNER_RADIUS
            + gl.utils.sagitta_offset_safe(
                radius=ZDRIVE_INNER_RADIUS,
                chord=0,
                angle_resolution=ANGLE_RESOLUTION,
            ),
            angles=span,
            geometry_layer=LAYERS.DEVICE,
            angle_resolution=ANGLE_RESOLUTION,
            release_spec=None,
        )

    return c


@static_cell
def zr_connector() -> gf.Component:
    c = gf.Component()

    ref0 = c << zr_connector_half()
    ref1 = c << zr_connector_half()
    ref1.mirror_x(0)

    _ = c << gl.basic.ring(
        radius_inner=RFLEX_ANCHOR_RADIUS1
        - gl.utils.sagitta_offset_safe(
            radius=RFLEX_ANCHOR_RADIUS1,
            chord=0,
            angle_resolution=ANGLE_RESOLUTION,
        ),
        radius_outer=RDRIVE_OUTER_RADIUS,
        angles=(268, 272),
        geometry_layer=LAYERS.DEVICE,
        angle_resolution=ANGLE_RESOLUTION,
        release_spec=None,
    )

    _ = c << gl.basic.ring(
        radius_inner=0.5 * (RDRIVE_MID_RADIUS + RDRIVE_OUTER_RADIUS),
        radius_outer=RDRIVE_OUTER_RADIUS,
        angles=(250, 268),
        geometry_layer=LAYERS.DEVICE,
        angle_resolution=ANGLE_RESOLUTION,
        release_spec=None,
    )

    _ = c << gl.basic.ring(
        radius_inner=RDRIVE_OUTER_RADIUS
        - gl.utils.sagitta_offset_safe(
            radius=RDRIVE_OUTER_RADIUS,
            chord=0,
            angle_resolution=ANGLE_RESOLUTION,
        ),
        radius_outer=ZDRIVE_INNER_RADIUS
        + gl.utils.sagitta_offset_safe(
            radius=ZDRIVE_INNER_RADIUS,
            chord=0,
            angle_resolution=ANGLE_RESOLUTION,
        ),
        angles=(250, 255),
        geometry_layer=LAYERS.DEVICE,
        angle_resolution=ANGLE_RESOLUTION,
        release_spec=None,
    )

    via_radius = 0.5 * (ZDRIVE_INNER_RADIUS + ZDRIVE_OUTER_RADIUS)
    for angle in [285, 295]:
        ref = c << via
        ref.move(
            (
                via_radius * np.cos(angle * np.pi / 180),
                via_radius * np.sin(angle * np.pi / 180),
            )
        )

    return c


@static_cell
def z_release_lock() -> gf.Component:
    c = gf.Component()

    angle = 0.5 * ZDRIVE_RING_SPAN + CAVITY_WIDTH / ZDRIVE_INNER_RADIUS / (np.pi / 180)
    middle_radius = 0.5 * (ZDRIVE_INNER_RADIUS + CHIP_BOND_RADIUS - CAVITY_WIDTH)
    _ = c << gl.basic.ring(
        radius_inner=ZDRIVE_INNER_RADIUS,
        radius_outer=middle_radius,
        angles=(angle, 90 - angle),
        geometry_layer=LAYERS.DEVICE,
        angle_resolution=ANGLE_RESOLUTION,
        release_spec=None,
    )
    _ = c << gl.basic.ring(
        radius_inner=middle_radius,
        radius_outer=CHIP_BOND_RADIUS - CAVITY_WIDTH,
        angles=(angle, 90 - angle),
        geometry_layer=LAYERS.DEVICE,
        angle_resolution=ANGLE_RESOLUTION,
        release_spec=RELEASE_SPEC,
    )

    return c


@static_cell
def chip_bond_pad() -> gf.Component:
    c = gf.boolean(
        A=gf.components.rectangle(
            size=(0.5 * CAP_CHIP_SIZE, 0.5 * CAP_CHIP_SIZE),
            layer=LAYERS.DEVICE,
            centered=False,
        ),
        B=gf.components.circle(
            radius=CHIP_BOND_RADIUS,
            angle_resolution=ANGLE_RESOLUTION,
            layer=LAYERS.DEVICE,
        ),
        operation="-",
        layer=LAYERS.DEVICE,
        layer1=LAYERS.DEVICE,
        layer2=LAYERS.DEVICE,
    )

    marker0_ref = c << gf.components.rectangle(
        size=(CHIP_BOND_MARKER_SIZE, 0.1 * CHIP_BOND_MARKER_SIZE),
        layer=LAYERS.DEVICE,
        centered=False,
    )
    marker0_ref.move((0.5 * CAP_CHIP_SIZE, 0.5 * CAP_CHIP_SIZE))

    marker1_ref = c << gf.components.rectangle(
        size=(CHIP_BOND_MARKER_SIZE, 0.1 * CHIP_BOND_MARKER_SIZE),
        layer=LAYERS.DEVICE,
        centered=False,
    )
    marker1_ref.rotate(angle=90, center=(0, 0))
    marker1_ref.move(
        (0.5 * CAP_CHIP_SIZE + 0.1 * CHIP_BOND_MARKER_SIZE, 0.5 * CAP_CHIP_SIZE)
    )

    c.name = "CHIP_BOND_PAD"

    return c


@static_cell
def cap_border_quarter() -> gf.Component:
    outer = gf.Component()
    outer.add_polygon(
        points=[
            (0, 0),
            (0, RDRIVE_MID_RADIUS + CAVITY_WIDTH),
            (ZCANT_WIDTH - CAVITY_WIDTH, RDRIVE_MID_RADIUS + CAVITY_WIDTH),
            (ZCANT_WIDTH - CAVITY_WIDTH, 0.5 * CAP_CHIP_SIZE + CAVITY_WIDTH),
            (0.5 * CAP_CHIP_SIZE + CAVITY_WIDTH, 0.5 * CAP_CHIP_SIZE + CAVITY_WIDTH),
            (0.5 * CAP_CHIP_SIZE + CAVITY_WIDTH, ZCANT_WIDTH - CAVITY_WIDTH),
            (RDRIVE_MID_RADIUS + CAVITY_WIDTH, ZCANT_WIDTH - CAVITY_WIDTH),
            (RDRIVE_MID_RADIUS + CAVITY_WIDTH, 0),
        ],
        layer=LAYERS.CAP_BACKSIDE,
    )
    inner = gf.Component()
    inner.add_polygon(
        points=[
            (0, 0),
            (0, RDRIVE_MID_RADIUS),
            (ZCANT_WIDTH, RDRIVE_MID_RADIUS),
            (ZCANT_WIDTH, 0.5 * CAP_CHIP_SIZE),
            (0.5 * CAP_CHIP_SIZE, 0.5 * CAP_CHIP_SIZE),
            (0.5 * CAP_CHIP_SIZE, ZCANT_WIDTH),
            (RDRIVE_MID_RADIUS, ZCANT_WIDTH),
            (RDRIVE_MID_RADIUS, 0),
        ],
        layer=LAYERS.CAP_BACKSIDE,
    )

    c = gf.boolean(
        A=outer,
        B=inner,
        operation="-",
        layer=LAYERS.CAP_BACKSIDE,
        layer1=LAYERS.CAP_BACKSIDE,
        layer2=LAYERS.CAP_BACKSIDE,
    )

    _ = c << gl.basic.ring(
        radius_inner=1.1 * CAP_TRENCH_OUTER_RADIUS,
        radius_outer=0.5 * CHIP_SIZE,
        angles=(15, 75),
        geometry_layer=LAYERS.CAP_OXIDE,
        angle_resolution=ANGLE_RESOLUTION,
        release_spec=None,
    )

    c.name = "CAP_BORDER_QUARTER"

    return c


@static_cell
def device() -> gf.Component:
    c = gf.Component()

    chip_border_ref = c << chip_border()

    center_carriage_ref = c << center_carriage()

    r_flexure_half_upper_ref = c << r_flexure_half()
    r_flexure_half_upper_ref.rotate(angle=90, center=(0, 0))

    r_flexure_half_lower_ref = c << r_flexure_half()
    r_flexure_half_lower_ref.rotate(angle=90, center=(0, 0))
    r_flexure_half_lower_ref.mirror_y(0)

    r_flexure_half_right_ref = c << r_drive_half()
    r_flexure_half_left_ref = c << r_drive_half()
    r_flexure_half_left_ref.mirror_x(0)

    for r in [0, 90, 180, 270]:
        z_drive_ref = c << z_drive()
        z_drive_ref.rotate(angle=r, center=(0, 0))

        chip_bond_ref = c << chip_bond_pad()
        chip_bond_ref.rotate(angle=r, center=(0, 0))

        z_release_lock_ref = c << z_release_lock()
        z_release_lock_ref.rotate(angle=r, center=(0, 0))

        cap_border_quarter_ref = c << cap_border_quarter()
        cap_border_quarter_ref.rotate(angle=r, center=(0, 0))

    zr_connector_ref = c << zr_connector()

    return c
