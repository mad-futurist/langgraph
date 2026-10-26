"""compatibility boundaries for issue 9410 experiments"""

import dataclasses
import sys
from datetime import date
from decimal import Decimal
from uuid import UUID

import ormsgpack
import pytest

from benchmarks.issue_9410.benchmark import (
    STRATEGIES,
    Kind,
    Leaf,
    Node,
    SendLike,
    make_encoder,
)
from langgraph.checkpoint.serde.jsonplus import (
    EXT_CONSTRUCTOR_KW_ARGS,
    EXT_CONSTRUCTOR_POS_ARGS,
    EXT_PYDANTIC_V2,
    JsonPlusSerializer,
)
from langgraph.checkpoint.serde.types import SendProtocol


@dataclasses.dataclass(unsafe_hash=True)
class SendDataclass:
    node: str
    arg: object
    extra: str = "preserved only by the dataclass branch"


@dataclasses.dataclass(slots=True)
class SlottedDataclass:
    value: int


@dataclasses.dataclass
class InheritedDataclass(Leaf):
    extra: int = 1


class InheritedSend(SendLike):
    pass


class InheritedUUID(UUID):
    pass


class InheritedDecimal(Decimal):
    pass


class InheritedDate(date):
    pass


@dataclasses.dataclass(unsafe_hash=True)
class DynamicDataclass:
    value: int = 1

    def __getattr__(self, name: str) -> object:
        if name == "node":
            return "worker"
        if name == "arg":
            return self.value
        raise AttributeError(name)


@dataclasses.dataclass(unsafe_hash=True)
class InstanceAttributes:
    value: int = 1


class CountingDescriptor:
    def __get__(self, instance: object, owner: type | None = None) -> str:
        if instance is None:
            return self
        instance.reads += 1
        return f"worker-{instance.reads}"


@dataclasses.dataclass(unsafe_hash=True)
class DescriptorDataclass:
    value: int = 1
    reads: int = dataclasses.field(default=0, init=False, compare=False)
    node = CountingDescriptor()
    arg = "argument"


@dataclasses.dataclass(unsafe_hash=True)
class MissingProperty:
    value: int = 1
    arg = "argument"

    @property
    def node(self) -> str:
        raise AttributeError("node is unavailable")


@dataclasses.dataclass(unsafe_hash=True)
class RaisingProperty:
    value: int = 1
    arg = "argument"

    @property
    def node(self) -> str:
        raise RuntimeError("descriptor failure")


@dataclasses.dataclass
class MissingArg:
    node: str = "worker"


@dataclasses.dataclass
class UnhashableSendDataclass:
    node: str = "worker"
    arg: object = 1


@dataclasses.dataclass(unsafe_hash=True)
class AttributeAccessDataclass:
    node: str = "worker"
    arg: object = 1
    reads: int = dataclasses.field(default=0, init=False, compare=False)

    def __getattribute__(self, name: str) -> object:
        if name in {"node", "arg"}:
            object.__setattr__(
                self, "reads", object.__getattribute__(self, "reads") + 1
            )
        return object.__getattribute__(self, name)


def extension(strategy: str, obj: object) -> tuple[int, bytes]:
    _, namespace = make_encoder(strategy)
    ext = namespace["_msgpack_default"](obj)
    assert isinstance(ext, ormsgpack.Ext)
    return ormsgpack.unpackb(
        ormsgpack.packb(ext), ext_hook=lambda code, data: (code, data)
    )


@pytest.mark.parametrize("strategy", STRATEGIES)
@pytest.mark.parametrize(
    "factory",
    [
        lambda: Leaf("one", Kind.A),
        lambda: Node("tree", [Leaf("one", Kind.A), Leaf("two", Kind.A)]),
        lambda: SendLike("worker", {"x": 1}),
        lambda: SendLike("worker", {"x": 1}, 3.5),
        lambda: SlottedDataclass(1),
        lambda: InheritedDataclass("one", Kind.A),
        lambda: InheritedSend("worker", 1),
        lambda: InstanceAttributes(),
        lambda: MissingArg(),
        lambda: UnhashableSendDataclass(),
        lambda: [Leaf("one", Kind.A), Kind.A, SendLike("worker", 1)],
        lambda: [UUID(int=1), Decimal("1.5"), date(2026, 1, 1)],
        lambda: InheritedUUID(int=1),
        lambda: InheritedDecimal("1.5"),
        lambda: InheritedDate(2026, 1, 1),
    ],
    ids=[
        "leaf",
        "nested_tree",
        "send",
        "send_timeout",
        "slotted_dataclass",
        "dataclass_subclass",
        "send_subclass",
        "missing_members",
        "missing_arg",
        "unhashable_send_dataclass",
        "mixed",
        "exact_types",
        "uuid_subclass",
        "decimal_subclass",
        "date_subclass",
    ],
)
def test_dispatch_candidates_preserve_regular_values(strategy: str, factory) -> None:
    baseline, _ = make_encoder("baseline")
    candidate, _ = make_encoder(strategy)
    expected = baseline(factory())
    actual = candidate(factory())
    assert actual == expected
    serde = JsonPlusSerializer(allowed_msgpack_modules=True)
    assert serde.loads_typed(actual) == factory()
    assert serde.loads_typed(expected) == serde.loads_typed(actual)


