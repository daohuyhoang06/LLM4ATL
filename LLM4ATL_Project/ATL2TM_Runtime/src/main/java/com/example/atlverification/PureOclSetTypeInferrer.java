package com.example.atlverification;

import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.eclipse.emf.ecore.EClass;
import org.eclipse.emf.ecore.EClassifier;
import org.eclipse.emf.ecore.EObject;
import org.eclipse.emf.ecore.EPackage;
import org.eclipse.emf.ecore.EReference;
import org.eclipse.emf.ecore.EStructuralFeature;
import org.eclipse.emf.ecore.EcorePackage;

/** Checks a collect source independently of its syntactic nesting. */
final class PureOclSetTypeInferrer {
    private enum Kind { SCALAR, SET, ORDERED_SET, BAG, SEQUENCE }

    private record ValueType(EClassifier element, Kind kind, int nestedDepth) {
        ValueType(EClassifier element, Kind kind) {
            this(element, kind, 0);
        }

        boolean collection() {
            return kind != Kind.SCALAR;
        }
    }

    private final EPackage sourcePackage;

    private PureOclSetTypeInferrer(EPackage sourcePackage) {
        this.sourcePackage = sourcePackage;
    }

    static EClass infer(EObject expression, EPackage sourcePackage, EObject caller) {
        ValueType result = inferValue(expression, sourcePackage, caller);
        if (result.kind() != Kind.SET || result.nestedDepth() != 0
                || !(result.element() instanceof EClass type)) {
            throw unsupported("collect source must be a pure OCL Set of source objects");
        }
        return type;
    }

    static EClass inferCollection(EObject expression, EPackage sourcePackage,
            EObject caller) {
        ValueType result = inferValue(expression, sourcePackage, caller);
        if (!result.collection() || result.nestedDepth() != 0
                || !(result.element() instanceof EClass type)) {
            throw unsupported("union branch must be a pure OCL collection of source objects");
        }
        return type;
    }

    private static ValueType inferValue(EObject expression, EPackage sourcePackage,
            EObject caller) {
        PureOclSetTypeInferrer inferrer = new PureOclSetTypeInferrer(sourcePackage);
        Map<EObject, ValueType> variables = new HashMap<>();
        EObject inPattern = (EObject) feature(caller, "inPattern");
        for (Object entry : elements(inPattern, "elements")) {
            EObject input = (EObject) entry;
            EObject type = (EObject) feature(input, "type");
            EClassifier classifier = sourcePackage.getEClassifier(
                    String.valueOf(feature(type, "name")));
            if (!(classifier instanceof EClass)) {
                throw unsupported("unknown source input type");
            }
            variables.put(input, new ValueType(classifier, Kind.SCALAR));
        }
        return inferrer.typeOf(expression, variables);
    }

    private ValueType typeOf(EObject expression, Map<EObject, ValueType> variables) {
        if (expression == null) {
            throw unsupported("null OCL expression in collect source");
        }
        String node = expression.eClass().getName();
        switch (node) {
            case "VariableExp": {
                ValueType value = variables.get(feature(expression, "referredVariable"));
                if (value == null) {
                    throw unsupported("collect source refers to a variable outside its source scope");
                }
                return value;
            }
            case "NavigationOrAttributeCallExp": {
                ValueType owner = typeOf((EObject) feature(expression, "source"), variables);
                if (owner.collection() || !(owner.element() instanceof EClass ownerClass)) {
                    throw unsupported("navigation requires a source object");
                }
                EStructuralFeature property = ownerClass.getEStructuralFeature(
                        String.valueOf(feature(expression, "name")));
                if (property == null) {
                    throw unsupported("unknown source property " + feature(expression, "name"));
                }
                Kind kind = !property.isMany() ? Kind.SCALAR
                        : property.isOrdered()
                                ? (property.isUnique() ? Kind.ORDERED_SET : Kind.SEQUENCE)
                                : (property.isUnique() ? Kind.SET : Kind.BAG);
                return new ValueType(property.getEType(), kind);
            }
            case "IteratorExp":
                return iteratorType(expression, variables);
            case "SetExp", "OrderedSetExp", "BagExp", "SequenceExp":
                return collectionLiteralType(expression, variables);
            case "CollectionOperationCallExp":
                return collectionOperationType(expression, variables);
            case "OperatorCallExp":
                return operatorType(expression, variables);
            case "OperationCallExp":
                return operationType(expression, variables);
            case "BooleanExp":
                return scalar(EcorePackage.eINSTANCE.getEBoolean());
            case "IntegerExp":
                return scalar(EcorePackage.eINSTANCE.getEInt());
            case "RealExp":
                return scalar(EcorePackage.eINSTANCE.getEDouble());
            case "StringExp":
                return scalar(EcorePackage.eINSTANCE.getEString());
            case "OclModelElement": {
                EClassifier modelType = sourcePackage.getEClassifier(
                        String.valueOf(feature(expression, "name")));
                if (modelType == null) {
                    throw unsupported("unknown source model type");
                }
                return scalar(modelType);
            }
            default:
                throw unsupported("unsupported pure OCL node " + node);
        }
    }

