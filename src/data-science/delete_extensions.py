import argparse
import vertexai
from vertexai.preview import extensions

# Default constants (can be overridden by CLI args)
DEFAULT_PROJECT_ID = "demos-vertex-ai"
DEFAULT_LOCATION = "us-central1"


def manage_vertex_extensions(project_id: str, location: str, mode: str, ids: list[str] = None):
    """
    Manages Vertex AI extensions based on the specified mode.

    Args:
        project_id: The Google Cloud project ID.
        location: The Google Cloud location.
        mode: Operation mode:
              'delete_all' (deletes all extensions),
              'keep_newest' (deletes all but the most recent extension by ID),
              'delete_list' (deletes extensions from a provided list of IDs).
        ids: A list of extension resource IDs to delete. Required for 'delete_list' mode.
    """
    try:
        vertexai.init(project=project_id, location=location)
        print(f"Initialized Vertex AI for project {project_id} in {location}.")
    except Exception as e:
        print(f"ERROR: Failed to initialize Vertex AI: {e}")
        return

    if mode == "delete_list":
        if not ids:
            # This should be caught by argparse, but defensive check.
            print("ERROR: --ids argument is required for 'delete_list' mode.")
            return

        print(f"Mode: Delete extensions from list: {ids}")
        extensions_to_delete_names = [
            f"projects/{project_id}/locations/{location}/extensions/{ext_id}" for ext_id in ids
        ]

        print(f"\nStarting deletion of {len(extensions_to_delete_names)} extension(s) from the provided list...")
        deleted_count = 0
        failed_count = 0
        for ext_name in extensions_to_delete_names:
            delete_id = ext_name.split('/')[-1]
            print(f"Attempting to delete extension: {ext_name} (ID: {delete_id})...")
            try:
                extension_instance_to_delete = extensions.Extension(extension_name=ext_name)
                extension_instance_to_delete.delete()
                print(f"Successfully deleted {ext_name}")
                deleted_count += 1
            except Exception as e:
                print(f"ERROR: Failed to delete {ext_name}: {e}")
                failed_count += 1

        print("\n--- Deletion Summary ---")
        print(f"Attempted to delete: {len(extensions_to_delete_names)} extension(s) from list.")
        print(f"Successfully deleted: {deleted_count} extension(s).")
        if failed_count > 0:
            print(f"Failed to delete: {failed_count} extension(s).")
        print("--- End of Summary ---")
        print("\nFinished processing extensions.")
        return

    print(f"Fetching extensions from project {project_id} in {location}...")
    try:
        extensions_list = extensions.Extension.list()
    except Exception as e:
        print(f"ERROR: Failed to list extensions: {e}")
        return

    if not extensions_list:
        print(f"No extensions found in project {project_id}, location {location}.")
        return

    print(f"\nFound {len(extensions_list)} extensions in project {project_id}, location {location}.")

    extension_to_keep = None
    extensions_to_delete = []

    if mode == "delete_all":
        print("Mode: Delete all extensions.")
        extensions_to_delete = list(extensions_list)
    elif mode == "keep_newest":
        print("Mode: Keep the newest extension (highest ID), delete others.")
        if len(extensions_list) <= 1:
            print("Only one or no extensions found. No extensions will be deleted under 'keep_newest' mode.")
            if extensions_list: # Means exactly one extension
                ext = extensions_list[0]
                ext_id = ext.name.split('/')[-1]
                print(
                    f"Keeping extension: {ext.name} (ID: {ext_id}, Display Name: {ext.display_name})")
            return

        try:
            # Sort extensions by ID descending (higher ID means newer)
            sorted_extensions = sorted(
                extensions_list,
                key=lambda ext: int(ext.name.split('/')[-1]),
                reverse=True
            )
        except (ValueError, IndexError, TypeError) as e:
            print(
                f"ERROR: Error parsing extension ID for sorting: {e}. Cannot determine the newest extension.")
            print("No extensions will be deleted.")
            return

        extension_to_keep = sorted_extensions[0]
        extensions_to_delete = sorted_extensions[1:]

        keep_id = extension_to_keep.name.split('/')[-1]
        print(
            f"Keeping the newest extension (by ID): {extension_to_keep.name} (ID: {keep_id}, Display Name: {extension_to_keep.display_name})")
    else:
        # This case should be caught by argparse choices, but defensive check.
        print(f"ERROR: Unknown mode '{mode}'. Supported modes are 'delete_all', 'keep_newest', and 'delete_list'.")
        return

    if not extensions_to_delete:
        print("No extensions are targeted for deletion based on the selected mode and current state.")
        if extension_to_keep:
             keep_id = extension_to_keep.name.split('/')[-1]
             display_name_kept = extension_to_keep.display_name
             print(f"The extension being kept is: {extension_to_keep.name} (ID: {keep_id}, Display Name: {display_name_kept})")
        print("\nFinished processing extensions.")
        return

    print(f"\nStarting deletion of {len(extensions_to_delete)} extension(s)...")
    deleted_count = 0
    failed_count = 0
    for ext_to_delete_obj in extensions_to_delete:
        delete_id = ext_to_delete_obj.name.split('/')[-1]
        display_name = ext_to_delete_obj.display_name
        print(
            f"Attempting to delete extension: {ext_to_delete_obj.name} (ID: {delete_id}, Display Name: {display_name})...")
        try:
            # Re-fetch the extension by its resource name to use the .delete() method,
            # consistent with official samples and original script.
            extension_instance_to_delete = extensions.Extension(
                extension_name=ext_to_delete_obj.name
            )
            extension_instance_to_delete.delete()
            print(f"Successfully deleted {ext_to_delete_obj.name}")
            deleted_count += 1
        except Exception as e:
            print(f"ERROR: Failed to delete {ext_to_delete_obj.name}: {e}")
            failed_count += 1

    print("\n--- Deletion Summary ---")
    if mode == "keep_newest":
        if extension_to_keep:
            keep_id = extension_to_keep.name.split('/')[-1]
            display_name_kept = extension_to_keep.display_name
            print(f"Kept extension: {extension_to_keep.name} (ID: {keep_id}, Display Name: {display_name_kept})")
        elif len(extensions_list) <= 1 and extensions_list: # Only one existed
            ext_info = extensions_list[0]
            ext_id_info = ext_info.name.split('/')[-1]
            print(f"Kept extension (only one found): {ext_info.name} (ID: {ext_id_info}, Display Name: {ext_info.display_name})")

    print(f"Attempted to delete: {len(extensions_to_delete)} extension(s).")
    print(f"Successfully deleted: {deleted_count} extension(s).")
    if failed_count > 0:
        print(f"Failed to delete: {failed_count} extension(s).")
    print("--- End of Summary ---")
    print("\nFinished processing extensions.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Manage Vertex AI Extensions. Deletes all extensions, all except the most recent one (by ID), or a specific list of extensions."
    )
    parser.add_argument(
        "--project_id",
        type=str,
        default=DEFAULT_PROJECT_ID,
        help=f"Google Cloud Project ID (default: {DEFAULT_PROJECT_ID})."
    )
    parser.add_argument(
        "--location",
        type=str,
        default=DEFAULT_LOCATION,
        help=f"Google Cloud Location (default: {DEFAULT_LOCATION})."
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["keep_newest", "delete_all", "delete_list"],
        required=True,
        help="Operation mode: 'keep_newest' (deletes all but the most recent by ID), 'delete_all' (deletes all extensions), or 'delete_list' (deletes extensions specified by --ids)."
    )
    parser.add_argument(
        "--ids",
        nargs='+',
        type=str,
        help="One or more extension resource IDs to delete. Required and only used when mode is 'delete_list'."
    )

    args = parser.parse_args()

    if args.mode == 'delete_list' and not args.ids:
        parser.error("--ids is required when mode is 'delete_list'")
    if args.mode != 'delete_list' and args.ids:
        parser.error("--ids is only used with mode 'delete_list'")


    manage_vertex_extensions(project_id=args.project_id, location=args.location, mode=args.mode, ids=args.ids)

# https://cloud.google.com/vertex-ai/generative-ai/docs/samples/generativeaionvertexai-delete-extension
