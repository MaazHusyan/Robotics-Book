---
id: "002"
title: "Explain Pydantic Config Error"
stage: "general"
date_iso: "2025-12-19"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "001-chatbot-agent-integration"
branch: "001-chatbot-agent-integration"
user: "maaz"
command: "general"
labels:
  - "configuration"
  - "pydantic"
  - "error"
  - "validation"
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml: |
  - /home/maaz/Desktop/Robotics-Book/backend/src/config.py
tests_yaml: |
  - /home/maaz/Desktop/Robotics-Book/backend/tests/integration/test_agent_endpoint.py
---

# Explain Pydantic Config Error

## User Prompt
```
i have got this error tell me what is the cause and do not make any changes in code
(venv) maaz@ThinkPad-T460:~/Desktop/Robotics-Book/backend$  uvicorn main:app --reload --port 8000
INFO:     Will watch for changes in these directories: ['/home/maaz/Desktop/Robotics-Book/backend']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [104113] using StatReload
Process SpawnProcess-1:
Traceback (most recent call last):
  File "/usr/lib/python3.13/multiprocessing/process.py", line 313, in _bootstrap
    self.run()
    ~~~~~~~~^^
  File "/usr/lib/python3.13/multiprocessing/process.py", line 108, in run
    self._target(*self._args, **self._kwargs)
    ~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/maaz/Desktop/Robotics-Book/backend/venv/lib/python3.13/site-packages/uvicorn/_subprocess.py", line 80, in subprocess_started
    target(sockets=sockets)
    ~~~~~~^^^^^^^^^^^^^^^^^
  File "/home/maaz/Desktop/Robotics-Book/backend/venv/lib/python3.13/site-packages/uvicorn/server.py", line 67, in run
    return asyncio_run(self.serve(sockets=sockets), loop_factory=self.config.get_loop_factory())
  File "/usr/lib/python3.13/asyncio/runners.py", line 195, in run
    return runner.run(main)
           ~~~~~~~~~~^^^^^^
  File "/usr/lib/python3.13/asyncio/runners.py", line 118, in run
    return self._loop.run_until_complete(task)
           ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "/usr/lib/python3.13/asyncio/base_events.py", line 719, in run_until_complete
    return future.result()
           ~~~~~~~~~~~~~^^
  File "/home/maaz/Desktop/Robotics-Book/backend/venv/lib/python3.13/site-packages/uvicorn/server.py", line 71, in serve
    await self._serve(sockets)
  File "/home/maaz/Desktop/Robotics-Book/backend/venv/lib/python3.13/site-packages/uvicorn/server.py", line 78, in _serve
    config.load()
    ~~~~~~~~~~~^^
  File "/home/maaz/Desktop/Robotics-Book/backend/venv/lib/python3.13/site-packages/uvicorn/config.py", line 439, in load
    self.loaded_app = import_from_string(self.app)
                      ~~~~~~~~~~~~~~~~~~^^^^^^^^^^
  File "/home/maaz/Desktop/Robotics-Book/backend/venv/lib/python3.13/site-packages/uvicorn/importer.py", line 19, in import_from_string
    module = importlib.import_module(module_str)
  File "/usr/lib/python3.13/importlib/__init__.py", line 88, in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "<frozen importlib._bootstrap>", line 1387, in _gcd_import
  File "<frozen importlib._bootstrap>", line 1360, in _find_and_load
  File "<frozen importlib._bootstrap>", line 1331, in _find_and_load_unlocked
  File "<frozen importlib._bootstrap>", line 935, in _load_unlocked
  File "<frozen importlib._bootstrap_external>", line 1026, in exec_module
  File "<frozen importlib._bootstrap>", line 488, in _call_with_frames_removed
  File "/home/maaz/Desktop/Robotics-Book/backend/main.py", line 11, in <module>
    from src.api.agent_endpoint import router as agent_router
  File "/home/maaz/Desktop/Robotics-Book/backend/src/api/agent_endpoint.py", line 14, in <module>
    from ..config import get_settings
  File "/home/maaz/Desktop/Robotics-Book/backend/src/config.py", line 46, in <module>
    settings = Settings()
  File "/home/maaz/Desktop/Robotics-Book/backend/venv/lib/python3.13/site-packages/pydantic_settings/main.py", line 194, in __init__
    super().__init__(
    ~~~~~~~~~~~~~~~~^
        **__pydantic_self__._settings_build_values(
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<27 lines>...
        )
        ^
    )
    ^
  File "/home/maaz/Desktop/Robotics-Book/backend/venv/lib/python3.13/site-packages/pydantic/main.py", line 250, in __init__
    validated_self = self.__pydantic_validator__.validate_python(data, self_instance=self)
pydantic_core._pydantic_core.ValidationError: 5 validation errors for Settings
GEMINI_API_KEY
  Extra inputs are not permitted [type=extra_forbidden, input_value='AIzaSyCxmJ7A_jl_hL6LCPri0pKc-Y0s-0rZ9oE', input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/extra_forbidden
OPENAI_API_KEY
  Extra inputs are not permitted [type=extra_forbidden, input_value='sk-proj-JXwen_qYQlD9h9bR...rEXbtpuezHlio3li0b0dqIA', input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/extra_forbidden
OPENROUTER_KEY
  Extra inputs are not permitted [type=extra_forbidden, input_value='sk-or-v1-f7fada9ed438abf...874e7561d4ab192b80fd92e', input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/extra_forbidden
BASE_URL
  Extra inputs are not permitted [type=extra_forbidden, input_value='https://openrouter.ai/api/v1', input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/extra_forbidden
MODEL
  Extra inputs are not permitted [type=extra_forbidden, input_value='gemini/gemini-2.5-flash', input_type=str]
    For further information visit https://errors.pydantic.dev/2.12/v/extra_forbidden
```

## Assistant Response
Explained the Pydantic validation error in the configuration. The error occurs because the Settings class in src/config.py has extra='forbid' set, which prevents it from accepting environment variables that are not explicitly defined in the model. The environment currently has GEMINI_API_KEY, OPENAI_API_KEY, OPENROUTER_KEY, BASE_URL, and MODEL set, but these fields are not defined in the Settings model, causing the validation to fail.

## Outcome
Successfully diagnosed the Pydantic validation error and explained the root cause to the user.

## Evaluation
Provided clear explanation of the configuration error without making any code changes as requested.