@pytest.mark.parametrize("strategy", STRATEGIES)
def test_send_dataclass_precedence_and_roundtrip(strategy: str) -> None:
    value = SendDataclass("worker", 1, extra="custom extra")
    baseline, _ = make_encoder("baseline")
    encode, _ = make_encoder(strategy)
    code, _ = extension(strategy, value)
    serde = JsonPlusSerializer(allowed_msgpack_modules=True)
    restored = serde.loads_typed(encode(value))
    if strategy == "dataclass_first":
        assert code == EXT_CONSTRUCTOR_KW_ARGS
        assert encode(value) != baseline(value)
        assert restored.extra == "custom extra"
    else:
        assert code == EXT_CONSTRUCTOR_POS_ARGS
        assert encode(value) == baseline(value)
        # Existing Send precedence drops dataclass-only fields.
        assert restored.extra == SendDataclass("worker", 1).extra


@pytest.mark.parametrize("strategy", STRATEGIES)
def test_dynamic_protocol_is_version_dependent(strategy: str) -> None:
    old_protocol = sys.version_info < (3, 12)
    expect_send = old_protocol and strategy not in {"static_guard", "dataclass_first"}
    code, _ = extension(strategy, DynamicDataclass())
    assert code == (
        EXT_CONSTRUCTOR_POS_ARGS if expect_send else EXT_CONSTRUCTOR_KW_ARGS
    )
    baseline, _ = make_encoder("baseline")
    candidate, _ = make_encoder(strategy)
    assert (candidate(DynamicDataclass()) == baseline(DynamicDataclass())) == (
        not old_protocol or strategy not in {"static_guard", "dataclass_first"}
    )
    serde = JsonPlusSerializer(allowed_msgpack_modules=True)
    expected = ["worker", 1] if expect_send else DynamicDataclass()
    assert serde.loads_typed(candidate(DynamicDataclass())) == expected


@pytest.mark.parametrize("strategy", STRATEGIES)
def test_descriptor_access_counts_and_bytes(strategy: str) -> None:
    original = DescriptorDataclass()
    value = DescriptorDataclass()
    expected = extension("baseline", original)
    actual = extension(strategy, value)
    adds_reads = strategy in {"attribute_guard", "guarded_dataclass"} or (
        strategy == "version_guard" and sys.version_info < (3, 12)
    )
    if strategy == "dataclass_first":
        assert actual[0] == EXT_CONSTRUCTOR_KW_ARGS
        assert value.reads == 0
        assert actual != expected
    elif adds_reads:
        assert value.reads == original.reads + 1
        assert actual != expected
    else:
        assert value.reads == original.reads
        assert actual == expected


@pytest.mark.parametrize("strategy", STRATEGIES)
def test_attribute_error_property_changes_branch_on_new_python(strategy: str) -> None:
    guarded = strategy in {"attribute_guard", "guarded_dataclass", "dataclass_first"}
    if sys.version_info >= (3, 12) and not guarded:
        with pytest.raises(AttributeError, match="node is unavailable"):
            extension(strategy, MissingProperty())
    else:
        assert extension(strategy, MissingProperty())[0] == EXT_CONSTRUCTOR_KW_ARGS


@pytest.mark.parametrize("strategy", STRATEGIES)
def test_non_attribute_error_property_exception(strategy: str) -> None:
    if strategy == "dataclass_first":
        assert extension(strategy, RaisingProperty())[0] == EXT_CONSTRUCTOR_KW_ARGS
    else:
        with pytest.raises(RuntimeError, match="descriptor failure"):
            extension(strategy, RaisingProperty())
        encode, _ = make_encoder(strategy)
        with pytest.raises(TypeError, match="Type is not msgpack serializable"):
            encode(RaisingProperty())


