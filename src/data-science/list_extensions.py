import vertexai
from vertexai.preview import extensions

# TODO (developer):Update project_id
# PROJECT_ID = "your-project-id"
# vertexai.init(project="demos-vertex-ai", location="us-central1")
vertexai.init(location="us-central1")

extensions_list = extensions.Extension.list()
print(extensions_list)
# Example response:
# [<vertexai.extensions._extensions.Extension object at 0x76e8ced37af0>
# resource name: projects/[PROJECT_ID]/locations/us-central1/extensions/1234567890123456]
# https://cloud.google.com/vertex-ai/generative-ai/docs/samples/generativeaionvertexai-list-extensions
