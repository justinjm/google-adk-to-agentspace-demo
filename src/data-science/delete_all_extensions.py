import vertexai
from vertexai.preview import extensions

# TODO (developer): Update project_id if not using the default.
PROJECT_ID = "demos-vertex-ai"  # Default project ID
LOCATION = "us-central1"      # Default location


def delete_all_except_oldest_extension():
    """Lists all extensions, then deletes all but the oldest created one."""
    try:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        print(f"Initialized Vertex AI for project {PROJECT_ID} in {LOCATION}.")
    except Exception as e:
        print(f"ERROR: Failed to initialize Vertex AI: {e}")
        return

    print(f"Fetching extensions from project {PROJECT_ID} in {LOCATION}...")
    try:
        extensions_list = extensions.Extension.list()
    except Exception as e:
        print(f"ERROR: Failed to list extensions: {e}")
        return

    if not extensions_list:
        print("No extensions found.")
        return

    if len(extensions_list) <= 1:
        print("Only one or no extensions found. No extensions will be deleted.")
        if extensions_list:
            ext = extensions_list[0]
            ext_id = ext.name.split('/')[-1]
            print(
                f"Keeping extension: {ext.name} (ID: {ext_id}, Display Name: {ext.display_name})")
        return

    # Sort extensions by their ID (assuming lower ID means older).
    # The extension ID is the last part of its resource name.
    try:
        sorted_extensions = sorted(
            extensions_list,
            # Sort by ID ascending
            key=lambda ext: int(ext.name.split('/')[-1])
        )
    except (ValueError, IndexError, TypeError) as e:
        print(
            f"ERROR: Error parsing extension ID for sorting: {e}. Cannot determine the oldest extension.")
        print("No extensions will be deleted.")
        return

    # Keep the first one (oldest by ID)
    extension_to_keep = sorted_extensions[0]
    extensions_to_delete = sorted_extensions[1:]  # Delete all others

    keep_id = extension_to_keep.name.split('/')[-1]
    print(f"\nFound {len(extensions_list)} extensions.")
    print(
        f"Keeping the oldest extension (by ID): {extension_to_keep.name} (ID: {keep_id}, Display Name: {extension_to_keep.display_name})")

    print("\nStarting deletion of newer extensions...")
    for ext_to_delete_obj in extensions_to_delete:
        delete_id = ext_to_delete_obj.name.split('/')[-1]
        print(
            f"Attempting to delete extension: {ext_to_delete_obj.name} (ID: {delete_id}, Display Name: {ext_to_delete_obj.display_name})...")
        try:
            # Re-fetch the extension by its ID to use the .delete() method as per official docs
            extension_instance_to_delete = extensions.Extension(
                extension_name=ext_to_delete_obj.name)
            extension_instance_to_delete.delete()
            print(f"Successfully deleted {ext_to_delete_obj.name}")
        except Exception as e:
            print(f"ERROR: Failed to delete {ext_to_delete_obj.name}: {e}")

    print("\nFinished processing extensions.")


if __name__ == "__main__":
    delete_all_except_oldest_extension()

# https://cloud.google.com/vertex-ai/generative-ai/docs/samples/generativeaionvertexai-delete-extension
