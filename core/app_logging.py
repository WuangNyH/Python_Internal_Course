import logging
from colorlog import ColoredFormatter
from core.trace import trace_id_ctx


class TraceIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = trace_id_ctx.get() or "n/a"
        return True


class ReqPhaseDefaultFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "req_phase"):
            record.req_phase = ""
        return True


class PhaseColoredFormatter(ColoredFormatter):
    def format(self, record: logging.LogRecord) -> str:
        # Format base trước (đã có log_color theo level)
        s = super().format(record)

        # Chỉ áp dụng cho access log
        if record.name != "access":
            return s

        phase = getattr(record, "req_phase", "")
        if phase == "start":
            # đổi màu phần message sang cyan
            return s.replace(record.getMessage(), f"\x1b[36m{record.getMessage()}\x1b[0m")
        if phase == "end":
            # đổi sang purple
            return s.replace(record.getMessage(), f"\x1b[35m{record.getMessage()}\x1b[0m")

        return s


def _build_formatter() -> PhaseColoredFormatter:
    return PhaseColoredFormatter(
        fmt=(
            "%(log_color)s %(asctime)s %(levelname)s "
            "[trace_id=%(trace_id)s] %(name)s: "
            "%(message)s"
        ),
        log_colors={
            "DEBUG": "white",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "bold_red",
        },
    )

# Gọi 1 lần khi app start để
# tạo formatter có %(trace_id)s
# và gắn TraceIdFilter vào root logger
def setup_logging(sql_echo: bool = False) -> None:
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    formatter = _build_formatter()
    trace_filter = TraceIdFilter()
    phase_filter = ReqPhaseDefaultFilter()

    # Nếu root đã có handler (thường do uvicorn cấu hình), gắn filter vào các handler đó
    if root.handlers:
        for h in root.handlers:
            h.setFormatter(formatter) # override formatter
            h.addFilter(trace_filter)
            h.addFilter(phase_filter)
    else:
        # Nếu chưa có handler nào, tự tạo handler console theo format tự cấu hình
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        handler.addFilter(trace_filter)
        handler.addFilter(phase_filter)
        root.addHandler(handler)

    # DEV ONLY: bật SQLAlchemy engine log qua hệ logging hiện tại
    sa_logger = logging.getLogger("sqlalchemy.engine")
    sa_logger.setLevel(logging.INFO if sql_echo else logging.WARNING)
    sa_logger.propagate = True
