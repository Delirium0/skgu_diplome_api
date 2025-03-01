import base64


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        if image_path.lower().endswith(".svg"):
            return f"data:image/svg+xml;base64,{encoded_string}"
        else:
            return f"data:image/png;base64,{encoded_string}"
