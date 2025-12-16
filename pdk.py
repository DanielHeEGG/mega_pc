import gdsfactory as gf


class LAYERS(gf.technology.LayerMap):
    DEVICE: gf.typings.Layer = (1, 0)
    DEVICE_RELEASE: gf.typings.Layer = (1, 1)
    HANDLE: gf.typings.Layer = (2, 0)

    VIAS_ETCH: gf.typings.Layer = (10, 0)
    VIAS_POLY: gf.typings.Layer = (11, 0)
    VIAS_OXIDE: gf.typings.Layer = (12, 0)
    NITRIDE: gf.typings.Layer = (13, 0)

    CAP_OXIDE: gf.typings.Layer = (20, 0)
    CAP_NITRIDE: gf.typings.Layer = (21, 0)
    CAP_TRENCH_ETCH: gf.typings.Layer = (22, 0)


PDK = gf.Pdk(
    name="mega_pc",
    layers=LAYERS,
    layer_views=gf.technology.LayerViews(),
)
