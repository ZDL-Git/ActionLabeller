import textwrap
from copy import deepcopy

from lxml import etree
# root = etree.Element("annotation")
# etree.SubElement(root, "folder")
# etree.SubElement(root, "filename")
#
# size = etree.SubElement(root, "size")
# etree.SubElement(size, "width").text = "some value1"
# etree.SubElement(size, "height").text = "some vlaue2"
# etree.SubElement(size, "depth").text = "some vlaue2"
#
# object_ = etree.SubElement(root, "object")
# etree.SubElement(object_, "name").text = "some vlaue2"
# etree.SubElement(object_, "difficult").text = "some vlaue2"
# etree.SubElement(object_, "bndbox").text = "some vlaue2"
# root = etree.fromstring(default_template)
#
# tree = etree.ElementTree(root)
# tree.write('xmldemo.xml', pretty_print=True)
from zdl.utils.io.log import logger


class AnnotationXml:
    default_template = textwrap.dedent("""
        <annotation>
            <folder>images</folder>
            <filename>boxer1_index350.png</filename>
            <size>
                <width>200</width>
                <height>70</height>
                <depth>3</depth>
            </size>
            <object>
                <name>action1</name>
                <difficult>0</difficult>
                <bndbox>
                    <xmin>188</xmin>
                    <ymin>1</ymin>
                    <xmax>200</xmax>
                    <ymax>70</ymax>
                </bndbox>
            </object>
            <object>
                <name>action2</name>
                <difficult>0</difficult>
                <bndbox>
                    <xmin>185</xmin>
                    <ymin>1</ymin>
                    <xmax>200</xmax>
                    <ymax>70</ymax>
                </bndbox>
            </object>
        </annotation>""")

    def __init__(self, temp: str = None):
        parser = etree.XMLParser(remove_blank_text=True)
        self.temp_str = temp or self.default_template  # type:str
        self.temp_root = etree.fromstring(self.temp_str, parser)  # type:etree._Element
        self.action_top_elem = self._get_action_top_tag()  # type:etree._Element
        for e in self.temp_root.xpath(f'./{self.action_top_elem.tag}'):
            self.temp_root.remove(e)

    def __repr__(self):
        try:
            return etree.tostring(self.new_root, encoding='unicode', pretty_print=True)
        except AttributeError as e:
            return etree.tostring(self.temp_root, encoding='unicode', pretty_print=True)

    def new_file(self, fname):
        self.fname = fname  # type:str
        self.new_root = deepcopy(self.temp_root)  # type:etree._Element

    def set_tag(self, tag_name, value):
        for e in self.new_root.xpath(f'.//{tag_name}'):
            e.text = str(value)

    def append_action(self, name: str, xmin: int, xmax: int, ymin: int, ymax: int):
        action_top_tag = deepcopy(self.action_top_elem)
        action_top_tag.xpath('.//name')[0].text = name
        action_top_tag.xpath('.//xmin')[0].text = str(xmin)
        action_top_tag.xpath('.//xmax')[0].text = str(xmax)
        action_top_tag.xpath('.//ymin')[0].text = str(ymin)
        action_top_tag.xpath('.//ymax')[0].text = str(ymax)
        self.new_root.append(action_top_tag)

    def dump(self):
        etree.indent(self.new_root, space="    ")
        tree = etree.ElementTree(self.new_root)
        tree.write(self.fname, pretty_print=True)

    def _get_action_top_tag(self):
        for elem in self.temp_root.iterchildren():
            if elem.xpath('.//xmin'):
                logger.debug(f'action top tag: {elem.tag} {elem}')
                return elem


if __name__ == '__main__':
    annotation = AnnotationXml()
    annotation.new_file('runtime/xmldemo.xml')
    annotation.append_action('jab', 1, 2, 3, 4)
    annotation.append_action('punch', 21, 22, 23, 24)
    annotation.dump()
    print(annotation)
