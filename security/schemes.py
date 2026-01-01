from fastapi.security import HTTPBearer

# auto_error=False để không can thiệp flow hiện tại (guards vẫn là nơi quyết định 401/403)
bearer_scheme = HTTPBearer(auto_error=False)
