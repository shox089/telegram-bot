def calculate(expression: str) -> str:
    try:
        result = eval(expression)
        return str(result)
    except:
        return "❌ Xato ifoda!"
