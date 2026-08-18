import xml.etree.ElementTree as ET
from .errors import SemanticError

class ATLEcoreRegistry:
    def __init__(self, ecore_file_path):
        if isinstance(ecore_file_path, list):
            self.ecore_file_paths = ecore_file_path
        else:
            self.ecore_file_paths = [ecore_file_path]

        self.packages = {}
        self.uml_context = {}

        for path in self.ecore_file_paths:
            self._parse_ecore(path)

    def _parse_ecore(self, path):
        tree = ET.parse(path)
        root = tree.getroot()

        # print("ROOT TAG:", root.tag)
        # print("ROOT ATTRIBUTES:", root.attrib)

        namespaces = {
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'ecore': 'http://www.eclipse.org/emf/2002/Ecore'
        }

        if root.tag == "{http://www.eclipse.org/emf/2002/Ecore}EPackage":
            packages = [root]
        else:
            packages = root.findall(
                ".//ecore:EPackage",
                namespaces
            )

        for package in packages:

            package_name = package.get("name")
            ns_uri = package.get("nsURI")
            ns_prefix = package.get("nsPrefix")

            self.packages[package_name] = {
                "name": package_name,
                "nsURI": ns_uri,
                "nsPrefix": ns_prefix,
            }

            # print("PACKAGE:", package.tag, package.attrib)
            # print(
            #     "CLASSIFIERS:",
            #     [(c.tag, c.attrib) for c in package.findall("./eClassifiers")]
            # )   

            for classifier in package.findall("./eClassifiers"):
                classifier_type = classifier.get("{http://www.w3.org/2001/XMLSchema-instance}type")

                #Xử lý nếu là EClass
                if classifier_type == "ecore:EClass":
                    class_name = classifier.get("name")
                    full_class_name = f"{package_name}!{class_name}"

                    atributes = {}
                    associations = {}

                    # - Xử lý tính kế thừa (Supertypes) -
                    super_classes = []
                    super_types = classifier.get("eSuperTypes")
                    
                    if not super_types:
                        super_type_node = classifier.find("./eSuperTypes")
                        if super_type_node is not None:
                            super_types = super_type_node.get("href")
                    
                    if super_types:
                        for st in super_types.strip().split():
                            super_base = st.split("/")[-1]
                            super_classes.append(f"{package_name}!{super_base}")

                    # Xử lý các structural features (EAttributes và EReferences)
                    for feature in classifier.findall("./eStructuralFeatures"):
                        feature_type = feature.get("{http://www.w3.org/2001/XMLSchema-instance}type")

                        if feature_type == "ecore:EAttribute":
                           attribute_name, attribute_type = self._parse_attribute(feature)

                           atributes[attribute_name] = attribute_type


                        elif feature_type == "ecore:EReference":
                            reference_name, reference_type = self._parse_reference(feature, package_name)

                            associations[reference_name] = reference_type

                    self.uml_context[full_class_name] = {
                        "super_classes": super_classes,
                        "attributes": atributes,
                        "associations": associations,
                    }
                    if class_name not in self.uml_context:
                        self.uml_context[class_name] = self.uml_context[full_class_name]

    def _parse_attribute(self, feature):
        attribute_name = feature.get("name")
        ecore_type = feature.get("eType")

        attribute_type = self._map_ecore_type_to_ocl(ecore_type)

        return attribute_name, attribute_type

    def _map_ecore_type_to_ocl(self, ecore_type):
        if ecore_type is None:
            return "Unknown"

        type_name = ecore_type.split("/")[-1].split("#")[-1]

        if type_name in ("EString", "String"):
            return "String"

        if type_name in ("EInt", "EIntegerObject", "Integer", "Int"):
            return "Integer"

        if type_name in ("EDouble", "EFloat", "Double", "Float", "Real"):
            return "Real"

        if type_name in ("EBoolean", "Boolean"):
            return "Boolean"

        return "Unknown"
        
    def _parse_reference(self, feature, package_name):
        reference_name = feature.get("name")
        ecore_type = feature.get("eType")

        if ecore_type is None:
            return reference_name, "Unknown"
        
        ecore_type = feature.get("eType").split("/")[-1]  # Lấy tên class từ eType

        qualified_type = f"{package_name}!{ecore_type}"

        lower_bound = feature.get("lowerBound", "0")
        upper_bound = feature.get("upperBound", "1")
        ordered = feature.get("ordered", "true").lower() == "true"

        if upper_bound == "-1" or int(upper_bound) > 1:
            unique = feature.get("unique", "true").lower() == "true"
            
            if unique and ordered:
                reference_type = f"OrderedSet({qualified_type})"
            elif unique and not ordered:
                reference_type = f"Set({qualified_type})"
            elif not unique and ordered:
                reference_type = f"Sequence({qualified_type})"
            else:
                reference_type = f"Bag({qualified_type})"

        elif lower_bound == "0" and upper_bound == "1":
            reference_type = f"{qualified_type}[0..1]"

        else:
            reference_type = f"{qualified_type}[1..1]"

        return reference_name, reference_type

    def resolve_property(self, class_name: str, property_name: str) -> str:
        current_class = class_name
        
        if current_class not in self.uml_context and "!" in class_name:
           current_class = class_name.split("!")[-1]

        queue = [current_class]
        visited = set()

        while queue:
            curr = queue.pop(0)
            if curr in visited:
                continue
            visited.add(curr)

            if curr not in self.uml_context:
               raise SemanticError(f"Class '{curr}' not found in UML context.")

            cls_info = self.uml_context[curr]

            if property_name in cls_info.get("attributes", {}):
               return cls_info["attributes"][property_name]

            if property_name in cls_info.get("associations", {}):
               return cls_info["associations"][property_name]

            for super_cls in cls_info.get("super_classes", []):
                # Remove the package name part if it exists for context lookup
                super_base = super_cls.split("!")[-1] if "!" in super_cls else super_cls
                queue.append(super_base)

        raise SemanticError(
            f"Class '{class_name}' doesn't have "
            f"the attribute or association: '{property_name}' "
            f"in its inheritance hierarchy"
        )