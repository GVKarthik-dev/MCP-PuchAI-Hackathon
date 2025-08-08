from fastmcp import FastMCP

mcp = FastMCP(name="MyServer")

@mcp.tool
def hello(name: str) -> str:
    return f"Hello, {name}!"


@mcp.tool
def add_nums(a:int, b: int)-> int:
    """Adding of two numbers

    Args:
        a (int): Any integer
        b (int): Any integer

    Returns:
        int: Sum of these integers
    """
    return a+b

