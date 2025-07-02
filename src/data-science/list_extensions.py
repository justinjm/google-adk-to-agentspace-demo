import vertexai
from vertexai.preview import extensions


vertexai.init(location="us-central1")

extensions_list = extensions.Extension.list() 
if not extensions_list:
    print("No extensions found.")
else:
    print("Found extensions:")
    for ext in extensions_list:
        print(f"  Display Name: {ext.display_name}")
        print(f"  Resource Name: {ext.name}")
        print(f"  Create Time: {ext.create_time}")
        print("-" * 20)

# Example response:
# [<vertexai.extensions._extensions.Extension object at 0x76e8ced37af0>
# resource name: projects/[PROJECT_ID]/locations/us-central1/extensions/1234567890123456]
# https://cloud.google.com/vertex-ai/generative-ai/docs/samples/generativeaionvertexai-list-extensions