    private ValueType iteratorType(EObject expression, Map<EObject, ValueType> variables) {
        ValueType source = typeOf((EObject) feature(expression, "source"), variables);
        List<?> iterators = elements(expression, "iterators");
        if (!source.collection() || iterators.size() != 1) {
            throw unsupported("iterator requires one variable over a collection");
        }
        Map<EObject, ValueType> nested = new HashMap<>(variables);
        nested.put((EObject) iterators.get(0), scalar(source.element()));
        ValueType body = typeOf((EObject) feature(expression, "body"), nested);
        String name = String.valueOf(feature(expression, "name"));
        return switch (name) {
            case "select", "reject" -> {
                if (!isBoolean(body)) {
                    throw unsupported(name + " requires a Boolean predicate");
                }
                yield source;
            }
            case "collect" -> new ValueType(body.element(),
                    source.kind() == Kind.ORDERED_SET || source.kind() == Kind.SEQUENCE
                            ? Kind.SEQUENCE : Kind.BAG,
                    body.nestedDepth() + (body.collection() ? 1 : 0));
            case "exists", "forAll", "one" -> {
                if (!isBoolean(body)) {
                    throw unsupported(name + " requires a Boolean predicate");
                }
                yield scalar(EcorePackage.eINSTANCE.getEBoolean());
            }
            default -> throw unsupported("unsupported pure OCL iterator " + name);
        };
    }

    private ValueType collectionLiteralType(EObject expression,
            Map<EObject, ValueType> variables) {
        List<?> entries = elements(expression, "elements");
        if (entries.isEmpty()) {
            throw unsupported("empty collection literal has no inferable source element type");
        }
        EClassifier element = null;
        for (Object entry : entries) {
            ValueType current = typeOf((EObject) entry, variables);
            if (current.collection() || (element != null && element != current.element())) {
                throw unsupported("collection literal requires source elements of one type");
            }
            element = current.element();
        }
        Kind kind = switch (expression.eClass().getName()) {
            case "SetExp" -> Kind.SET;
            case "OrderedSetExp" -> Kind.ORDERED_SET;
            case "BagExp" -> Kind.BAG;
            default -> Kind.SEQUENCE;
        };
        return new ValueType(element, kind);
    }

