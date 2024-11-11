from fvh3t.core.area_layer import AreaLayer


def test_area_layer_create_areas(qgis_area_polygon_layer):
    area_layer = AreaLayer(
        qgis_area_polygon_layer,
        "fid",
        "name",
    )

    areas = area_layer.areas()

    assert len(areas) == 2

    area1 = areas[0]
    area2 = areas[1]

    assert area1.geometry().asWkt() == "Polygon ((1 2, 2 2, 2 2.5, 1 2.5, 1 2))"
    assert area2.geometry().asWkt() == "Polygon ((0 0, 1 0, 1 1, 0 1, 0 0))"