@pytest.mark.parametrize(
    "first_has_attributes",
    [False, True],
    ids=["nonconforming_first", "conforming_first"],
)
def test_type_cache_is_not_an_instance_conformance_cache(
    first_has_attributes: bool,
) -> None:
    absent, present = InstanceAttributes(), InstanceAttributes()
    present.node, present.arg = "worker", 1
    baseline, _ = make_encoder("baseline")
    cached, _ = make_encoder("type_cache")
    first, second = (present, absent) if first_has_attributes else (absent, present)
    assert cached(first) == baseline(first)
    if first_has_attributes:
        with pytest.raises(TypeError):
            cached(second)
        assert extension("baseline", second)[0] == EXT_CONSTRUCTOR_KW_ARGS
    else:
        assert cached(second) != baseline(second)
        assert extension("baseline", second)[0] == EXT_CONSTRUCTOR_POS_ARGS


@pytest.mark.parametrize("strategy", STRATEGIES)
@pytest.mark.parametrize("virtual", [False, True], ids=["explicit", "registered"])
def test_nominal_and_registered_protocol_instances_can_lack_members(
    strategy: str, virtual: bool
) -> None:
    if virtual:

        @dataclasses.dataclass
        class Nominal:
            value: int = 1

        SendProtocol.register(Nominal)
    else:

        @dataclasses.dataclass
        class Nominal(SendProtocol):
            value: int = 1

    value = Nominal()
    assert isinstance(value, SendProtocol)
    guarded = strategy in {
        "attribute_guard",
        "guarded_dataclass",
        "dataclass_first",
        "static_guard",
    } or (strategy == "version_guard" and sys.version_info < (3, 12))
    if guarded:
        assert extension(strategy, value)[0] == EXT_CONSTRUCTOR_KW_ARGS
    else:
        with pytest.raises(AttributeError):
            extension(strategy, value)


def test_current_production_matches_frozen_baseline_for_regular_tree() -> None:
    value = [Node("tree", [Leaf("one", Kind.A)]), SendDataclass("worker", 1)]
    baseline, _ = make_encoder("baseline")
    assert JsonPlusSerializer().dumps_typed(value) == baseline(value)


@pytest.mark.parametrize(
    "factory", [DescriptorDataclass, AttributeAccessDataclass, DynamicDataclass]
)
def test_production_preserves_attribute_access_and_bytes(factory) -> None:
    original, actual = factory(), factory()
    baseline, _ = make_encoder("baseline")
    expected = baseline(original)
    assert JsonPlusSerializer().dumps_typed(actual) == expected
    if hasattr(original, "reads"):
        assert actual.reads == original.reads


def test_production_property_exception_matches_baseline() -> None:
    baseline, _ = make_encoder("baseline")
    for encode in (baseline, JsonPlusSerializer().dumps_typed):
        with pytest.raises(TypeError):
            encode(RaisingProperty())


def test_protocol_rejects_blocked_methods() -> None:
    @dataclasses.dataclass(unsafe_hash=True)
    class BlockedRepr:
        node: str = "worker"
        arg: object = 1

        __repr__ = None

    assert not isinstance(BlockedRepr(), SendProtocol)
    for strategy in STRATEGIES:
        assert extension(strategy, BlockedRepr())[0] == EXT_CONSTRUCTOR_KW_ARGS


@pytest.mark.parametrize("strategy", STRATEGIES)
def test_unsupported_object_exception_matches_baseline(strategy: str) -> None:
    encode, namespace = make_encoder(strategy)
    with pytest.raises(TypeError, match="Object of type object is not serializable"):
        namespace["_msgpack_default"](object())
    with pytest.raises(TypeError, match="Type is not msgpack serializable"):
        encode(object())


def test_exact_registry_preserves_earlier_duck_typed_branch(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        UUID, "model_dump", lambda self: {"int": self.int}, raising=False
    )
    baseline, _ = make_encoder("baseline")
    registry, _ = make_encoder("exact_registry")
    value = UUID(int=1)
    assert extension("exact_registry", value)[0] == EXT_PYDANTIC_V2
    assert registry(value) == baseline(value)
