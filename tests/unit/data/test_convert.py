"""Unit tests for WBS 2.2.1 (Member A). Remove the skip marks as you implement each function."""

import pytest

from src.data import convert_voc_to_yolo as conv

TODO = pytest.mark.skip(reason="TODO WBS 2.2.1 (Member A): implement convert_voc_to_yolo")

SAMPLE_XML = """<annotation>
  <size><width>100</width><height>50</height><depth>3</depth></size>
  <object><name>Grasper</name><bndbox><xmin>10</xmin><ymin>10</ymin><xmax>30</xmax><ymax>40</ymax></bndbox></object>
  <object><name>SpecimenBag</name><bndbox><xmin>0</xmin><ymin>0</ymin><xmax>5</xmax><ymax>5</ymax></bndbox></object>
  <object><name>hook</name><bndbox><xmin>90</xmin><ymin>40</ymin><xmax>120</xmax><ymax>60</ymax></bndbox></object>
</annotation>"""


@TODO
def test_map_class_case_insensitive_and_drops_specimen_bag():
    assert conv.map_class("Grasper") == 0
    assert conv.map_class("IRRIGATOR") == 5
    assert conv.map_class("SpecimenBag") is None


@TODO
def test_box_is_clipped_and_normalised():
    cx, cy, w, h = conv.voc_box_to_yolo(90, 40, 120, 60, img_w=100, img_h=50)
    assert all(0.0 <= v <= 1.0 for v in (cx, cy, w, h))
    assert cx == pytest.approx(0.95) and w == pytest.approx(0.10)


@TODO
def test_known_xml_gives_expected_lines(tmp_path):
    xml = tmp_path / "v01_000001.xml"
    xml.write_text(SAMPLE_XML)
    lines = conv.convert_xml(xml)
    assert len(lines) == 2                      # SpecimenBag dropped
    assert lines[0].split()[0] == "0"           # grasper
    assert lines[1].split()[0] == "2"           # hook
