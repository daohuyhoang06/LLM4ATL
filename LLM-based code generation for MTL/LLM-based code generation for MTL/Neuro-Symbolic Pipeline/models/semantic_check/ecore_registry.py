import xml.etree.ElementTree as ET
from errors import SemanticError

class ATLEcoreRegistry:
    def __init__(self, ecore_file_path):
        self.ecore_file_path = ecore_file_path

        self.packages = {}
        self.uml_context = {}

        self._parse_ecore()

    def _parse_ecore(self):
        tree = ET.parse(self.ecore_file_path)
        root = tree.getroot()

        namespaces = {
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'ecore': 'http://www.eclipse.org/emf/2002/Ecore'
        }

        for package in root.findall(
            "./ecore:EPackage",
            namespaces
        ):
            package_name = package.get("name")
            ns_uri = package.get("nsURI")
            ns_prefix = package.get("nsPrefix")

            self.packages[package_name] = {
                "name": package_name,
                "nsURI": ns_uri,
                "nsPrefix": ns_prefix,
            }

            for classifier in package.findall("./eClassifiers"):
                classifier_type = classifier.get("{http://www.w3.org/2001/XMLSchema-instance}type")

                #Xử lý nếu là EClass
                if classifier_type == "ecore:EClass":
                    class_name = classifier.get("name")

                    atributes = {}
                    associations = {}

                    # - Xử lý tính kế thừa (Supertypes) -
                    super_class = None
                    super_types = classifier.get("eSuperTypes")

                    if super_types:
                        super_class = super_types.split("/")[-1]

                    # Xử lý các structural features (EAttributes và EReferences)
                    for feature in classifier.findall("./eStructuralFeatures"):
                        feature_type = feature.get("{http://www.w3.org/2001/XMLSchema-instance}type")

                        if feature_type == "ecore:EAttribute":
                           attribute_name, attribute_type = self._parse_attribute(feature)

                           atributes[attribute_name] = attribute_type


                        elif feature_type == "ecore:EReference":
                            reference_name, reference_type = self._parse_reference(feature)

                            associations[reference_name] = reference_type

                    self.uml_context[class_name] = {
                        "super_class": super_class,
                        "attributes": atributes,
                        "associations": associations,
                    }

    def _parse_attribute(self, feature):
        attribute_name = feature.get("name")
        ecore_type = feature.get("eType")

        attribute_type = self._map_ecore_type_to_ocl(ecore_type)

        return attribute_name, attribute_type

    def _map_ecore_type_to_ocl(self, ecore_type):
        if ecore_type is None:
            return "Unknown"
        
        if ecore_type.endswith("/String"):
            return "String"
        
        if ecore_type.endswith("/Integer"):
            return "Integer"

        if ecore_type.endswith("/Real"):
            return "Real"

        if ecore_type.endswith("/Boolean"):
            return "Boolean"

        return "Unknown"
        
    def _parse_reference(self, feature):
        reference_name = feature.get("name")
        ecore_type = feature.get("eType").split("/")[-1]  # Lấy tên class từ eType

        lower_bound = feature.get("lowerBound", "0")
        upper_bound = feature.get("upperBound", "1")
        ordered = feature.get("ordered", "true").lower() == "true"

        if upper_bound == "-1":
            if ordered:
                raise ValueError(
                    f"Ordered collection '{reference_name}' "
                    f"cannot be represented in the supported OCL subset."
                )
            else:
                reference_type = f"Set({ecore_type})"

        elif int(upper_bound) > 1:
            if ordered:
                raise ValueError(
                    f"Ordered collection '{reference_name}' "
                    f"cannot be represented in the supported OCL subset."
                )
            else:
                reference_type = f"Set({ecore_type})"

        elif lower_bound == "0" and upper_bound == "1":
            reference_type = f"{ecore_type}[0..1]"

        else:
            reference_type = f"{ecore_type}[1..1]"

        return reference_name, reference_type

    def resolve_property(self, class_name: str, property_name: str) -> str:
        if "!" in class_name:
           class_name = class_name.split("!")[-1]

        current_class = class_name

        while current_class:
            if current_class not in self.uml_context:
               raise SemanticError(f"Class '{current_class}' not found in UML context.")

            cls_info = self.uml_context[current_class]

            if property_name in cls_info.get("attributes", {}):
               return cls_info["attributes"][property_name]

            if property_name in cls_info.get("associations", {}):
               return cls_info["associations"][property_name]

            current_class = cls_info.get("super_class")

        raise SemanticError(
            f"Class '{class_name}' doesn't have "
            f"the attribute or association: '{property_name}' "
            f"in its inheritance hierarchy"
        )