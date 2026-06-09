from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from langchain_core.tools import tool


class ShoppingDataStore:
    """Mock data store with fast in-memory indexes."""

    def __init__(self, json_path: Path) -> None:
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)

        self.metadata = data.get("metadata", {})
        self._customers = data.get("customers", [])
        self._orders = data.get("orders", [])
        self._vouchers = data.get("vouchers", [])

        self.customer_by_id: dict[str, Any] = {
            c["customer_id"]: c for c in self._customers
        }
        self.order_by_id: dict[str, Any] = {
            str(o["order_id"]): o for o in self._orders
        }

        self.orders_by_customer_id: dict[str, list] = {}
        for o in self._orders:
            cid = o.get("customer_id", "")
            self.orders_by_customer_id.setdefault(cid, []).append(o)

        self.vouchers_by_customer_id: dict[str, list] = {}
        for v in self._vouchers:
            cid = v.get("customer_id", "")
            self.vouchers_by_customer_id.setdefault(cid, []).append(v)

    def get_customer_by_id(self, customer_id: str) -> dict[str, Any]:
        c = self.customer_by_id.get(str(customer_id))
        if c is None:
            return {"status": "not_found", "customer_id": str(customer_id)}
        return {"status": "ok", "customer": c}

    def get_orders_by_customer_id(
        self, customer_id: str, limit: int = 10
    ) -> dict[str, Any]:
        cid = str(customer_id)
        if cid not in self.customer_by_id:
            return {"status": "not_found", "customer_id": cid}
        orders = self.orders_by_customer_id.get(cid, [])
        return {"status": "ok", "customer_id": cid, "orders": orders[:limit]}

    def get_order_detail_by_order_id(self, order_id: str) -> dict[str, Any]:
        oid = str(order_id)
        o = self.order_by_id.get(oid)
        if o is None:
            return {"status": "not_found", "order_id": oid}
        return {"status": "ok", "order": o}

    def get_vouchers_by_customer_id(
        self,
        customer_id: str,
        only_active: bool = False,
    ) -> dict[str, Any]:
        cid = str(customer_id)
        if cid not in self.customer_by_id:
            return {"status": "not_found", "customer_id": cid}
        vouchers = self.vouchers_by_customer_id.get(cid, [])
        if only_active:
            vouchers = [v for v in vouchers if v.get("status") == "active"]
        return {"status": "ok", "customer_id": cid, "vouchers": vouchers}


def build_data_tools(store: ShoppingDataStore) -> list:
    @tool
    def get_customer_by_id(customer_id: str) -> dict:
        """Look up customer profile by customer_id (e.g. 'C001').
        Returns tier, max_voucher_per_month, remaining_voucher_quota_this_month, loyalty_points, contact info."""
        return store.get_customer_by_id(customer_id)

    @tool
    def get_orders_by_customer_id(customer_id: str) -> dict:
        """Get the list of recent orders for a customer by customer_id (e.g. 'C001').
        Returns order ids, statuses, and basic info."""
        return store.get_orders_by_customer_id(customer_id)

    @tool
    def get_order_detail_by_order_id(order_id: str) -> dict:
        """Get full details of a single order by order_id (e.g. '1971').
        Includes order_status, estimated_delivery, delivered_at, can_return_now, eligible_for_return_until, items."""
        return store.get_order_detail_by_order_id(order_id)

    @tool
    def get_vouchers_by_customer_id(customer_id: str) -> dict:
        """Get all vouchers for a customer by customer_id (e.g. 'C001').
        Includes voucher_code, status (active/used/expired/locked), discount_value, end_at."""
        return store.get_vouchers_by_customer_id(customer_id)

    return [
        get_customer_by_id,
        get_orders_by_customer_id,
        get_order_detail_by_order_id,
        get_vouchers_by_customer_id,
    ]
