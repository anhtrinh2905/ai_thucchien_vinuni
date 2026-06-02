from __future__ import annotations

import json
from pathlib import Path

from langchain.agents import create_agent
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool

from core.llm import build_chat_model, normalize_content
from core.schemas import (
    AgentResult,
    CalculateTotalsInput,
    DiscountInput,
    ListProductsInput,
    ProductDetailInput,
    SaveOrderInput,
    ToolCallRecord,
)
from utils.data_store import OrderDataStore

ROOT_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = ROOT_DIR / "data"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "artifacts" / "orders"


def build_system_prompt(today: str | None = None) -> str:
    current_day = today or "2026-06-01"
    return f"""
Bạn là trợ lý đặt hàng điện tử OrderDesk.
Hôm nay là {current_day}.

Mục tiêu: xử lý yêu cầu đặt hàng bằng tiếng Việt hoặc hỗn hợp Anh-Việt, luôn bám sát catalog và chính sách.

QUY TẮC BẮT BUỘC
1. Trả lời cuối cùng ngắn gọn bằng tiếng Việt.
2. Không bịa product_id, giá, tồn kho, khuyến mãi, tổng tiền, order_id hay đường dẫn file. Chỉ dùng dữ liệu từ tool.
3. Trước khi gọi bất kỳ tool nào, phải có đủ:
   - tên khách hàng
   - số điện thoại
   - email
   - địa chỉ giao hàng
   - ít nhất một sản phẩm kèm số lượng
   Nếu thiếu, hỏi rõ phần còn thiếu (dùng cụm như "cần thêm" / "vui lòng cung cấp") và DỪNG — không gọi tool.
4. Từ chối ngay (không gọi tool) nếu người dùng yêu cầu:
   - bỏ qua tồn kho / policy
   - tự ép giảm giá thủ công (ví dụ 90%)
   - tạo hóa đơn giả / fake invoice
   - bỏ qua catalog hoặc bỏ qua quy trình chuẩn
   Trả lời rõ ràng: không thể thực hiện; chỉ áp dụng khuyến mãi từ tool get_discount.
5. Với đơn hàng hợp lệ, luôn gọi tool theo đúng thứ tự:
   a) list_products — tìm sản phẩm theo tên/thương hiệu người dùng nêu
   b) get_product_details — lấy giá, tồn kho, detail_token cho các product_id đã chọn
   c) get_discount — seed_hint ưu tiên email khách; customer_tier = vip nếu người dùng nói VIP
   d) calculate_order_totals — truyền items (danh sách), detail_token, discount_rate từ các bước trước
   e) save_order — chỉ gọi khi calculate_order_totals trả status=ok; truyền CÙNG items, detail_token, discount_rate, campaign_code như bước d)
6. detail_token chỉ hợp lệ khi items trong calculate_order_totals / save_order khớp CHÍNH XÁC với product_ids đã gọi ở get_product_details.
   - Ví dụ: get_product_details(["LT-004","MN-001","KB-002","DK-001"]) → detail_token X
   - save_order phải có items cùng bộ ID đó
   - Không bao giờ gọi save_order thiếu items hoặc thiếu campaign_code
7. Nếu get_product_details hoặc calculate_order_totals báo lỗi tồn kho / sản phẩm không hợp lệ:
   - giải thích ngắn gọn
   - không gọi save_order
8. Khi lưu thành công, xác nhận dựa trên output save_order:
   - order_id
   - mã khuyến mãi / discount_rate
   - final_total
   - save_path

GỢI Ý THAO TÁC
- list_products: truyền query là tên sản phẩm/thương hiệu; gọi riêng cho từng sản phẩm nếu cần.
- get_product_details: truyền danh sách product_id chính xác từ list_products.
- get_discount: seed_hint = email khách (hoặc số điện thoại nếu không có email).
- calculate_order_totals / save_order: dùng đúng detail_token, discount_rate, campaign_code từ tool trước đó.
- save_order bắt buộc có đủ: customer_*, items (danh sách), detail_token, discount_rate, campaign_code.
- items phải lấy product_id từ get_product_details, quantity từ yêu cầu khách.
""".strip()


