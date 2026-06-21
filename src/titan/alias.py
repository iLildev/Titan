from __future__ import annotations

from titan.errors import TitanError
from titan.ctx import Context


class AliasMap:
    """
    طبقة التسمية الاختيارية في Titan.

    تسمح للمطور بتعريف أسماء بديلة لـ methods موجودة في Context.
    لا تغير أي سلوك — mapping فقط من اسم إلى اسم.

    القواعد:
    - الأسماء الأصلية في ctx تبقى ثابتة بدون أي تغيير
    - الاسم الهدف يجب أن يكون موجوداً في Context وإلا TitanError
    - لا magic، لا wrapping، لا interception
    """

    def __init__(self) -> None:
        self._map: dict[str, str] = {}

    def register(self, alias: str, target: str) -> None:
        if not hasattr(Context, target):
            raise TitanError(
                f"Cannot create alias '{alias}': '{target}' does not exist in Context."
            )
        self._map[alias] = target

    def apply(self, ctx: Context) -> None:
        for alias, target in self._map.items():
            setattr(ctx, alias, getattr(ctx, target))