    private ValueType collectionOperationType(EObject expression,
            Map<EObject, ValueType> variables) {
        ValueType source = typeOf((EObject) feature(expression, "source"), variables);
        if (!source.collection()) {
            throw unsupported("collection operation requires a collection");
        }
        String name = String.valueOf(feature(expression, "operationName"));
        List<?> arguments = elements(expression, "arguments");
        switch (name) {
            case "asSet", "asBag", "asSequence", "asOrderedSet":
                requireArity(name, arguments, 0);
                return new ValueType(source.element(), switch (name) {
                    case "asSet" -> Kind.SET;
                    case "asBag" -> Kind.BAG;
                    case "asSequence" -> Kind.SEQUENCE;
                    default -> Kind.ORDERED_SET;
                }, source.nestedDepth());
            case "flatten":
                requireArity(name, arguments, 0);
                if (source.nestedDepth() == 0) {
                    throw unsupported("flatten requires nested collection elements");
                }
                return new ValueType(source.element(), source.kind(),
                        source.nestedDepth() - 1);
            case "union", "intersection": {
                requireArity(name, arguments, 1);
                ValueType other = typeOf((EObject) arguments.get(0), variables);
                if (!other.collection() || source.element() != other.element()
                        || source.nestedDepth() != other.nestedDepth()) {
                    throw unsupported(name + " requires collections of the same source type");
                }
                return new ValueType(source.element(),
                        source.kind() == Kind.SET && other.kind() == Kind.SET
                                ? Kind.SET : Kind.BAG, source.nestedDepth());
            }
            case "including", "excluding": {
                requireArity(name, arguments, 1);
                ValueType item = typeOf((EObject) arguments.get(0), variables);
                if (item.collection() || item.element() != source.element()) {
                    throw unsupported(name + " requires an element of the source type");
                }
                return source;
            }
            case "includes", "excludes":
                requireArity(name, arguments, 1);
                typeOf((EObject) arguments.get(0), variables);
                return scalar(EcorePackage.eINSTANCE.getEBoolean());
            case "isEmpty", "notEmpty":
                requireArity(name, arguments, 0);
                return scalar(EcorePackage.eINSTANCE.getEBoolean());
            case "size":
                requireArity(name, arguments, 0);
                return scalar(EcorePackage.eINSTANCE.getEInt());
            default:
                throw unsupported("unsupported pure OCL collection operation " + name);
        }
    }

    private ValueType operatorType(EObject expression, Map<EObject, ValueType> variables) {
        String name = String.valueOf(feature(expression, "operationName"));
        typeOf((EObject) feature(expression, "source"), variables);
        List<?> arguments = elements(expression, "arguments");
        for (Object argument : arguments) {
            typeOf((EObject) argument, variables);
        }
        return switch (name) {
            case "not", "and", "or", "xor", "implies", "=", "<>",
                    "<", "<=", ">", ">=" -> scalar(EcorePackage.eINSTANCE.getEBoolean());
            case "+", "-", "*", "/", "div", "mod" ->
                scalar(EcorePackage.eINSTANCE.getEInt());
            default -> throw unsupported("unsupported pure OCL operator " + name);
        };
    }

    private ValueType operationType(EObject expression, Map<EObject, ValueType> variables) {
        ValueType source = typeOf((EObject) feature(expression, "source"), variables);
        String name = String.valueOf(feature(expression, "operationName"));
        List<?> arguments = elements(expression, "arguments");
        for (Object argument : arguments) {
            typeOf((EObject) argument, variables);
        }
        return switch (name) {
            case "oclIsUndefined", "oclIsKindOf", "oclIsTypeOf" ->
                scalar(EcorePackage.eINSTANCE.getEBoolean());
            case "oclAsType" -> {
                requireArity(name, arguments, 1);
                yield typeOf((EObject) arguments.get(0), variables);
            }
            case "toString" -> scalar(EcorePackage.eINSTANCE.getEString());
            default -> throw unsupported("unsupported pure OCL operation " + name
                    + " on " + source.element().getName());
        };
    }

    private static boolean isBoolean(ValueType value) {
        return !value.collection() && value.element() == EcorePackage.eINSTANCE.getEBoolean();
    }

    private static ValueType scalar(EClassifier element) {
        return new ValueType(element, Kind.SCALAR);
    }

    private static void requireArity(String name, List<?> args, int expected) {
        if (args.size() != expected) {
            throw unsupported(name + " requires " + expected + " argument(s)");
        }
    }

    private static List<?> elements(EObject object, String name) {
        Object value = feature(object, name);
        return value instanceof List<?> list ? list : List.of();
    }

    private static Object feature(EObject object, String name) {
        if (object == null) {
            return null;
        }
        EStructuralFeature property = object.eClass().getEStructuralFeature(name);
        return property == null ? null : object.eGet(property);
    }

    private static IllegalArgumentException unsupported(String reason) {
        return new IllegalArgumentException(reason);
    }
}
