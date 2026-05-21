"""Węzły drzewa AST dla translatora PascC."""

from dataclasses import dataclass, field
from typing import List, Optional, Any


@dataclass
class Node:
    line: int = field(default=0, compare=False, kw_only=True)


@dataclass
class Program(Node):
    name: str
    block: 'Block'


@dataclass
class Block(Node):
    var_section: Optional['VarSection']
    sub_decls: List[Any]
    compound: 'CompoundStatement'


@dataclass
class VarSection(Node):
    declarations: List['VarDecl']


@dataclass
class VarDecl(Node):
    names: List[str]
    type_name: str


@dataclass
class ProcedureDecl(Node):
    name: str
    params: List['ParamGroup']
    sub_block: 'Block'


@dataclass
class FunctionDecl(Node):
    name: str
    params: List['ParamGroup']
    return_type: str
    sub_block: 'Block'


@dataclass
class ParamGroup(Node):
    names: List[str]
    type_name: str
    by_ref: bool


@dataclass
class CompoundStatement(Node):
    statements: List[Any]


@dataclass
class Assignment(Node):
    target: str
    value: Any


@dataclass
class ProcedureCall(Node):
    name: str
    args: List[Any]


@dataclass
class IfStatement(Node):
    condition: Any
    then_branch: Any
    else_branch: Optional[Any]


@dataclass
class WhileStatement(Node):
    condition: Any
    body: Any


@dataclass
class ForStatement(Node):
    var: str
    start: Any
    end: Any
    direction: str
    body: Any


@dataclass
class RepeatStatement(Node):
    body: List[Any]
    condition: Any


@dataclass
class WriteStatement(Node):
    newline: bool
    args: List[Any]


@dataclass
class ReadStatement(Node):
    newline: bool
    vars: List[str]


@dataclass
class BinOp(Node):
    left: Any
    op: str
    right: Any


@dataclass
class UnaryOp(Node):
    op: str
    operand: Any


@dataclass
class IntConst(Node):
    value: int


@dataclass
class RealConst(Node):
    value: float


@dataclass
class CharConst(Node):
    value: str


@dataclass
class StringConst(Node):
    value: str


@dataclass
class BoolConst(Node):
    value: bool


@dataclass
class VarRef(Node):
    name: str


@dataclass
class FunctionCallExpr(Node):
    name: str
    args: List[Any]


@dataclass
class WriteArg(Node):
    expr: Any
    width: Optional[int] = None
    decimals: Optional[int] = None
