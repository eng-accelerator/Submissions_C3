class AppError(Exception):
    pass

class ConfigurationError(AppError):
    pass

class LLMInvocationError(AppError):
    pass

class AgentExecutionError(AppError):
    pass