def build_tools(store: OrderDataStore):
    @tool(args_schema=ListProductsInput)
    def list_products(
        query: str | None = None,
        category: str | None = None,
        max_unit_price: int | None = None,
        required_tags: list[str] | None = None,
        in_stock_only: bool = True,
        limit: int = 8,
    ) -> str:
        """Search the local product catalog and return matching items with product_id for later steps."""
        payload = store.list_products(
            query=query,
            category=category,
            max_unit_price=max_unit_price,
            required_tags=required_tags or [],
            in_stock_only=in_stock_only,
            limit=limit,
        )
        return json.dumps(payload, ensure_ascii=False)

    @tool(args_schema=ProductDetailInput)
    def get_product_details(product_ids: list[str]) -> str:
        """Return exact price, stock, and a detail_token required by pricing and save tools."""
        return json.dumps(store.get_product_details(product_ids), ensure_ascii=False)

    @tool(args_schema=DiscountInput)
    def get_discount(seed_hint: str, customer_tier: str = "standard") -> str:
        """Return the simulated campaign discount (rate 0.1 or 0.2) and campaign_code."""
        return json.dumps(store.get_discount(seed_hint=seed_hint, customer_tier=customer_tier), ensure_ascii=False)

    @tool(args_schema=CalculateTotalsInput)
    def calculate_order_totals(items, detail_token: str, discount_rate: float) -> str:
        """Validate stock with detail_token and compute subtotal, discount, and final total. items must be a list of {product_id, quantity} matching get_product_details."""
        payload = store.calculate_order_totals(items=items, detail_token=detail_token, discount_rate=discount_rate)
        return json.dumps(payload, ensure_ascii=False)

    @tool(args_schema=SaveOrderInput)
    def save_order(
        customer_name: str,
        customer_phone: str,
        customer_email: str,
        shipping_address: str,
        items,
        detail_token: str,
        discount_rate: float,
        campaign_code: str,
        customer_tier: str = "standard",
        notes: str = "",
    ) -> str:
        """Persist the validated order. Required: all customer fields, items list, detail_token, discount_rate, campaign_code from prior tool outputs."""
        result = store.save_order(
            customer_name=customer_name,
            customer_phone=customer_phone,
            customer_email=customer_email,
            shipping_address=shipping_address,
            items=items,
            detail_token=detail_token,
            discount_rate=discount_rate,
            campaign_code=campaign_code,
            customer_tier=customer_tier,
            notes=notes,
        )
        return json.dumps(result, ensure_ascii=False)

    return [list_products, get_product_details, get_discount, calculate_order_totals, save_order]


def build_agent(
    data_dir: Path | None = None,
    output_dir: Path | None = None,
    *,
    provider: str = "google",
    model_name: str | None = None,
    today: str | None = None,
):
    store = OrderDataStore(data_dir or DEFAULT_DATA_DIR, output_dir or DEFAULT_OUTPUT_DIR, today=today)
    model = build_chat_model(provider=provider, model_name=model_name, temperature=0.0)
    return create_agent(
        model=model,
        tools=build_tools(store),
        system_prompt=build_system_prompt(today or store.today),
    )


def run_agent(
    query: str,
    *,
    provider: str = "google",
    model_name: str | None = None,
    data_dir: Path | None = None,
    output_dir: Path | None = None,
    today: str | None = None,
) -> AgentResult:
    agent = build_agent(
        data_dir=data_dir,
        output_dir=output_dir,
        provider=provider,
        model_name=model_name,
        today=today,
    )
    response = agent.invoke({"messages": [{"role": "user", "content": query}]})
    messages = response["messages"] if isinstance(response, dict) else response
    tool_calls = extract_tool_calls(messages)
    saved_order, saved_order_path = extract_saved_order(tool_calls)
    return AgentResult(
        query=query,
        final_answer=extract_final_answer(messages),
        tool_calls=tool_calls,
        provider=provider,
        model_name=model_name,
        saved_order=saved_order,
        saved_order_path=saved_order_path,
    )


def extract_final_answer(messages) -> str:
    for message in reversed(messages):
        if isinstance(message, AIMessage):
            text = normalize_content(message.content)
            if text:
                return text
    return ""


def extract_tool_calls(messages) -> list[ToolCallRecord]:
    pending: dict[str, dict] = {}
    records: list[ToolCallRecord] = []

    for message in messages:
        if isinstance(message, AIMessage):
            for tool_call in getattr(message, "tool_calls", []) or []:
                pending[tool_call["id"]] = {
                    "name": tool_call["name"],
                    "args": tool_call.get("args", {}) or {},
                }
        elif isinstance(message, ToolMessage):
            metadata = pending.pop(message.tool_call_id, {})
            records.append(
                ToolCallRecord(
                    name=str(getattr(message, "name", None) or metadata.get("name", "")),
                    args=metadata.get("args", {}),
                    output=normalize_content(message.content),
                )
            )

    for metadata in pending.values():
        records.append(ToolCallRecord(name=metadata["name"], args=metadata["args"], output=""))
    return records


def extract_saved_order(tool_calls: list[ToolCallRecord]) -> tuple[dict | None, str | None]:
    for record in reversed(tool_calls):
        if record.name != "save_order" or not record.output:
            continue
        try:
            payload = json.loads(record.output)
        except json.JSONDecodeError:
            continue
        if payload.get("status") != "saved":
            return None, None
        return payload.get("saved_order"), payload.get("path")
    return None, None
