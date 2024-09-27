from lxml import etree


def parse_jmx_file(file_path):
    """
    Parses the JMX file and returns the root element.
    """
    try:
        tree = etree.parse(file_path)
        return tree.getroot()
    except etree.XMLSyntaxError as e:
        print(f"Error parsing the JMX file: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
