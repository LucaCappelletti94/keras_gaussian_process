from typing import Dict, Tuple, List
from skopt.space import Categorical, Real, Integer
from deflate_dict import inflate, deflate
from collections import OrderedDict
import numpy as np
from scipy.optimize import OptimizeResult


class Space(OrderedDict):
    def __init__(self, space: Dict, sep="____"):
        super().__init__(space)
        self._sep = sep
        self._space = self._fixed = self._names = None

    def _parse_categorical(self, value: Tuple, name: str):
        if len(self._to_tuple(value)) > 1:
            self._space.append(Categorical(self._to_tuple(value), name=name))
            self._names.append(name)
        else:
            self._fixed[name] = value

    def _parse_real(self, low: float, high: float, name: str):
        self._space.append(Real(low=low, high=high, name=name))
        self._names.append(name)

    def _parse_integer(self, low: int, high: int, name: str):
        self._space.append(Integer(low=low, high=high, name=name))
        self._names.append(name)

    @classmethod
    def _is_categorical(cls, value) -> bool:
        return not (isinstance(value, list) and len(value) == 2 and all([
            isinstance(v, (float, int)) for v in value
        ]))

    @classmethod
    def _is_real(cls, values) -> bool:
        return all([isinstance(v, float) for v in values])

    @classmethod
    def _to_tuple(cls, value) -> bool:
        if isinstance(value, tuple):
            return value
        if isinstance(value, list):
            return tuple(value)
        return (value, )

    def _parse(self, name: str, value):
        if self._is_categorical(value):
            self._parse_categorical(value, name=name)
        elif self._is_real(value):
            self._parse_real(*value, name=name)
        else:
            self._parse_integer(*value, name=name)

    def rasterize(self):
        self._names = []
        self._fixed = {}
        self._space = []
        for name, value in deflate(self, sep=self._sep, leave_tuples=True).items():
            self._parse(name, value)

    @property
    def space(self) -> List:
        return self._space

    def inflate(self, deflated_space: Dict) -> Dict:
        return inflate({**deflated_space, **self._fixed}, sep=self._sep, leave_tuples=True)

    def inflate_results(self, results: OptimizeResult) -> Dict:
        return self.inflate(dict(zip(self._names, results.x)))
