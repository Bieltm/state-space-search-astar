import dataclasses
import math
from pathlib import Path
import re
from fractions import Fraction
from functools import cache

from typing import Any

from hlogedu.search.problem import Problem
from hlogedu.search.common import ClassParameter


@dataclasses.dataclass
class Relation:
    name: str # The name of the table
    cardinality: int # How many rows are in the table
    pages: int # How many pages this Relation uses.
    # It might not be equal to cardinality/page_tuples (see JoinInput).

    @classmethod
    def parse(cls, line):
        m = re.match(r"(\S+)\s+(\d+)\s+(\d+)", line)
        name, cardinality, pages = m.groups()
        return cls(name, int(cardinality), int(pages))


@dataclasses.dataclass(frozen=True)
class JoinInput:
    # Config
    page_tuples: int # The number of tuples per I/O page
    read_cost: int # The cost of retrieving one page from disk
    write_cost: int # The cost of writing a page to the disk

    relations: dict[str, Relation] # tables in the DB, indexed by relation name

    # A predicate is indexed by pairs of relations (the relations joined)
    # and the value is the fraction of the cartesian product that
    # survives the join. For example, sel = 0.15 means the join
    # returns .15 * card(relation1) * card(relation2) rows
    # The pair of relations is sorted, as we assume a commutative
    # join operation.
    predicates: dict[tuple[str, str], float]

    @classmethod
    def parse(cls, text):
        cfg, rels, preds = {}, {}, {}
        section = None
        for raw in text.splitlines():
            # remove comments
            line = raw.split("#", 1)[0].strip()
            # skip empty lines
            if not line: continue
            # parse header
            if line.startswith("[") and line.endswith("]"):
                section = line[1:-1].upper(); continue
            # parse content
            if section == "CONFIG":
                key, value = re.match(r"(\S+)\s+(\d+)", line).groups()
                cfg[key] = int(value)
            elif section == "RELATIONS":
                r = Relation.parse(line)
                rels[r.name] = r
            elif section == "PREDICATES":
                k, v = cls.parse_predicate(line)
                preds[k] = v
            else:
                raise ValueError(f"Unknown section {section}")
        return cls(
            page_tuples=cfg.get("page_tuples", 100),
            read_cost=cfg.get("read_cost", 1),
            write_cost=cfg.get("write_cost", 1),
            relations=rels,
            predicates=preds
        )

    @classmethod
    def parse_predicate(cls, line):
        m = re.match(r"(\S+)\s+(\S+)\s+(\d+\.\d+)", line)
        r1, r2, selectivity = m.groups()
        r1, r2 = sorted((r1, r2)) # canonical representation
        return (r1, r2), float(selectivity)


class JoinOrderProblem(Problem):
    NAME = "JoinOrder"
    PARAMS = [
        ClassParameter(
            "file_",
            type=str,
            default=None,
            help="Query instance in the .q format.",
        )
    ]

    def __init__(self, file_: str):
        file_ = Path(file_)
        query = JoinInput.parse(file_.read_text())

        @cache
        def estimate_card(joined):
            if not joined:
                return 0

            mult = 1
            for name in joined:
                mult = mult * query.relations[name].cardinality

            for (r1, r2), selectivity in query.predicates.items():
                if r1 in joined and r2 in joined:
                    mult = mult * selectivity

            return mult
        self.estimate_card = estimate_card
        self.query = query

    def initials(self):
        states = []
        relations_list = sorted(self.query.relations)
        for i in relations_list:
            a = frozenset([i])
            states.append(a)
        return states

    def is_goal(self, s):
        total = set(self.query.relations)
        rest = total - s
        return not rest

    def actions(self, s):
        total = frozenset(self.query.relations)
        rest = sorted(total - s)
        return rest

    def result(self, s, a):
        return s | frozenset([a])

    def cost(self, s, a):
        if not s:
            return 0
        #cost(S,r) = pagines(S)*read_cost+pagines(SU{r})*write_cost
        next_s = self.result(s, a)
        if len(s) == 1:
            rel_name = next(iter(s))
            pages_read = self.query.relations[rel_name].pages
        else:
            pages_read = math.ceil(self.estimate_card(s) / self.query.page_tuples)

        pages_write = math.ceil(self.estimate_card(next_s) / self.query.page_tuples)

        return pages_read * self.query.read_cost + pages_write * self.query.write_cost