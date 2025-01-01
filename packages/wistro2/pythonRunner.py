import sys
import json
import importlib.util
import os
from typing import Any, Callable

def parse_args(arg: str) -> Any:
    try:
        return json.loads(arg)
    except json.JSONDecodeError:
        return arg

async def emit(data: Any) -> None:
    print('emitter', data)

async def run_python_module(file_path: str, args: Any) -> None:
    try:
        # Construct path relative to flows directory
        flows_dir = os.path.join(os.getcwd(), 'flows')
        module_path = os.path.join(flows_dir, file_path)

        # Load the module dynamically
        spec = importlib.util.spec_from_file_location("dynamic_module", module_path)
        if spec is None or spec.loader is None:
            raise ImportError(f"Could not load module from {module_path}")
            
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check if the executor function exists
        if not hasattr(module, 'executor'):
            raise AttributeError(f"Function 'executor' not found in module {module_path}")

        # Call the executor function with arguments
        result = await module.executor(args, emit)

        # Log the result if any
        if result is not None:
            print('Result:', result)

    except Exception as error:
        print('Error running Python module:', str(error), file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python pythonRunner.py <file-path> <arg>', file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    arg = sys.argv[2] if len(sys.argv) > 2 else None

    import asyncio
    asyncio.run(run_python_module(file_path, parse_args(arg)))