import aiolimiter

external_api_limiter = aiolimiter.AsyncLimiter(1, 1)
